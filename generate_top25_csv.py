"""
generate_top25_csv.py
Generates detailed trade-level CSVs for top 25 DCA and Scalper bots
"""
import sys, json, csv
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime
db.init_pool()

def generate_dca_csv():
    with db.get_db() as conn:
        cur = conn.cursor()

        # Get top 25 DCA bots by RARS (avg_pnl proxy, min 10 closed trades)
        cur.execute("""
            SELECT b.id, b.name, b.method, b.bot_params::text,
                   COUNT(*) FILTER (WHERE p.status='closed') as closed,
                   ROUND(AVG(p.total_sold_usdt - p.total_invested) FILTER (WHERE p.status='closed')::numeric,2) as avg_pnl,
                   COUNT(*) FILTER (WHERE p.status='closed' AND p.total_sold_usdt > p.total_invested) as wins
            FROM bots b
            LEFT JOIN positions p ON p.bot_id=b.id
            WHERE b.is_research=TRUE AND b.method NOT LIKE 'BM%'
            GROUP BY b.id, b.name, b.method, b.bot_params
            HAVING COUNT(*) FILTER (WHERE p.status='closed') >= 10
            ORDER BY avg_pnl DESC NULLS LAST
            LIMIT 25
        """)
        top_bots = cur.fetchall()
        top_bot_ids = [r[0] for r in top_bots]
        top_bot_info = {r[0]: r for r in top_bots}

        if not top_bot_ids:
            print('No DCA bots with enough data')
            return

        # Get all trades for top 25 bots
        cur.execute("""
            SELECT 
                b.name as bot_name,
                b.method,
                b.bot_params::text as params,
                p.id as position_id,
                p.coin,
                p.category,
                p.status,
                p.direction,
                p.avg_cost as entry_price,
                p.avg_sell_price as exit_price,
                p.quantity,
                p.total_invested,
                p.total_sold_usdt,
                ROUND((p.total_sold_usdt - p.total_invested)::numeric, 4) as pnl_usd,
                CASE WHEN p.total_invested > 0 THEN
                    ROUND(((p.total_sold_usdt - p.total_invested) / p.total_invested * 100)::numeric, 2)
                ELSE 0 END as pnl_pct,
                p.dca_count,
                p.opened_at as entry_time,
                p.closed_at as exit_time,
                CASE WHEN p.closed_at IS NOT NULL AND p.opened_at IS NOT NULL THEN
                    ROUND(EXTRACT(EPOCH FROM (p.closed_at - p.opened_at))/3600::numeric, 2)
                ELSE
                    ROUND(EXTRACT(EPOCH FROM (NOW() - p.opened_at))/3600::numeric, 2)
                END as hold_hours,
                p.tp_armed,
                p.peak_price,
                p.last_buy_price,
                p.pos_tp_pct,
                p.pos_dca_pct,
                p.pos_trail_pct,
                p.is_paper,
                p.sequence_number,
                p.coin_trade_number
            FROM positions p
            JOIN bots b ON b.id=p.bot_id
            WHERE b.id = ANY(%s)
            ORDER BY b.name, p.opened_at
        """, (top_bot_ids,))
        trades = cur.fetchall()

    path = '/home/averion/Averion/docs/TOP25_DCA_TRADES.csv'
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'bot_name', 'method', 'params',
            'position_id', 'coin', 'category', 'status', 'direction',
            'entry_price', 'exit_price', 'quantity',
            'total_invested_usd', 'total_sold_usd',
            'pnl_usd', 'pnl_pct',
            'dca_count', 'entry_time', 'exit_time', 'hold_hours',
            'tp_armed', 'peak_price', 'last_buy_price',
            'pos_tp_pct', 'pos_dca_pct', 'pos_trail_pct',
            'is_paper', 'sequence_number', 'coin_trade_number'
        ])
        for t in trades:
            writer.writerow(t)

    print(f'✅ DCA CSV: {len(trades)} trades · top {len(top_bots)} bots')
    print(f'   File: {path}')
    print(f'   Top bots: {[r[1] for r in top_bots[:5]]}...')


