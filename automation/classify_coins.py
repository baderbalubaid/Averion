import psycopg2
import requests
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
CMC_API_KEY = os.getenv('CMC_API_KEY', '')

CATEGORIES = {
    'mega':  100_000_000_000,
    'large': 10_000_000_000,
    'mid':   1_000_000_000,
    'small': 100_000_000,
    'micro': 0
}

def get_category(market_cap):
    if market_cap >= CATEGORIES['mega']:
        return 'mega'
    elif market_cap >= CATEGORIES['large']:
        return 'large'
    elif market_cap >= CATEGORIES['mid']:
        return 'mid'
    elif market_cap >= CATEGORIES['small']:
        return 'small'
    else:
        return 'micro'

def apply_cap_protection(real_cap, previous_cap):
    if previous_cap is None:
        return real_cap
    if real_cap < previous_cap:
        return real_cap
    return min(real_cap, previous_cap * 1.10)

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telegram as tg

def send_telegram(msg):
    tg.send_admin(msg)

def fetch_coingecko():
    print('Fetching CoinGecko...')
    all_coins = {}
    page = 1
    while True:
        try:
            url = 'https://api.coingecko.com/api/v3/coins/markets'
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 250,
                'page': page,
                'sparkline': False
            }
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 429:
                print('CoinGecko rate limit · waiting 60s')
                time.sleep(60)
                continue
            if r.status_code != 200:
                print(f'CoinGecko error: {r.status_code}')
                break
            coins = r.json()
            if not coins:
                break
            for coin in coins:
                symbol = coin.get('symbol', '').upper()
                cap = coin.get('market_cap') or 0
                if cap > 0:
                    all_coins[symbol] = cap
            print(f'CoinGecko page {page}: {len(coins)} coins')
            page += 1
            time.sleep(1.5)
        except Exception as e:
            print(f'CoinGecko fetch error: {e}')
            break
    print(f'CoinGecko total: {len(all_coins)} coins')
    return all_coins

def fetch_coinmarketcap():
    if not CMC_API_KEY:
        print('CMC API key not set · skipping')
        return {}
    print('Fetching CoinMarketCap...')
    all_coins = {}
    start = 1
    limit = 5000
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        params = {
            'start': start,
            'limit': limit,
            'convert': 'USD'
        }
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            for coin in data.get('data', []):
                symbol = coin.get('symbol', '').upper()
                cap = coin.get('quote', {}).get('USD', {}).get('market_cap') or 0
                if cap > 0:
                    all_coins[symbol] = cap
            print(f'CMC total: {len(all_coins)} coins')
        else:
            print(f'CMC error: {r.status_code}')
    except Exception as e:
        print(f'CMC fetch error: {e}')
    return all_coins

def get_previous_data(cur, coin_id):
    cur.execute("""
        SELECT recorded_cap, category FROM coin_history
        WHERE coin = %s ORDER BY recorded_at DESC LIMIT 1
    """, (coin_id,))
    row = cur.fetchone()
    if row:
        return float(row[0]), row[1]
    return None, None

def classify_and_store(conn, cg_caps, cmc_caps):
    cur = conn.cursor()
    now = datetime.utcnow()
    reclassified = []
    total = 0

    all_coins = set(list(cg_caps.keys()) + list(cmc_caps.keys()))

    for coin_id in all_coins:
        cg_cap = cg_caps.get(coin_id)
        cmc_cap = cmc_caps.get(coin_id)

        # Average both sources
        if cg_cap and cmc_cap:
            real_cap = (cg_cap + cmc_cap) / 2
            source = 'both'
        elif cg_cap:
            real_cap = cg_cap
            source = 'coingecko'
        elif cmc_cap:
            real_cap = cmc_cap
            source = 'cmc'
        else:
            continue

        previous_cap, previous_category = get_previous_data(cur, coin_id)
        recorded_cap = apply_cap_protection(real_cap, previous_cap)
        new_category = get_category(recorded_cap)

        cur.execute("""
            INSERT INTO coin_history
            (coin, real_cap, recorded_cap, category, recorded_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (coin_id, real_cap, recorded_cap, new_category, now))

        if previous_category and previous_category != new_category:
            reclassified.append({
                'coin': coin_id,
                'from': previous_category,
                'to': new_category
            })
        total += 1

    conn.commit()

    if reclassified:
        msg = f'⚠️ Reclassification — {now.date()}\n\n'
        for r in reclassified:
            msg += f'{r["coin"]}: {r["from"]} → {r["to"]}\n'
        send_telegram(msg)
        print(msg)

    return total, len(reclassified)

def main():
    print(f'=== Classification started: {datetime.utcnow()} ===')
    conn = psycopg2.connect(**DB_CONFIG)

    # Fetch from both sources
    cg_caps = fetch_coingecko()
    cmc_caps = fetch_coinmarketcap()

    # Fallback if both fail
    if not cg_caps and not cmc_caps:
        print('❌ Both sources failed · using last recorded caps')
        send_telegram('⚠️ Classification failed — CoinGecko + CMC both unavailable · using last recorded caps')
        conn.close()
        return

    # Classify
    total, reclassified = classify_and_store(conn, cg_caps, cmc_caps)
    conn.close()

    # Summary
    cg_status = f'✅ {len(cg_caps)} coins' if cg_caps else '❌ Failed'
    cmc_status = f'✅ {len(cmc_caps)} coins' if cmc_caps else '❌ Failed'

    summary = f"""✅ Classification complete — {datetime.utcnow().date()}
CoinGecko: {cg_status}
CoinMarketCap: {cmc_status}
Total classified: {total} coins
Reclassified: {reclassified} coins"""

    print(summary)
    send_telegram(summary)

if __name__ == '__main__':
    main()

# Write daily market regime
from datetime import date, datetime
import database as db

def determine_and_write_regime():
    try:
        # Get BTC price changes
        btc_7d = db.get_btc_7d_change()
        btc_24h = db.get_btc_24h_change()
        volatility = db.get_market_volatility()

        # Determine regime
        if btc_7d > 5 and volatility < 60:
            regime = 'bull'
        elif btc_7d < -5 or volatility > 80:
            regime = 'bear'
        else:
            regime = 'sideways'

        db.write_market_regime(
            date.today(), regime,
            btc_24h, btc_7d, volatility
        )
        print(f'✅ Market regime: {regime} · BTC 7d: {btc_7d:.1f}% · Vol: {volatility:.1f}%')
    except Exception as e:
        print(f'❌ Regime write failed: {e}')

determine_and_write_regime()
