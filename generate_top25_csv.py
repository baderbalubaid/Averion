"""
generate_top25_csv.py
Generates 4 trade-level CSVs:
- TOP20_DCA_RARS_TRADES.csv    — top 20 DCA bots by RARS score
- TOP20_DCA_SCORE_TRADES.csv   — top 20 DCA bots by Champ Score
- TOP20_SCALPER_RARS_TRADES.csv — top 20 scalper bots by avg P&L
- TOP20_SCALPER_SCORE_TRADES.csv — top 20 scalper bots by Score formula
"""
import sys, json, csv
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime
db.init_pool()

DCA_COLUMNS = [
    'bot_name', 'method', 'params',
    'position_id', 'coin', 'category', 'status', 'direction',
    'entry_price', 'exit_price', 'quantity',
    'total_invested_usd', 'total_sold_usd',
    'pnl_usd', 'pnl_pct', 'is_clean_win',
    'dca_count', 'entry_time', 'exit_time', 'hold_hours',
    'tp_armed', 'peak_price', 'last_buy_price',
    'pos_tp_pct', 'pos_dca_pct', 'pos_trail_pct',
    'is_paper', 'sequence_number', 'coin_trade_number',
    'btc_price_at_entry', 'btc_sma50_at_entry',
    'btc_24h_change_pct', 'btc_regime', 'btc_dominance'
]

SCALPER_COLUMNS = [
    'bot_name', 'trigger_pct', 'window_sec', 'hold_sec', 'stop_loss_pct',
    'trade_id', 'coin', 'status',
    'entry_price', 'exit_price',
    'entry_time', 'exit_time', 'actual_hold_sec',
    'pnl_pct', 'pnl_usd',
    'max_profit_seen', 'max_loss_seen',
    'exit_reason', 'base_order',
    'raw_price_change_pct', 'missed_profit_pct',
    'btc_price_at_entry', 'btc_sma50_at_entry',
    'btc_24h_change_pct', 'btc_regime', 'btc_dominance'
]

def get_dca_trades(bot_ids):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                b.name, b.method, b.bot_params::text,
                p.id, p.coin, p.category, p.status, p.direction,
                p.avg_cost, p.avg_sell_price, p.quantity,
                p.total_invested, p.total_sold_usdt,
                ROUND((p.total_sold_usdt - p.total_invested)::numeric,4),
                CASE WHEN p.total_invested > 0 THEN
                    ROUND(((p.total_sold_usdt - p.total_invested)/p.total_invested*100)::numeric,2)
                ELSE 0 END,
                CASE WHEN p.total_sold_usdt > p.total_invested AND p.dca_count = 0 THEN 1 ELSE 0 END,
                p.dca_count, p.opened_at, p.closed_at,
                CASE WHEN p.closed_at IS NOT NULL THEN
                    ROUND(EXTRACT(EPOCH FROM (p.closed_at-p.opened_at))/3600::numeric,2)
                ELSE
                    ROUND(EXTRACT(EPOCH FROM (NOW()-p.opened_at))/3600::numeric,2)
                END,
                p.tp_armed, p.peak_price, p.last_buy_price,
                p.pos_tp_pct, p.pos_dca_pct, p.pos_trail_pct,
                p.is_paper, p.sequence_number, p.coin_trade_number,
                p.btc_price_at_entry, p.btc_sma50_at_entry,
                p.btc_24h_change_pct, p.btc_regime, p.btc_dominance
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE b.id = ANY(%s)
            ORDER BY b.name, p.opened_at
        """, (bot_ids,))
        return cur.fetchall()

def get_scalper_trades(bot_ids):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                b.name,
                (b.bot_params->>'trigger_pct')::numeric,
                (b.bot_params->>'window_sec')::numeric,
                (b.bot_params->>'hold_sec')::numeric,
                COALESCE(b.bot_params->>'stop_loss_pct','none'),
                s.id, s.coin, s.status,
                s.entry_price, s.exit_price,
                s.entry_time, s.exit_time,
                CASE WHEN s.exit_time IS NOT NULL THEN
                    ROUND(EXTRACT(EPOCH FROM (s.exit_time-s.entry_time))::numeric,1)
                ELSE
                    ROUND(EXTRACT(EPOCH FROM (NOW()-s.entry_time))::numeric,1)
                END,
                s.pnl_pct, s.pnl_usdt,
                s.max_profit_seen, s.max_loss_seen,
                s.exit_reason, s.base_order,
                CASE WHEN s.entry_price > 0 AND s.exit_price IS NOT NULL THEN
                    ROUND(((s.exit_price-s.entry_price)/s.entry_price*100)::numeric,4)
                ELSE NULL END,
                CASE WHEN s.max_profit_seen IS NOT NULL AND s.pnl_pct IS NOT NULL THEN
                    ROUND((s.max_profit_seen-s.pnl_pct)::numeric,3)
                ELSE NULL END,
                s.btc_price_at_entry, s.btc_sma50_at_entry,
                s.btc_24h_change_pct, s.btc_regime, s.btc_dominance
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            WHERE b.id = ANY(%s)
            ORDER BY b.name, s.entry_time
        """, (bot_ids,))
        return cur.fetchall()

