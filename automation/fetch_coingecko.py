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

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telegram as tg

def send_telegram(msg):
    tg.send_admin(msg)

def fetch_page(page):
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': page,
        'sparkline': False
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 429:
            print('Rate limited · waiting 60s')
            time.sleep(60)
            return fetch_page(page)
        if r.status_code == 200:
            return r.json()
        print(f'Error: {r.status_code}')
        return []
    except Exception as e:
        print(f'Fetch error: {e}')
        return []

def main():
    print(f'=== CoinGecko Fetch started: {datetime.utcnow()} ===')
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    now = datetime.utcnow()

    total = 0
    page = 1
    while True:
        coins = fetch_page(page)
        if not coins:
            break
        for coin in coins:
            symbol = coin.get('symbol', '').upper()
            cap = coin.get('market_cap') or 0
            volume = coin.get('total_volume') or 0
            if cap <= 0:
                continue
            cur.execute("""
                INSERT INTO coin_history
                (coin, real_cap, recorded_cap, category, volume_24h, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (symbol, cap, cap, 'pending', volume, now))
            total += 1
        conn.commit()
        print(f'Page {page}: {len(coins)} coins stored')
        page += 1
        time.sleep(1.5)

    conn.close()
    msg = f'✅ CoinGecko fetch complete: {total} coins stored'
    print(msg)
    send_telegram(msg)

if __name__ == '__main__':
    main()
