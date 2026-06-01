import psycopg2
import requests
import os
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

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telegram as tg

def send_telegram(msg):
    tg.send_admin(msg)

def main():
    print(f'=== CMC Fetch started: {datetime.utcnow()} ===')

    if not CMC_API_KEY:
        msg = '⚠️ CMC API key not set · skipping CMC fetch'
        print(msg)
        send_telegram(msg)
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    now = datetime.utcnow()

    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
        params = {'start': 1, 'limit': 5000, 'convert': 'USD'}
        r = requests.get(url, headers=headers, params=params, timeout=30)

        if r.status_code != 200:
            msg = f'❌ CMC fetch failed: {r.status_code}'
            print(msg)
            send_telegram(msg)
            conn.close()
            return

        data = r.json()
        total = 0
        for coin in data.get('data', []):
            symbol = coin.get('symbol', '').upper()
            cap = coin.get('quote', {}).get('USD', {}).get('market_cap') or 0
            if cap <= 0:
                continue
            cur.execute("""
                INSERT INTO coin_history
                (coin, real_cap, recorded_cap, category, recorded_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (symbol, cap, cap, 'pending', now))
            total += 1

        conn.commit()
        msg = f'✅ CMC fetch complete: {total} coins stored'
        print(msg)
        send_telegram(msg)

    except Exception as e:
        msg = f'❌ CMC fetch error: {e}'
        print(msg)
        send_telegram(msg)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