def write_csv(path, columns, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow(row)
    return len(rows)

def get_top20_dca_rars():
    """Top 20 DCA bots by RARS (win rate + speed + drawdown)"""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.name,
                COUNT(*) FILTER (WHERE p.status='closed') as closed,
                COUNT(*) FILTER (WHERE p.status='closed' AND p.total_sold_usdt > p.total_invested) as wins,
                ROUND(AVG(p.total_sold_usdt-p.total_invested) FILTER (WHERE p.status='closed')::numeric,2) as avg_pnl,
                ROUND(AVG(p.dca_count) FILTER (WHERE p.status='closed')::numeric,2) as avg_dca,
                ROUND(AVG(EXTRACT(EPOCH FROM (p.closed_at-p.opened_at))/3600) FILTER (WHERE p.status='closed')::numeric,1) as avg_hold
            FROM bots b LEFT JOIN positions p ON p.bot_id=b.id
            WHERE b.is_research=TRUE AND b.method NOT LIKE 'BM%'
            GROUP BY b.id, b.name
            HAVING COUNT(*) FILTER (WHERE p.status='closed') >= 5
        """)
        rows = cur.fetchall()

    # Calculate RARS
    import numpy as np
    raw = []
    for r in rows:
        bot_id, name, trades, wins, avg_pnl, avg_dca, avg_hold = r
        wr = (wins or 0)/(trades or 1)
        rs_raw = 1/(float(avg_hold or 1)+1)
        dd = max(0.01, 1 - float(avg_dca or 0)*0.07)
        raw.append({'id': bot_id, 'name': name, 'trades': trades, 'wr': wr,
                    'avg_pnl': float(avg_pnl or 0), 'rs_raw': rs_raw, 'dd': dd})

    if not raw:
        return []

    ap_vals = [r['avg_pnl'] for r in raw]
    rs_vals = [r['rs_raw'] for r in raw]
    ap_min, ap_max = min(ap_vals), max(ap_vals)
    rs_min, rs_max = min(rs_vals), max(rs_vals)

    for r in raw:
        wr_n = max(r['wr'], 0.01)
        ap_n = max((r['avg_pnl']-ap_min)/(ap_max-ap_min+1e-9), 0.01)
        rs_n = max((r['rs_raw']-rs_min)/(rs_max-rs_min+1e-9), 0.01)
        dd_n = max(r['dd'], 0.01)
        r['rars'] = (wr_n**0.30)*(ap_n**0.20)*(rs_n**0.15)*(dd_n**0.35)*100

    raw.sort(key=lambda x: -x['rars'])
    return [r['id'] for r in raw[:20]]

def get_top20_dca_score():
    """Top 20 DCA bots by Champ Score (total P&L + robustness + PF + trades)"""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id,
                ROUND(SUM(p.total_sold_usdt-p.total_invested) FILTER (WHERE p.status='closed')::numeric,2) as total_pnl,
                COUNT(*) FILTER (WHERE p.status='closed') as trades,
                ROUND(SUM(CASE WHEN p.total_sold_usdt > p.total_invested THEN p.total_sold_usdt-p.total_invested ELSE 0 END) FILTER (WHERE p.status='closed')::numeric,2) as gross_win,
                ROUND(SUM(CASE WHEN p.total_sold_usdt <= p.total_invested THEN p.total_invested-p.total_sold_usdt ELSE 0 END) FILTER (WHERE p.status='closed')::numeric,2) as gross_loss,
                array_agg(p.total_sold_usdt-p.total_invested ORDER BY p.total_sold_usdt-p.total_invested DESC) FILTER (WHERE p.status='closed') as all_pnls
            FROM bots b LEFT JOIN positions p ON p.bot_id=b.id
            WHERE b.is_research=TRUE AND b.method NOT LIKE 'BM%'
            GROUP BY b.id
            HAVING COUNT(*) FILTER (WHERE p.status='closed') >= 5
        """)
        rows = cur.fetchall()

    scored = []
    for r in rows:
        bot_id, total_pnl, trades, gross_win, gross_loss, all_pnls = r
        total_pnl = float(total_pnl or 0)
        gross_win = float(gross_win or 0)
        gross_loss = float(gross_loss or 0)
        pnls = [float(x) for x in (all_pnls or [])]
        excl5 = sum(pnls[5:]) if len(pnls) > 5 else total_pnl
        pf = gross_win/gross_loss if gross_loss > 0 else gross_win
        score = total_pnl*0.4 + excl5*0.3 + pf*0.2 + (trades or 0)*0.1
        scored.append({'id': bot_id, 'score': score})

    scored.sort(key=lambda x: -x['score'])
    return [r['id'] for r in scored[:20]]

