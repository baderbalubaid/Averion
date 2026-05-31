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

# Category boundaries (market cap in USD)
CATEGORIES = {
    'mega':  100_000_000_000,  # > $100B
    'large': 10_000_000_000,   # $10B - $100B
    'mid':   1_000_000_000,    # $1B - $10B
    'small': 100_000_000,      # $100M - $1B
    'micro': 0                 # < $100M
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
    # Max +10% upward per day
    max_upward = previous_cap * 1.10
    # Full drop immediately
    if real_cap < previous_cap:
        return real_cap
    # Cap upward movement
    return min(real_cap, max_upward)

def send_telegram(msg):
    try:
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': ADMIN_CHAT, 'text': msg}
        )
    except:
        pass

def fetch_coingecko_page(page):
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': page,
        'sparkline': False
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print('Rate limited — waiting 60 seconds')
            time.sleep(60)
            return fetch_coingecko_page(page)
        else:
            print(f'CoinGecko error: {response.status_code}')
            return []
    except Exception as e:
        print(f'CoinGecko fetch error: {e}')
        return []

def fetch_all_coins():
    all_coins = []
    page = 1
    while True:
        print(f'Fetching CoinGecko page {page}...')
        coins = fetch_coingecko_page(page)
        if not coins:
            break
        all_coins.extend(coins)
        page += 1
        time.sleep(1.5)
    print(f'Total coins fetched: {len(all_coins)}')
    return all_coins

def get_previous_cap(cur, coin_id):
    cur.execute("""
        SELECT recorded_cap FROM coin_history
        WHERE coin = %s
        ORDER BY recorded_at DESC
        LIMIT 1
    """, (coin_id,))
    row = cur.fetchone()
    return float(row[0]) if row else None

def get_previous_category(cur, coin_id):
    cur.execute("""
        SELECT category FROM coin_history
        WHERE coin = %s
        ORDER BY recorded_at DESC
        LIMIT 1
    """, (coin_id,))
    row = cur.fetchone()
    return row[0] if row else None

def classify_and_store(conn, coins):
    cur = conn.cursor()
    reclassified = []
    now = datetime.utcnow()

    for coin in coins:
        coin_id = coin.get('symbol', '').upper()
        real_cap = coin.get('market_cap') or 0
        volume_24h = coin.get('total_volume') or 0

        if real_cap <= 0:
            continue

        previous_cap = get_previous_cap(cur, coin_id)
        previous_category = get_previous_category(cur, coin_id)

        recorded_cap = apply_cap_protection(real_cap, previous_cap)
        new_category = get_category(recorded_cap)

        # Calculate confidence days
        cur.execute("""
            SELECT COUNT(DISTINCT DATE(recorded_at))
            FROM coin_history WHERE coin = %s
        """, (coin_id,))
        confidence_days = cur.fetchone()[0] or 0

        # Store in coin_history
        cur.execute("""
            INSERT INTO coin_history
            (coin, real_cap, recorded_cap, category, volume_24h, confidence_days, recorded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (coin_id, real_cap, recorded_cap, new_category, volume_24h, confidence_days, now))

        # Check reclassification
        if previous_category and previous_category != new_category:
            reclassified.append({
                'coin': coin_id,
                'from': previous_category,
                'to': new_category
            })

    conn.commit()

    # Alert reclassified coins
    if reclassified:
        msg = f'⚠️ Reclassification Alert — {now.date()}\n\n'
        for r in reclassified:
            msg += f'{r["coin"]}: {r["from"]} → {r["to"]}\n'
        send_telegram(msg)
        print(msg)

    return len(coins), len(reclassified)

def fallback_from_last_recorded(conn):
    print('⚠️ CoinGecko unavailable — using last recorded caps')
    send_telegram('⚠️ CoinGecko failed — classification skipped today · using last recorded caps')

def main():
    print(f'🔄 Classification started: {datetime.utcnow()}')
    conn = psycopg2.connect(**DB_CONFIG)

    coins = fetch_all_coins()

    if not coins:
        fallback_from_last_recorded(conn)
        conn.close()
        return

    total, reclassified = classify_and_store(conn, coins)
    conn.close()

    print(f'✅ Classification complete: {total} coins · {reclassified} reclassified')
    send_telegram(f'✅ Classification complete: {total} coins · {reclassified} reclassified')

if __name__ == '__main__':
    main()
