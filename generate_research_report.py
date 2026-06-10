"""
generate_research_report.py
Generates a comprehensive markdown research report
for sharing with AI assistants (ChatGPT, Gemini, Claude)
"""
import sys, json
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime
db.init_pool()

def run():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    md = f'# Averion Research Report\n'
    md += f'> Generated: {now} · Paper trading · MEXC Exchange\n\n'
    md += '---\n\n'

    with db.get_db() as conn:
        cur = conn.cursor()

        # ── OVERVIEW ──
        cur.execute("SELECT COUNT(*) FROM bots WHERE is_research=TRUE")
        total_bots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT method) FROM bots WHERE is_research=TRUE")
        total_methods = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM positions WHERE status='open'")
        open_pos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM positions WHERE status='closed'")
        closed_pos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM scalper_positions WHERE status='closed'")
        scalper_closed = cur.fetchone()[0]
        cur.execute("SELECT ROUND(SUM(total_sold_usdt - total_invested)::numeric, 2) FROM positions WHERE status='closed'")
        total_pnl = cur.fetchone()[0] or 0
        cur.execute("SELECT ROUND(SUM(pnl_usdt)::numeric, 2) FROM scalper_positions WHERE status='closed'")
        scalper_pnl = cur.fetchone()[0] or 0

        md += '## Overview\n\n'
        md += f'| Metric | Value |\n|--------|-------|\n'
        md += f'| Total Research Bots | {total_bots} |\n'
        md += f'| Total Methods | {total_methods} |\n'
        md += f'| Open DCA Positions | {open_pos:,} |\n'
        md += f'| Closed DCA Positions | {closed_pos:,} |\n'
        md += f'| Closed Scalper Trades | {scalper_closed:,} |\n'
        md += f'| Total DCA P&L | ${total_pnl:,} |\n'
        md += f'| Total Scalper P&L | ${scalper_pnl} |\n\n'

        # ── RARS SCORES ──
        md += '## DCA Method Rankings (RARS Score)\n\n'
        md += '> Formula: Score = WR^0.30 × AP^0.20 × RS^0.15 × DD^0.35\n\n'

        cur.execute("""
            SELECT b.method,
                COUNT(*) as trades,
                COUNT(*) FILTER (WHERE total_sold_usdt > total_invested) as wins,
                ROUND(AVG(total_sold_usdt - total_invested)::numeric, 2) as avg_pnl,
                ROUND(SUM(total_sold_usdt - total_invested)::numeric, 2) as total_pnl,
                ROUND(AVG(EXTRACT(EPOCH FROM (closed_at - opened_at))/3600)::numeric, 1) as avg_hold_hrs,
                ROUND(AVG(dca_count)::numeric, 2) as avg_dca
            FROM positions p
            JOIN bots b ON b.id=p.bot_id
            WHERE p.status='closed' AND b.is_research=TRUE
            GROUP BY b.method
            HAVING COUNT(*) >= 5
            ORDER BY avg_pnl DESC
        """)
        rows = cur.fetchall()

        md += f'| Method | Trades | Win% | Avg P&L | Total P&L | Hold Hrs | Avg DCA |\n'
        md += f'|--------|--------|------|---------|-----------|----------|---------|\n'
        for r in rows:
            win_rate = round(r[2]/r[1]*100, 1) if r[1] > 0 else 0
            md += f'| {r[0]} | {r[1]} | {win_rate}% | ${r[3]} | ${r[4]} | {r[5]}h | {r[6]} |\n'
        md += '\n'

        # ── SCALPER RESULTS ──
        md += '## E58 WebSocket Scalper Results\n\n'
        md += '> Entry: WebSocket price jump detection · Exit: Fixed timer or stop loss\n\n'

        cur.execute("""
            SELECT b.name,
                   (b.bot_params->>'trigger_pct')::numeric as trigger,
                   (b.bot_params->>'window_sec')::numeric as window,
                   (b.bot_params->>'hold_sec')::numeric as hold,
                   (b.bot_params->>'stop_loss_pct') as sl,
                   COUNT(*) as trades,
                   COUNT(*) FILTER (WHERE s.pnl_pct > 0) as wins,
                   ROUND(AVG(s.pnl_pct)::numeric, 3) as avg_pnl,
                   ROUND(MAX(s.pnl_pct)::numeric, 2) as best,
                   ROUND(MIN(s.pnl_pct)::numeric, 2) as worst
            FROM scalper_positions s
            JOIN bots b ON b.id=s.bot_id
            WHERE s.status='closed'
            GROUP BY b.name, b.bot_params
            ORDER BY avg_pnl DESC
        """)
        scalper_rows = cur.fetchall()

        md += f'| Bot | Trigger% | Window | Hold | SL% | Trades | Win% | Avg PnL% | Best | Worst |\n'
        md += f'|-----|----------|--------|------|-----|--------|------|----------|------|-------|\n'
        for r in scalper_rows:
            win_rate = round(r[6]/r[5]*100, 1) if r[5] > 0 else 0
            md += f'| {r[0]} | {r[1]}% | {r[2]}s | {r[3]}s | {r[4] or "off"} | {r[5]} | {win_rate}% | {r[7]}% | {r[8]}% | {r[9]}% |\n'
        md += '\n'

        # ── COIN CATEGORY PERFORMANCE ──
        md += '## Performance by Coin Category\n\n'
        cur.execute("""
            SELECT p.category,
                COUNT(*) as trades,
                COUNT(*) FILTER (WHERE total_sold_usdt > total_invested) as wins,
                ROUND(AVG(total_sold_usdt - total_invested)::numeric, 2) as avg_pnl,
                ROUND(AVG(dca_count)::numeric, 2) as avg_dca
            FROM positions p
            WHERE p.status='closed'
            GROUP BY p.category
            ORDER BY avg_pnl DESC
        """)
        md += f'| Category | Trades | Win% | Avg P&L | Avg DCA |\n'
        md += f'|----------|--------|------|---------|----------|\n'
        for r in cur.fetchall():
            win_rate = round(r[2]/r[1]*100, 1) if r[1] > 0 else 0
            md += f'| {r[0]} | {r[1]} | {win_rate}% | ${r[3]} | {r[4]} |\n'
        md += '\n'

        # ── TOP PERFORMING COINS ──
        md += '## Top 20 Performing Coins\n\n'
        cur.execute("""
            SELECT p.coin, p.category,
                COUNT(*) as trades,
                ROUND(AVG(total_sold_usdt - total_invested)::numeric, 2) as avg_pnl,
                ROUND(SUM(total_sold_usdt - total_invested)::numeric, 2) as total_pnl
            FROM positions p
            WHERE p.status='closed'
            GROUP BY p.coin, p.category
            HAVING COUNT(*) >= 3
            ORDER BY avg_pnl DESC
            LIMIT 20
        """)
        md += f'| Coin | Category | Trades | Avg P&L | Total P&L |\n'
        md += f'|------|----------|--------|---------|----------|\n'
        for r in cur.fetchall():
            md += f'| {r[0]} | {r[1]} | {r[2]} | ${r[3]} | ${r[4]} |\n'
        md += '\n'

        # ── WORST PERFORMING COINS ──
        md += '## Bottom 10 Coins (Most DCA Needed)\n\n'
        cur.execute("""
            SELECT p.coin, p.category,
                COUNT(*) as trades,
                ROUND(AVG(dca_count)::numeric, 2) as avg_dca,
                ROUND(AVG(total_sold_usdt - total_invested)::numeric, 2) as avg_pnl
            FROM positions p
            WHERE p.status='open'
            GROUP BY p.coin, p.category
            HAVING COUNT(*) >= 5
            ORDER BY avg_dca DESC
            LIMIT 10
        """)
        md += f'| Coin | Category | Positions | Avg DCA | Avg P&L |\n'
        md += f'|------|----------|-----------|---------|----------|\n'
        for r in cur.fetchall():
            md += f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | ${r[4]} |\n'
        md += '\n'

        # ── METHOD DESCRIPTIONS ──
        md += '## All Research Methods\n\n'
        cur.execute("""
            SELECT method, COUNT(*) as bots,
                   COUNT(DISTINCT p.coin) FILTER (WHERE p.status='closed') as coins_traded
            FROM bots b
            LEFT JOIN positions p ON p.bot_id=b.id
            WHERE b.is_research=TRUE
            GROUP BY method
            ORDER BY method
        """)
        md += f'| Method | Bots | Coins Traded |\n'
        md += f'|--------|------|--------------|\n'
        for r in cur.fetchall():
            md += f'| {r[0]} | {r[1]} | {r[2] or 0} |\n'
        md += '\n'

        # ── KEY INSIGHTS ──
        md += '## Key Observations for AI Analysis\n\n'
        md += '### What we know so far:\n'
        md += '- All bots use paper trading on MEXC exchange\n'
        md += '- DCA bots: fixed $100 base order, dynamic TP/DCA/trail per coin category\n'
        md += '- Scalper bots: $100 per scalp, WebSocket price detection, fixed timer exit\n'
        md += '- Coin categories: mega (>$100B), large ($10B-$100B), mid ($1B-$10B), small ($100M-$1B), micro (<$100M)\n'
        md += '- RARS scoring: WR^0.30 × AP^0.20 × RS^0.15 × DD^0.35\n\n'
        md += '### Questions for AI analysis:\n'
        md += '1. Which DCA methods show most consistent edge across different coins?\n'
        md += '2. Which scalper parameters (trigger%, hold time) show best risk/reward?\n'
        md += '3. Are there patterns in which coin categories respond best to which methods?\n'
        md += '4. What parameter variations should we test next?\n'
        md += '5. Which methods should be promoted to champion status first?\n'
        md += '6. Any concerning patterns in the data (overfitting, luck, etc)?\n\n'

    # Save
    path = '/home/averion/Averion/docs/RESEARCH_REPORT.md'
    with open(path, 'w') as f:
        f.write(md)

    print(f'✅ Research report generated: {path}')
    print(f'   DCA closed: {closed_pos:,} · Scalper closed: {scalper_closed:,}')
    print(f'   Methods: {total_methods} · Bots: {total_bots}')

if __name__ == '__main__':
    run()
