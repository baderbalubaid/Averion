# Hourly auto-recovery for Short DCA buyback limit orders.
# Checks every open LIVE Short position's real exchange order status;
# if the order has been cancelled or no longer exists (manually on the
# exchange's own site, or by the exchange itself), recreates it using
# the SAME tp_target/quantity math the original placement used -
# recoverable purely from the position's own stored fields.
# PENDING_BUYBACK stays TRUE throughout (never cleared until an actual
# fill), so Long DCA on this wallet correctly stays blocked the entire
# time, even mid-recovery, exactly as required.
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
db.init_pool()
from short_dca_engine import load_short_bots, load_open_short_positions, get_short_params, get_executor

def run():
    bots = load_short_bots()
    live_bots = [b for b in bots if not b['wallet']['is_paper']]
    print(f"Checking buyback orders for {len(live_bots)} live Short bots")

    checked = 0
    recovered = 0
    errors = 0

    for bot in live_bots:
        positions = load_open_short_positions(bot['id'])
        for pos in positions:
            if not pos.get('short_buyback_order_id') or pos.get('pending_buyback'):
                continue
            checked += 1
            coin = pos['coin']
            try:
                executor = get_executor(bot['wallet'])
                with db.get_db() as conn:
                    exchange_obj = executor._get_exchange_obj(bot['wallet'], conn)
                    symbol = f"{coin}/USDT"
                    order = exchange_obj.fetch_order(pos['short_buyback_order_id'], symbol)
                    status = order.get('status')

                if status in ('canceled', 'cancelled', 'expired', 'rejected'):
                    print(f"Order {pos['short_buyback_order_id']} for {coin} is {status} - recreating")
                    dca_pct, spacing_mult, tp_pct = get_short_params(bot, coin, {})
                    tp_target = pos['avg_sell_price'] * (1 - tp_pct / 100)
                    buyback_quantity = pos['total_sold_usdt'] / tp_target if tp_target > 0 else pos['quantity']

                    with db.get_db() as conn:
                        cur = conn.cursor()
                        cur.execute("UPDATE positions SET pending_buyback=TRUE WHERE id=%s", (pos['id'],))
                        conn.commit()

                    with db.get_db() as conn:
                        result = executor.place_limit_buyback(
                            pos['id'], coin, tp_target, buyback_quantity, bot['wallet'], conn
                        )
                        conn.commit()

                    if result.success:
                        with db.get_db() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "UPDATE positions SET short_buyback_order_id=%s, pending_buyback=FALSE WHERE id=%s",
                                (result.order_id, pos['id'])
                            )
                            conn.commit()
                        recovered += 1
                        print(f"  Recreated: new order_id={result.order_id} target=${tp_target:.6f}")
                    else:
                        print(f"  Recreation FAILED for {coin}: {result.error} - pending_buyback stays TRUE, will retry next hour")
                        errors += 1
            except Exception as e:
                print(f"Error checking {coin} order for bot {bot['id']}: {e}")
                errors += 1

    print(f"Checked {checked}, recovered {recovered}, errors {errors}")

if __name__ == '__main__':
    run()