def get_top20_scalper_rars():
    """Top 20 scalper bots by avg P&L (RARS equivalent)"""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            WHERE s.status='closed'
            GROUP BY b.id
            HAVING COUNT(*) >= 3
            ORDER BY AVG(s.pnl_pct) DESC NULLS LAST
            LIMIT 20
        """)
        return [r[0] for r in cur.fetchall()]

def get_top20_scalper_score():
    """Top 20 scalper bots by Champ Score"""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id,
                ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric,2) as total_pnl,
                COUNT(*) FILTER (WHERE s.status='closed') as trades,
                ROUND(SUM(CASE WHEN s.pnl_usdt > 0 THEN s.pnl_usdt ELSE 0 END) FILTER (WHERE s.status='closed')::numeric,2) as gross_win,
                ROUND(SUM(ABS(s.pnl_usdt)) FILTER (WHERE s.status='closed' AND s.pnl_usdt <= 0)::numeric,2) as gross_loss,
                array_agg(s.pnl_usdt ORDER BY s.pnl_usdt DESC) FILTER (WHERE s.status='closed') as all_pnls
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            GROUP BY b.id
            HAVING COUNT(*) FILTER (WHERE s.status='closed') >= 3
        """)
        rows = cur.fetchall()

    scored = []
    for r in rows:
        bot_id, total_pnl, trades, gross_win, gross_loss, all_pnls = r
        total_pnl = float(total_pnl or 0)
        gross_win = float(gross_win or 0)
        gross_loss = float(gross_loss or 0)
        pnls = [float(x) for x in (all_pnls or [])]
        excl5 = sum(pnls[5:]) if len(pnls) > 5 else total_pnl
        pf = gross_win/gross_loss if gross_loss > 0 else gross_win
        score = total_pnl*0.4 + excl5*0.3 + pf*0.2 + (trades or 0)*0.1
        scored.append({'id': bot_id, 'score': score})

    scored.sort(key=lambda x: -x['score'])
    return [r['id'] for r in scored[:20]]

if __name__ == '__main__':
    print('Generating 4 trade CSVs...')

    # DCA RARS
    ids = get_top20_dca_rars()
    trades = get_dca_trades(ids)
    n = write_csv('/home/averion/Averion/reports/TOP20_DCA_RARS_TRADES.csv', DCA_COLUMNS, trades)
    print(f'✅ TOP20_DCA_RARS_TRADES.csv: {n} trades · {len(ids)} bots')

    # DCA Score
    ids = get_top20_dca_score()
    trades = get_dca_trades(ids)
    n = write_csv('/home/averion/Averion/reports/TOP20_DCA_SCORE_TRADES.csv', DCA_COLUMNS, trades)
    print(f'✅ TOP20_DCA_SCORE_TRADES.csv: {n} trades · {len(ids)} bots')

    # Scalper RARS
    ids = get_top20_scalper_rars()
    trades = get_scalper_trades(ids)
    n = write_csv('/home/averion/Averion/reports/TOP20_SCALPER_RARS_TRADES.csv', SCALPER_COLUMNS, trades)
    print(f'✅ TOP20_SCALPER_RARS_TRADES.csv: {n} trades · {len(ids)} bots')

    # Scalper Score
    ids = get_top20_scalper_score()
    trades = get_scalper_trades(ids)
    n = write_csv('/home/averion/Averion/reports/TOP20_SCALPER_SCORE_TRADES.csv', SCALPER_COLUMNS, trades)
    print(f'✅ TOP20_SCALPER_SCORE_TRADES.csv: {n} trades · {len(ids)} bots')

    print('\n✅ All 4 CSVs generated!')
