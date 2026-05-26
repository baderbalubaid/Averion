import ccxt
import time
from datetime import datetime
from database import get_db, init_db
from dca_logic import calc_new_average, should_take_profit, calc_quantity
from config import *

exchange = ccxt.mexc({'enableRateLimit': True})

def get_all_coins():
    try:
        markets = exchange.load_markets()
        coins = [
            symbol for symbol, market in markets.items()
            if symbol.endswith('/USDT')
            and market.get('active', True)
            and market.get('spot', True)
        ]
        coins = coins[:100]
        print(f"Found {len(coins)} coins on MEXC")
        return coins
    except Exception as e:
        print(f"Error fetching coins: {e}")
        return ["BTC/USDT", "ETH/USDT", "XRP/USDT"]

def get_price(coin):
    ticker = exchange.fetch_ticker(coin)
    return ticker['last']

def open_position(coin, price):
    quantity = calc_quantity(BASE_ORDER_USDT, price)
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO positions 
                 (coin, avg_cost, quantity, total_invested, dca_count, last_buy_price)
                 VALUES (?, ?, ?, ?, 0, ?)''',
              (coin, price, quantity, BASE_ORDER_USDT, price))
    position_id = c.lastrowid
    c.execute('''INSERT INTO trades 
                 (position_id, side, price, quantity, usdt_amount, reason, paper)
                 VALUES (?, 'buy', ?, ?, ?, 'open', ?)''',
              (position_id, price, quantity, BASE_ORDER_USDT, 1 if PAPER_MODE else 0))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] OPEN {coin}: {quantity:.6f} @ ${price}")
    return position_id

def dca_position(position, price):
    dca_num = position['dca_count'] + 1
    size = BASE_ORDER_USDT * (SIZE_MULTIPLIER ** dca_num)
    quantity = calc_quantity(size, price)
    new_total = position['total_invested'] + size
    new_qty = position['quantity'] + quantity
    new_avg = calc_new_average(new_total, new_qty)
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE positions SET avg_cost=?, quantity=?,
                 total_invested=?, dca_count=dca_count+1,
                 last_buy_price=? WHERE id=?''',
              (new_avg, new_qty, new_total, price, position['id']))
    c.execute('''INSERT INTO trades
                 (position_id, side, price, quantity, usdt_amount, reason, paper)
                 VALUES (?, 'buy', ?, ?, ?, 'dca', ?)''',
              (position['id'], price, quantity, size, 1 if PAPER_MODE else 0))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] DCA #{dca_num} {position['coin']} @ ${price} | New Avg: ${new_avg:.6f}")

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
    print(f"[{datetime.now()}] TP {position['coin']} @ ${price} | Profit: ${profit:.4f}")

def get_open_position(coin):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM positions WHERE status='open' AND coin=? LIMIT 1", (coin,))
    pos = c.fetchone()
    conn.close()
    return pos

def run_bot():
    init_db()
    print("Averion Bot Started!")
    print(f"Mode: {'PAPER' if PAPER_MODE else 'LIVE'}")
    print("Fetching all coins from MEXC...")
    print("-" * 50)

    trailing_highs = {}

    while True:
        try:
            coins = get_all_coins()
            print(f"Trading {len(coins)} coins...")

            for coin in coins:
                try:
                    price = get_price(coin)
                    position = get_open_position(coin)

                    if position is None:
                        open_position(coin, price)
                        trailing_highs[coin] = None
                    else:
                        last_buy = position['last_buy_price'] or position['avg_cost']
                        dca_count = position['dca_count']
                        spacing = DCA_PERCENT * (SPACING_MULTIPLIER ** dca_count)
                        trigger = last_buy * (1 - spacing / 100)

                        if price <= trigger:
                            if MAX_DCA_ORDERS == 0 or dca_count < MAX_DCA_ORDERS:
                                dca_position(position, price)

                        if should_take_profit(position['avg_cost'], price, TAKE_PROFIT_PERCENT):
                            if trailing_highs.get(coin) is None or price > trailing_highs[coin]:
                                trailing_highs[coin] = price
                            trail_trigger = trailing_highs[coin] * (1 - TRAILING_PERCENT / 100)
                            if price <= trail_trigger:
                                close_position(position, price)
                                trailing_highs[coin] = None

                except Exception as e:
                    print(f"Error on {coin}: {e}")
                    continue

        except Exception as e:
            print(f"Bot error: {e}")

        print(f"Cycle complete. Waiting {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run_bot()
