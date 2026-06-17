"""
classify_coins.py — Coin Market Cap Classification
Categories: mega (>$100B) · large ($10B-$100B) · mid ($1B-$10B) · small ($100M-$1B) · micro (<$100M)
Runs daily · uses MEXC tickers + circulating supply estimates
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
import requests
import redis
import json
from datetime import datetime

db.init_pool()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def classify_by_cap(cap_usd):
    if cap_usd >= 100_000_000_000:  return 'mega'
    elif cap_usd >= 10_000_000_000: return 'large'
    elif cap_usd >= 1_000_000_000:  return 'mid'
    elif cap_usd >= 100_000_000:    return 'small'
    else:                           return 'micro'

def run():
    print(f'🔍 Fetching coin classifications...')

    # Get all coins from Redis prices
    keys = r.keys('price:MEXC*:*/USDT')
    coins = [k.split(':')[-1].replace('/USDT','') for k in keys]
    print(f'Found {len(coins)} coins in Redis')

    # Try CoinGecko for market caps (free tier)
    classified = {}
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 250,
            'page': 1,
            'sparkline': False
        }
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for coin_data in data:
                symbol = coin_data.get('symbol', '').upper()
                cap = coin_data.get('market_cap') or 0
                vol = coin_data.get('total_volume') or 0
                if cap > 0:
                    classified[symbol] = {
                        'cap': cap,
                        'vol': vol,
                        'category': classify_by_cap(cap),
                        'source': 'coingecko'
                    }
            print(f'✅ CoinGecko: {len(classified)} coins classified')
    except Exception as e:
        print(f'⚠️ CoinGecko failed: {e}')

    # For remaining coins use volume-based estimate
    # High volume = likely larger cap
    inserted = 0
    with db.get_db() as conn:
        cur = conn.cursor()
        for coin in coins:
            if coin in classified:
                info = classified[coin]
                category = info['category']
                cap = info['cap']
                vol = info['vol']
                source = info['source']
            else:
                # Estimate from price × volume proxy
                price_key = f'price:MEXC Paper:{coin}/USDT'
                price = float(r.get(price_key) or 0)
                # Use volume from OHLCV if available
                category = 'micro'  # default
                cap = 0
                vol = 0
                source = 'estimated'

            # Apply +10% cap protection (spec locked)
            cur.execute("""
                SELECT recorded_cap FROM coin_history
                WHERE coin=%s AND exchange='MEXC'
                ORDER BY id DESC LIMIT 1
            """, (coin,))
            prev = cur.fetchone()
            if prev and prev[0] and cap > 0:
                prev_cap = float(prev[0])
                # Cap upward at +10% per day · full drop allowed
                if cap > prev_cap:
                    recorded_cap = min(cap, prev_cap * 1.10)
                else:
                    recorded_cap = cap  # full drop immediately
            else:
                recorded_cap = cap

            cur.execute("""
                INSERT INTO coin_history (coin, exchange, real_cap, recorded_cap, category, volume_24h, source)
                VALUES (%s, 'MEXC', %s, %s, %s, %s, %s)
            """, (coin, cap, recorded_cap, category, vol, source))
            inserted += 1

            # first_seen_at: set once, permanent, survives coin_history wipes.
            # This is the real-world age signal used by the new-coin hard gate.
            cur.execute("""
                INSERT INTO coin_first_seen (coin, first_seen_at)
                VALUES (%s, NOW())
                ON CONFLICT (coin) DO NOTHING
            """, (coin,))

        conn.commit()

    print(f'✅ Classified {inserted} coins')

    # Summary
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT category, COUNT(*) 
            FROM (SELECT DISTINCT ON (coin) coin, category FROM coin_history ORDER BY coin, id DESC) t
            GROUP BY category ORDER BY count DESC
        """)
        print('\n📊 Classification summary:')
        for row in cur.fetchall():
            print(f'  {row[0]}: {row[1]} coins')

if __name__ == '__main__':
    run()
