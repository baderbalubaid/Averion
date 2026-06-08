"""
fetch_ohlcv.py — Hourly OHLCV fetcher for all active exchange coins
Runs every hour via cron · stores data in ohlcv_hourly table
Currently: MEXC only · other exchanges added later
"""

import os
import time
import ccxt
from datetime import datetime, timezone
from dotenv import load_dotenv
import database as db
from exchanges import decrypt

load_dotenv()

# How many hourly candles to fetch per coin
CANDLE_LIMIT = 200  # ~8 days of hourly data

def get_active_exchanges():
    """Get all active exchanges from DB."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT e.id, e.exchange, e.api_key_enc,
                   e.secret_enc, e.passphrase_enc
            FROM exchanges e
            JOIN bots b ON b.exchange_id = e.id
            WHERE b.status = 'open'
            AND e.paused_at IS NULL
            AND e.active = TRUE
        """)
        return cur.fetchall()

def init_public_exchange(exchange_name):
    """Init exchange WITHOUT api keys for public data."""
    try:
        exchange_class = getattr(ccxt, exchange_name)
        ex = exchange_class({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        return ex
    except Exception as e:
        print(f'❌ Failed to init {exchange_name}: {e}')
        return None

def fetch_coins_for_exchange(exchange_name):
    """Get all USDT pairs on this exchange."""
    try:
        ex = init_public_exchange(exchange_name)
        if not ex:
            return []
        markets = ex.load_markets()
        coins = [
            s.replace('/USDT', '')
            for s in markets.keys()
            if s.endswith('/USDT') and ':' not in s
        ]
        return coins, ex
    except Exception as e:
        print(f'❌ Failed to load markets for {exchange_name}: {e}')
        return [], None

def fetch_ohlcv_for_coin(ex, coin, exchange_name, limit=CANDLE_LIMIT):
    """Fetch hourly OHLCV for one coin and store in DB."""
    symbol = f'{coin}/USDT'
    try:
        candles = ex.fetch_ohlcv(symbol, timeframe='1h', limit=limit)
        if not candles:
            return 0

        stored = 0
        with db.get_db() as conn:
            cur = conn.cursor()
            for c in candles:
                ts = datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc)
                cur.execute("""
                    INSERT INTO ohlcv_hourly
                    (coin, exchange, timestamp, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (coin, exchange, timestamp) DO NOTHING
                """, (coin, exchange_name, ts,
                      c[1], c[2], c[3], c[4], c[5]))
                stored += 1
        return stored

    except Exception as e:
        return 0

def run_fetch():
    """Main fetch loop — runs once per hour."""
    print(f'\n=== OHLCV Fetch · {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} ===')
    db.init_pool()

    # For now: always fetch MEXC as primary exchange
    exchange_name = 'mexc'
    print(f'📡 Fetching OHLCV for {exchange_name}...')

    coins, ex = fetch_coins_for_exchange(exchange_name)
    if not coins:
        print('❌ No coins found')
        return

    print(f'📊 Found {len(coins)} USDT pairs on {exchange_name}')

    total_stored = 0
    errors = 0
    for i, coin in enumerate(coins):
        try:
            n = fetch_ohlcv_for_coin(ex, coin, exchange_name)
            total_stored += n
            if i % 100 == 0:
                print(f'  Progress: {i}/{len(coins)} coins · {total_stored} candles stored')
            time.sleep(0.05)  # rate limit respect
        except Exception as e:
            errors += 1

    # Cleanup old data (keep 90 days)
    deleted = db.cleanup_old_ohlcv(days=90)

    print(f'✅ Done: {total_stored} candles stored · {errors} errors · {deleted} old rows deleted')
    print(f'   Exchange: {exchange_name} · Coins: {len(coins)}')

if __name__ == '__main__':
    run_fetch()
