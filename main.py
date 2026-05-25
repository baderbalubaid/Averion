import time
import ccxt
from datetime import datetime
from database import get_db, init_db
from dca_logic import calc_new_average, should_dca, should_take_profit, calc_quantity
from config import *

exchange = ccxt.mexc()

def get_price():
    ticker = exchange.fetch_ticker(COIN)
    return ticker['last']

def open_position(price):
    quantity = calc_quantity(BASE_ORDER_USDT, price)
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO positions 
                 (coin, avg_cost, quantity, total_invested, dca_count)
                 VALUES (?, ?, ?, ?, 0)''',
              (COIN, price, quantity, BASE_ORDER_USDT))
    position_id = c.lastrowid
    c.execute('''INSERT INTO trades 
                 (position_id, side, price, quantity, usdt_amount, reason, paper)
                 VALUES (?, 'buy', ?, ?, ?, 'open', ?)''',
              (position_id, price, quantity, BASE_ORDER_USDT, 1 if PAPER_MODE else 0))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] OPEN: {quantity:.6f} {COIN} @ ${price} | Avg: ${price}")
    return position_id

def dca_position(position, price):
    quantity = calc_quantity(BASE_ORDER_USDT, price)
    new_total = position['total_invested'] + BASE_ORDER_USDT
    new_qty = position['quantity'] + quantity
    new_avg = calc_new_average(new_total, new_qty)
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE positions SET avg_cost=?, quantity=?, 
                 total_invested=?, dca_count=dca_count+1 
                 WHERE id=?''',
              (new_avg, new_qty, new_total, position['id']))
    c.execute('''INSERT INTO trades 
                 (position_id, side, price, quantity, usdt_amount, reason, paper)
                 VALUES (?, 'buy', ?, ?, ?, 'dca', ?)''',
              (position['id'], price, quantity, BASE_ORDER_USDT, 1 if PAPER_MODE else 0))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] DCA #{position['dca_count']+1}: {quantity:.6f} @ ${price} | New Avg: ${new_avg:.4f}")

def close_position(position, price):
    profit = (price - position['avg_cost']) * position['quantity']
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE positions SET status='closed', closed_at=CURRENT_TIMESTAMP 
                 WHERE id=?''', (position['id'],))
    c.execute('''INSERT INTO trades 
                 (position_id, side, price, quantity, usdt_amount, reason, paper)
                 VALUES (?, 'sell', ?, ?, ?, 'tp', ?)''',
              (position['id'], price, position['quantity'],
               position['quantity'] * price, 1 if PAPER_MODE else 0))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] TAKE PROFIT: Sold @ ${price} | Profit: ${profit:.4f}")

def get_open_position():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM positions WHERE status='open' AND coin=? LIMIT 1", (COIN,))
    pos = c.fetchone()
    conn.close()
    return pos

def run_bot(stop_event=None):
    init_db()
    print(f"Bot started! Coin: {COIN} | DCA: {DCA_PERCENT}% | TP: {TAKE_PROFIT_PERCENT}%")
    print(f"Mode: {'PAPER' if PAPER_MODE else 'LIVE'}")
    print("-" * 50)

    trailing_high = None

    while stop_event is None or not stop_event.is_set():
        try:
            price = get_price()
            print(f"[{datetime.now()}] Price: ${price}")
            position = get_open_position()

            if position is None:
                print("No open position. Opening now...")
                open_position(price)
                trailing_high = None

            else:
                if should_dca(position['avg_cost'], price, DCA_PERCENT):
                    if position['dca_count'] < MAX_DCA_ORDERS:
                        dca_position(position, price)
                    else:
                        print(f"Max DCA orders reached ({MAX_DCA_ORDERS})")

                if should_take_profit(position['avg_cost'], price, TAKE_PROFIT_PERCENT):
                    if trailing_high is None or price > trailing_high:
                        trailing_high = price
                        print(f"TP armed! Trailing high: ${trailing_high}")

                    trail_trigger = trailing_high * (1 - TRAILING_PERCENT / 100)
                    if price <= trail_trigger:
                        close_position(position, price)
                        trailing_high = None
                    else:
                        print(f"Trailing... High: ${trailing_high} | Trigger: ${trail_trigger:.4f}")

        except Exception as e:
            print(f"Error: {e}")

        print(f"Waiting {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_bot()
