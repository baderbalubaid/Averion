"""
rars_scoring.py — RARS Champion Scoring Engine
Calculates scores for all research bot methods
RARS = 35% Capital Efficiency + 30% Drawdown + 20% Win Rate + 15% Profit Factor
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
import json
from datetime import datetime

db.init_pool()

def calculate_rars():
    with db.get_db() as conn:
        cur = conn.cursor()
        
        # Get all closed research positions grouped by method
        cur.execute("""
            SELECT 
                b.method,
                b.id as bot_id,
                b.name as bot_name,
                p.total_invested,
                p.total_sold_usdt,
                p.opened_at,
                p.closed_at,
                p.dca_count,
                p.close_reason
            FROM positions p
            JOIN bots b ON b.id = p.bot_id
            WHERE p.status = 'closed'
            AND b.is_research = TRUE
            ORDER BY b.method, p.closed_at
        """)
        rows = cur.fetchall()

    if not rows:
        return []

    # Group by method
    methods = {}
    for row in rows:
        method = row[0]
        if method not in methods:
            methods[method] = []
        methods[method].append({
            'bot_id': row[1],
            'bot_name': row[2],
            'invested': float(row[3] or 0),
            'received': float(row[4] or 0),
            'opened_at': row[5],
            'closed_at': row[6],
            'dca_count': row[7],
            'reason': row[8],
        })

    results = []
    for method, trades in methods.items():
        if len(trades) < 3:  # need min 3 trades
            continue

        profits = [t['received'] - t['invested'] for t in trades]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p <= 0]
        
        total_invested = sum(t['invested'] for t in trades)
        total_profit = sum(profits)
        win_rate = len(wins) / len(profits) * 100
        avg_profit = sum(wins) / len(wins) if wins else 0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 0.01
        profit_factor = avg_profit / avg_loss if avg_loss > 0 else avg_profit
        
        # Capital efficiency = total profit / total invested * 100
        cap_efficiency = total_profit / total_invested * 100 if total_invested > 0 else 0
        
        # Max drawdown (simplified)
        max_loss = abs(min(profits)) if losses else 0
        max_drawdown = max_loss / total_invested * 100 if total_invested > 0 else 0
        
        # Avg hold time in hours
        hold_times = []
        for t in trades:
            if t['opened_at'] and t['closed_at']:
                delta = (t['closed_at'] - t['opened_at']).total_seconds() / 3600
                hold_times.append(delta)
        avg_hold = sum(hold_times) / len(hold_times) if hold_times else 0

        # RARS score (0-100)
        # Capital efficiency score (35%) - normalize to 0-100
        ce_score = min(cap_efficiency * 2, 100)  # 50% return = 100 score
        # Drawdown score (30%) - lower is better
        dd_score = max(0, 100 - max_drawdown * 4)
        # Win rate score (20%)
        wr_score = win_rate
        # Profit factor score (15%)
        pf_score = min(profit_factor * 20, 100)

        rars = (ce_score * 0.35 + dd_score * 0.30 + wr_score * 0.20 + pf_score * 0.15)

        results.append({
            'method': method,
            'trade_count': len(trades),
            'win_rate': round(win_rate, 1),
            'total_profit': round(total_profit, 2),
            'avg_profit_per_trade': round(total_profit / len(trades), 2),
            'capital_efficiency': round(cap_efficiency, 2),
            'max_drawdown': round(max_drawdown, 2),
            'profit_factor': round(profit_factor, 2),
            'avg_hold_hours': round(avg_hold, 1),
            'rars_score': round(rars, 2),
            'ce_score': round(ce_score, 1),
            'dd_score': round(dd_score, 1),
            'wr_score': round(wr_score, 1),
            'pf_score': round(pf_score, 1),
        })

    # Sort by RARS score
    results.sort(key=lambda x: -x['rars_score'])
    return results

if __name__ == '__main__':
    scores = calculate_rars()
    print(f'\n{"="*70}')
    print(f'RARS CHAMPION SCORES — {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print(f'{"="*70}')
    print(f'{"Rank":<5} {"Method":<8} {"RARS":<7} {"Trades":<8} {"Win%":<7} {"AvgP$":<8} {"Cap%":<7} {"DD%":<6}')
    print(f'{"-"*70}')
    for i, s in enumerate(scores[:20], 1):
        print(f'{i:<5} {s["method"]:<8} {s["rars_score"]:<7} {s["trade_count"]:<8} {s["win_rate"]:<7} {s["avg_profit_per_trade"]:<8} {s["capital_efficiency"]:<7} {s["max_drawdown"]:<6}')
