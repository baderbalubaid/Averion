import ccxt
import psycopg2
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

EXCHANGES = {
    'mexc': ccxt.mexc(),
    'binance': ccxt.binance(),
}

def get_active_coins(conn, exchange_name):
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT coin FROM positions 
        WHERE status = 'open' 
        AND exchange_id IN (
            SELECT id FROM exchanges WHERE exchange = %s
        )
    """, (exchange_name,))
    return [row[0] for row in cur.fetchall()]

def fetch_and_store_ohlcv(conn, exchange, exchange_name, coin):
    try:
        since = exchange.parse8601(
            (datetime.utcnow() - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        ohlcv = exchange.fetch_ohlcv(coin, '1h', since=since, limit=2)
        
        cur = conn.cursor()
        for candle in ohlcv:
            timestamp = datetime.utcfromtimestamp(candle[0] / 1000)
            cur.execute("""
                INSERT INTO ohlcv_hourly 
                (coin, exchange, timestamp, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (coin, exchange, timestamp) DO NOTHING
            """, (coin, exchange_name, timestamp,
                  candle[1], candle[2], candle[3], candle[4], candle[5]))
        conn.commit()
        print(f"✅ {exchange_name} {coin}: {len(ohlcv)} candles stored")
        
    except Exception as e:
        print(f"❌ {exchange_name} {coin}: {e}")
        conn.rollback()

def calculate_atr(conn, exchange_name, coin, periods=14):
    cur = conn.cursor()
    cur.execute("""
        SELECT high, low, close FROM ohlcv_hourly
        WHERE coin = %s AND exchange = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """, (coin, exchange_name, periods + 1))
    
    rows = cur.fetchall()
    if len(rows) < periods:
        return None
    
    true_ranges = []
    for i in range(len(rows) - 1):
        high = float(rows[i][0])
        low = float(rows[i][1])
        prev_close = float(rows[i+1][2])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)
    
    atr = sum(true_ranges[:periods]) / periods
    
    cur.execute("""
        UPDATE ohlcv_hourly SET atr_14 = %s
        WHERE coin = %s AND exchange = %s
        AND timestamp = (
            SELECT MAX(timestamp) FROM ohlcv_hourly
            WHERE coin = %s AND exchange = %s
        )
    """, (atr, coin, exchange_name, coin, exchange_name))
    conn.commit()
    return atr

def cleanup_old_ohlcv(conn):
    cur = conn.cursor()
    cutoff = datetime.utcnow() - timedelta(days=90)
    cur.execute("DELETE FROM ohlcv_hourly WHERE timestamp < %s", (cutoff,))
    deleted = cur.rowcount
    conn.commit()
    print(f"🧹 Cleaned up {deleted} old OHLCV rows (>90 days)")

def main():
    print(f"🔄 OHLCV fetch started: {datetime.utcnow()}")
    conn = psycopg2.connect(**DB_CONFIG)
    
    for exchange_name, exchange in EXCHANGES.items():
        coins = get_active_coins(conn, exchange_name)
        print(f"📊 {exchange_name}: fetching {len(coins)} coins")
        
        for coin in coins:
            fetch_and_store_ohlcv(conn, exchange, exchange_name, coin)
            calculate_atr(conn, exchange_name, coin)
            time.sleep(0.1)
    
    cleanup_old_ohlcv(conn)
    conn.close()
    print(f"✅ OHLCV fetch complete: {datetime.utcnow()}")

if __name__ == '__main__':
    main()
