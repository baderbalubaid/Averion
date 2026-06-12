"""
generate_scalper_results.py
Generates SCALPER_RESULTS.md — monthly P&L tracker for top 20 scalper bots by Score
Run daily via generate_reports.sh
"""
import sys, json
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime, date, timedelta
db.init_pool()

def get_top20_scalper_score():
    """Get top 20 scalper bots by Champ Score formula."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.name,
                ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric,2) as total_pnl,
                COUNT(*) FILTER (WHERE s.status='closed') as trades,
                ROUND(SUM(CASE WHEN s.pnl_usdt > 0 THEN s.pnl_usdt ELSE 0 END) FILTER (WHERE s.status='closed')::numeric,2) as gross_win,
                ROUND(SUM(ABS(s.pnl_usdt)) FILTER (WHERE s.status='closed' AND s.pnl_usdt <= 0)::numeric,2) as gross_loss,
                array_agg(s.pnl_usdt ORDER BY s.pnl_usdt DESC) FILTER (WHERE s.status='closed') as all_pnls
            FROM bots b
            LEFT JOIN scalper_positions s ON s.bot_id=b.id
            WHERE b.method='E58'
            GROUP BY b.id, b.name
            HAVING COUNT(*) FILTER (WHERE s.status='closed') > 0
        """)
        rows = cur.fetchall()

    scored = []
    for r in rows:
        bot_id, name, total_pnl, trades, gross_win, gross_loss, all_pnls = r
        total_pnl = float(total_pnl or 0)
        gross_win = float(gross_win or 0)
        gross_loss = float(gross_loss or 0)
        pnls = [float(x) for x in (all_pnls or [])]
        excl5 = sum(pnls[5:]) if len(pnls) > 5 else total_pnl
        pf = gross_win/gross_loss if gross_loss > 0 else gross_win
        score = total_pnl*0.4 + excl5*0.3 + pf*0.2 + (trades or 0)*0.1
        scored.append({'id': bot_id, 'name': name, 'score': score, 'total_pnl': total_pnl})

    scored.sort(key=lambda x: -x['score'])
    return scored[:20]

def get_daily_pnl(bot_id, target_date):
    """Get cumulative P&L up to end of target_date (UTC)."""
    with db.get_db() as conn:
        cur = conn.cursor()
        next_day = target_date + timedelta(days=1)
        cur.execute("""
            SELECT ROUND(COALESCE(SUM(pnl_usdt), 0)::numeric, 2)
            FROM scalper_positions
            WHERE bot_id = %s
            AND status = 'closed'
            AND exit_time < %s
        """, (bot_id, next_day))
        return float(cur.fetchone()[0] or 0)

def generate():
    now = datetime.utcnow()
    # Saudi time = UTC+3
    saudi_now = now + timedelta(hours=3)
    today = saudi_now.date()
    current_month = today.month
    current_year = today.year

    # Get top 20 bots
    top20 = get_top20_scalper_score()
    bot_ids = [b['id'] for b in top20]
    bot_names = [b['name'] for b in top20]

    # Days in current month so far
    days_so_far = list(range(1, today.day + 1))
    
    # Total days in month
    if current_month == 12:
        next_month = date(current_year + 1, 1, 1)
    else:
        next_month = date(current_year, current_month + 1, 1)
    days_in_month = (next_month - date(current_year, current_month, 1)).days
    all_days = list(range(1, days_in_month + 1))

    # Check if SCALPER_RESULTS.md exists to get start balances
    results_path = '/home/averion/Averion/reports/SCALPER_RESULTS.md'
    start_balances = {b['name']: 0.0 for b in top20}

    # Build table
    month_name = today.strftime('%B %Y')
    
    md = f'# Scalper Monthly P&L Tracker\n\n'
    md += f'> Top 20 bots by Champ Score · Cumulative net P&L · Updated: {saudi_now.strftime("%Y-%m-%d %H:%M")} (Saudi time)\n\n'
    md += f'---\n\n'
    md += f'## {month_name}\n\n'

    # Build header row
    header = '| Bot | Trigger | Hold | Start |'
    separator = '|-----|---------|------|-------|'
    for d in all_days:
        header += f' {d} |'
        separator += '-----|'
    md += header + '\n'
    md += separator + '\n'

    # Get bot params
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, bot_params::text FROM bots WHERE method='E58'")
        bot_params = {r[1]: json.loads(r[2]) if r[2] else {} for r in cur.fetchall()}

    # Fill rows
    for bot in top20:
        name = bot['name']
        p = bot_params.get(name, {})
        trigger = p.get('trigger_pct', '?')
        hold = p.get('hold_sec', '?')
        start = start_balances.get(name, 0.0)
        
        row = f'| {name} | {trigger}% | {hold}s | ${start:.2f} |'
        
        for d in all_days:
            day_date = date(current_year, current_month, d)
            if day_date <= today:
                pnl = get_daily_pnl(bot['id'], day_date)
                pnl_str = f'${pnl:.2f}'
                # Color coding with +/-
                if pnl > 0:
                    pnl_str = f'+${pnl:.2f}'
                elif pnl < 0:
                    pnl_str = f'-${abs(pnl):.2f}'
                row += f' {pnl_str} |'
            else:
                row += ' - |'
        
        md += row + '\n'

    md += '\n'
    md += f'> Score formula: 40% Total P&L + 30% Excl Top 5 + 20% Profit Factor + 10% Trade Count\n'
    md += f'> Start = cumulative P&L at start of month · Values = cumulative all-time P&L up to that day\n'

    with open(results_path, 'w') as f:
        f.write(md)

    print(f'✅ SCALPER_RESULTS.md generated · {len(top20)} bots · {month_name}')
    print(f'   Days filled: {today.day}/{days_in_month}')

if __name__ == '__main__':
    generate()
