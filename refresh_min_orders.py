"""
Daily refresh of real exchange minimum order sizes into the
exchange_min_orders table. Run by cron once per day - exchange
minimums essentially never change intraday, so a fast database read
during actual trading never needs to hit the slow live API.

Also intended for future use: bot creation wizard validation (when a
user picks an exchange + coin, check their chosen order size against
this table before letting them proceed).
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
import ccxt
from exchanges import decrypt, get_min_order_size

db.init_pool()

def run():
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, exchange, api_key_enc, secret_enc FROM exchanges")
        exchanges_list = cur.fetchall()
        cur.execute("SELECT DISTINCT coin FROM coin_parameters")
        coins = [r[0] for r in cur.fetchall()]

    print(f"Refreshing min orders for {len(exchanges_list)} exchanges x {len(coins)} coins")
    total_updated = 0

    for exc_id, exc_name, api_key_enc, secret_enc in exchanges_list:
        try:
            api_key = decrypt(api_key_enc) if api_key_enc else ''
            secret = decrypt(secret_enc) if secret_enc else ''
            exchange_class = getattr(ccxt, exc_name.lower())
            exchange_obj = exchange_class({
                'apiKey': api_key, 'secret': secret, 'enableRateLimit': True
            })
            exchange_obj.load_markets()
        except Exception as e:
            print(f"Could not init exchange {exc_name} (id={exc_id}): {e}")
            continue

        updated = 0
        for coin in coins:
            symbol = f"{coin}/USDT"
            if symbol not in exchange_obj.markets:
                continue
            try:
                result = get_min_order_size(exchange_obj, symbol)
                db.upsert_min_order(exc_id, coin, result['min_amount'], result['min_cost'])
                updated += 1
            except Exception as e:
                print(f"  {coin} on {exc_name}: {e}")
        print(f"{exc_name} (id={exc_id}): updated {updated}/{len(coins)} coins")
        total_updated += updated

    print("Min order refresh complete")
    print(f"RECORDS_PROCESSED:{total_updated}")

if __name__ == '__main__':
    run()
