"""
position_loader.py - Shared by Long and Short (NOT Scalper - confirmed
Scalper's positions live in a different table, live_positions, with
a genuinely different shape, stays in scalper_engine.py).

Takes direction as a parameter ('long' or 'short'), selecting the
full union of fields either system needs from the one shared
positions table - same principle as bot_loader.py. Each caller reads
only the fields relevant to its own direction.
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
import database as db


def load_open_positions(bot_id, direction):
    """direction: 'long' or 'short'."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, coin, avg_cost, avg_sell_price, quantity,
                   total_invested, total_sold_usdt,
                   last_buy_price, last_sell_price,
                   dca_count, tp_armed, peak_price,
                   pos_tp_pct, pos_trail_pct, pos_dca_pct,
                   status, opened_at, wallet_id,
                   pending_buyback, short_buyback_order_id,
                   sequence_number, standby_amount
            FROM positions
            WHERE bot_id=%s AND status='open' AND direction=%s
            ORDER BY opened_at ASC
        """, (bot_id, direction))
        rows = cur.fetchall()

    positions = []
    for r in rows:
        positions.append({
            'id': r[0], 'coin': r[1],
            'avg_cost': float(r[2] or 0), 'avg_sell_price': float(r[3] or 0),
            'quantity': float(r[4] or 0),
            'total_invested': float(r[5] or 0), 'total_sold_usdt': float(r[6] or 0),
            'last_buy_price': float(r[7] or 0), 'last_sell_price': float(r[8] or 0),
            'dca_count': int(r[9] or 0),
            'tp_armed': r[10], 'peak_price': float(r[11] or 0),
            'pos_tp_pct': float(r[12]) if r[12] is not None else None,
            'pos_trail_pct': float(r[13]) if r[13] is not None else None,
            'pos_dca_pct': float(r[14]) if r[14] is not None else None,
            'status': r[15], 'opened_at': r[16], 'wallet_id': r[17],
            'pending_buyback': r[18] or False,
            'short_buyback_order_id': r[19],
            'sequence_number': r[20],
            'standby_amount': float(r[21] or 0),
        })
    return positions
