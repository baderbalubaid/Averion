"""
fetch_btc_daily.py
Fetches latest BTC daily candle and stores in btc_daily table.
Run daily via cron to keep SMA50 updated.
"""
import sys, ccxt
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime, timezone
db.init_pool()

exchange = ccxt.mexc({'enableRateLimit': True})
ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='1d', limit=3)

with db.get_db() as conn:
    cur = conn.cursor()
    inserted = 0
    for candle in ohlcv:
        ts, open_, high, low, close, volume = candle
        dt = datetime.fromtimestamp(ts/1000, tz=timezone.utc).replace(tzinfo=None)
        cur.execute("""
            INSERT INTO btc_daily (timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp) DO UPDATE SET
                high=EXCLUDED.high, low=EXCLUDED.low,
                close=EXCLUDED.close, volume=EXCLUDED.volume
        """, (dt, open_, high, low, close, volume))
        inserted += 1
    conn.commit()

# Verify SMA50
cur2 = conn.cursor() if False else db.get_db().__enter__().cursor()
with db.get_db() as conn2:
    cur2 = conn2.cursor()
    cur2.execute("SELECT close FROM btc_daily ORDER BY timestamp DESC LIMIT 50")
    rows = cur2.fetchall()
    sma50 = sum(float(r[0]) for r in rows) / len(rows)
    price = float(rows[0][0])
    regime = 'bull' if price > sma50*1.02 else 'bear' if price < sma50*0.98 else 'sideways'
    print(f'✅ BTC daily updated · Price=${price:,.2f} · SMA50=${sma50:,.2f} · {regime.upper()}')
    print(f'RECORDS_PROCESSED:{inserted}')
