"""
rars_scoring.py — RARS Champion Scoring Engine
LOCKED FORMULA: Score = (WR_norm^0.30) x (AP_norm^0.20) x (RS_norm^0.15) x (DD_norm^0.35)

Normalization (locked):
- WR_norm = Win Rate (0-1)
- AP_norm = (avg_profit - min) / (max - min) across all methods
- RS_norm = 1/(recovery_hours+1) then normalized
- DD_norm = 1 - drawdown_pct, floor at 0.01

Promotion rules (locked):
- < 30 trades  → score = 0, not eligible
- 30-99 trades → PROVISIONAL
- 100+ trades  → full eligibility
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime

db.init_pool()

def calculate_rars():
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                b.method,
                p.total_invested,
                p.total_sold_usdt,
                p.opened_at,
                p.closed_at,
                p.dca_count,
                b.base_order,
                b.take_profit_percent
            FROM positions p
            JOIN bots b ON b.id = p.bot_id
            WHERE p.status = 'closed'
            AND b.is_research = TRUE
            ORDER BY b.method, p.closed_at
        """)
        rows = cur.fetchall()

    if not rows:
        return []

    # Get open positions + capital locked per method
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.method,
                   COUNT(*) as open_count,
                   ROUND(SUM(p.total_invested)::numeric,2) as capital_locked
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE p.status='open' AND b.is_research=TRUE
            GROUP BY b.method
        """)
        open_data = {r[0]: {'open':r[1],'capital':float(r[2] or 0)} for r in cur.fetchall()}

    # Group by method
    methods = {}
    for row in rows:
        method = row[0]
        if method not in methods:
            methods[method] = []
        pnl = float(row[2] or 0) - float(row[1] or 0)
        hold_hours = 0
        if row[3] and row[4]:
            hold_hours = (row[4] - row[3]).total_seconds() / 3600
        methods[method].append({
            'pnl': pnl,
            'invested': float(row[1] or 0),
            'dca_count': int(row[5] or 0),
            'hold_hours': max(hold_hours, 0.01),
            'base_order': float(row[6] or 100),
            'tp_pct': float(row[7] or 5),
        })

    raw = []
    for method, trades in methods.items():
        profits = [t['pnl'] for t in trades]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p <= 0]
        n = len(trades)

        # WR: win rate 0-1
        wr = len(wins) / n

        # AP: avg profit per trade
        avg_profit = sum(profits) / n

        # RS: recovery speed = 1/(avg_hold_hours+1)
        avg_hold = sum(t['hold_hours'] for t in trades) / n
        rs_raw = 1 / (avg_hold + 1)

        # DD: drawdown = avg DCA count / tp_pct ratio
        # Higher DCA needed = worse drawdown
        avg_dca = sum(t['dca_count'] for t in trades) / n
        tp_pct = trades[0]['tp_pct']
        # Drawdown estimate: each DCA averages down by dca_spacing
        drawdown_pct = avg_dca * 0.07  # approx 7% per DCA level
        dd = max(0.01, 1 - drawdown_pct)

        raw.append({
            'method': method,
            'trade_count': n,
            'open_positions': open_data.get(method,{}).get('open',0),
            'capital_locked': open_data.get(method,{}).get('capital',0),
            'wr': wr,
            'avg_profit': avg_profit,
            'rs_raw': rs_raw,
            'dd': dd,
            'avg_hold_hours': round(avg_hold, 1),
            'avg_dca': round(avg_dca, 2),
            'total_profit': round(sum(profits), 2),
            'win_count': len(wins),
            'loss_count': len(losses),
        })

    if not raw:
        return []

    # Normalize AP and RS across all methods
    ap_vals = [s['avg_profit'] for s in raw]
    rs_vals = [s['rs_raw'] for s in raw]
    ap_min, ap_max = min(ap_vals), max(ap_vals)
    rs_min, rs_max = min(rs_vals), max(rs_vals)

    results = []
    for s in raw:
        # Normalize
        wr_norm = s['wr']  # already 0-1
        ap_norm = (s['avg_profit'] - ap_min) / (ap_max - ap_min + 1e-9)
        rs_norm = (s['rs_raw'] - rs_min) / (rs_max - rs_min + 1e-9)
        dd_norm = max(s['dd'], 0.01)

        # Epsilon floors
        wr_norm = max(wr_norm, 0.01)
        ap_norm = max(ap_norm, 0.01)
        rs_norm = max(rs_norm, 0.01)
        dd_norm = max(dd_norm, 0.01)

        # LOCKED FORMULA
        rars = (wr_norm**0.30) * (ap_norm**0.20) * (rs_norm**0.15) * (dd_norm**0.35)
        rars_score = round(rars * 100, 2)

        # Eligibility
        if s['trade_count'] < 30:
            status = 'NOT_ELIGIBLE'
            rars_score = 0
        elif s['trade_count'] < 100:
            status = 'PROVISIONAL'
        else:
            status = 'ELIGIBLE'

        results.append({
            'method': s['method'],
            'trade_count': s['trade_count'],
            'open_positions': s.get('open_positions',0),
            'capital_locked': s.get('capital_locked',0),
            'win_rate': round(s['wr'] * 100, 1),
            'avg_profit_per_trade': round(s['avg_profit'], 2),
            'avg_hold_hours': s['avg_hold_hours'],
            'avg_dca': s['avg_dca'],
            'total_profit': s['total_profit'],
            'rars_score': rars_score,
            'status': status,
            'wr_norm': round(wr_norm, 3),
            'ap_norm': round(ap_norm, 3),
            'rs_norm': round(rs_norm, 3),
            'dd_norm': round(dd_norm, 3),
        })

    results.sort(key=lambda x: -x['rars_score'])
    return results

if __name__ == '__main__':
    scores = calculate_rars()
    print(f'\n{"="*85}')
    print(f'RARS CHAMPION SCORES — {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print(f'Formula: Score = WR^0.30 × AP^0.20 × RS^0.15 × DD^0.35')
    print(f'{"="*85}')
    print(f'{"Rank":<5} {"Method":<10} {"RARS":<8} {"Status":<14} {"Trades":<8} {"Win%":<7} {"AvgP$":<8} {"AvgDCA":<8} {"Hold"}')
    print(f'{"-"*85}')
    for i, s in enumerate(scores, 1):
        print(f'{i:<5} {s["method"]:<10} {s["rars_score"]:<8} {s["status"]:<14} {s["trade_count"]:<8} {s["win_rate"]:<7} {s["avg_profit_per_trade"]:<8} {s["avg_dca"]:<8} {s["avg_hold_hours"]}h')
    print(f'RECORDS_PROCESSED:{len(scores)}')