def generate_scalper_csv():
    with db.get_db() as conn:
        cur = conn.cursor()

        # Get top 25 scalper bots by avg_pnl
        cur.execute("""
            SELECT b.id, b.name, b.bot_params::text,
                   COUNT(*) FILTER (WHERE s.status='closed') as closed,
                   ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric, 3) as avg_pnl,
                   COUNT(*) FILTER (WHERE s.status='closed' AND s.pnl_pct > 0) as wins
            FROM bots b
            LEFT JOIN scalper_positions s ON s.bot_id=b.id
            WHERE b.method='E58'
            GROUP BY b.id, b.name, b.bot_params
            HAVING COUNT(*) FILTER (WHERE s.status='closed') >= 3
            ORDER BY avg_pnl DESC NULLS LAST
            LIMIT 25
        """)
        top_bots = cur.fetchall()
        top_bot_ids = [r[0] for r in top_bots]

        if not top_bot_ids:
            print('No scalper bots with enough data')
            return

        # Get all trades
        cur.execute("""
            SELECT
                b.name as bot_name,
                (b.bot_params->>'trigger_pct')::numeric as trigger_pct,
                (b.bot_params->>'window_sec')::numeric as window_sec,
                (b.bot_params->>'hold_sec')::numeric as hold_sec,
                COALESCE(b.bot_params->>'stop_loss_pct', 'none') as stop_loss_pct,
                s.id as trade_id,
                s.coin,
                s.status,
                s.entry_price,
                s.exit_price,
                s.entry_time,
                s.exit_time,
                CASE WHEN s.exit_time IS NOT NULL THEN
                    ROUND(EXTRACT(EPOCH FROM (s.exit_time - s.entry_time))::numeric, 1)
                ELSE
                    ROUND(EXTRACT(EPOCH FROM (NOW() - s.entry_time))::numeric, 1)
                END as actual_hold_sec,
                s.pnl_pct,
                s.pnl_usdt,
                s.max_profit_seen,
                s.max_loss_seen,
                s.exit_reason,
                s.base_order,
                CASE WHEN s.entry_price > 0 AND s.exit_price IS NOT NULL THEN
                    ROUND(((s.exit_price - s.entry_price) / s.entry_price * 100)::numeric, 4)
                ELSE NULL END as raw_price_change_pct,
                CASE WHEN s.max_profit_seen IS NOT NULL AND s.pnl_pct IS NOT NULL THEN
                    ROUND((s.max_profit_seen - s.pnl_pct)::numeric, 3)
                ELSE NULL END as missed_profit_pct
            FROM scalper_positions s
            JOIN bots b ON b.id=s.bot_id
            WHERE b.id = ANY(%s)
            ORDER BY b.name, s.entry_time
        """, (top_bot_ids,))
        trades = cur.fetchall()

    path = '/home/averion/Averion/docs/TOP25_SCALPER_TRADES.csv'
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'bot_name', 'trigger_pct', 'window_sec', 'hold_sec', 'stop_loss_pct',
            'trade_id', 'coin', 'status',
            'entry_price', 'exit_price',
            'entry_time', 'exit_time', 'actual_hold_sec',
            'pnl_pct', 'pnl_usd',
            'max_profit_seen', 'max_loss_seen',
            'exit_reason', 'base_order',
            'raw_price_change_pct', 'missed_profit_pct'
        ])
        for t in trades:
            writer.writerow(t)

    print(f'✅ Scalper CSV: {len(trades)} trades · top {len(top_bots)} bots')
    print(f'   File: {path}')
    print(f'   Top bots: {[r[1] for r in top_bots[:5]]}...')


if __name__ == '__main__':
    print('Generating Top 25 DCA trades CSV...')
    generate_dca_csv()
    print('\nGenerating Top 25 Scalper trades CSV...')
    generate_scalper_csv()
    print('\n✅ Done! Push to GitHub to download.')
