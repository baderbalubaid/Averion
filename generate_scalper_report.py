"""
generate_scalper_report.py
Scalper-specific research report for E58 bots
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

    with db.get_db() as conn:
        cur = conn.cursor()

        # Overview
        cur.execute("SELECT COUNT(DISTINCT b.name) FROM scalper_positions s JOIN bots b ON b.id=s.bot_id")
        total_bots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM scalper_positions WHERE status='closed'")
        total_closed = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM scalper_positions WHERE status='open'")
        total_open = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(ROUND(SUM(pnl_usdt)::numeric,2),0) FROM scalper_positions WHERE status='closed'")
        total_pnl = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FILTER (WHERE pnl_pct>0), COUNT(*) FILTER (WHERE pnl_pct<=0) FROM scalper_positions WHERE status='closed'")
        wins, losses = cur.fetchone()

        md = f'# Averion E58 Scalper Research Report\n\n'
        md += f'> Generated: {now} · Paper trading · MEXC · WebSocket Momentum Scalper\n\n'
        md += '> ⚠️ **DATA WARNING:** Early stage paper trading. Use for directional guidance only.\n\n'
        md += '---\n\n'

        md += '## Overview\n\n'
        md += '| Metric | Value |\n|--------|-------|\n'
        md += f'| Active Scalper Bots | {total_bots} |\n'
        md += f'| Closed Trades | {total_closed:,} |\n'
        md += f'| Open Positions | {total_open:,} |\n'
        md += f'| Total P&L | ${total_pnl} |\n'
        md += f'| Win Rate | {round(wins/(wins+losses)*100,1) if wins+losses else 0}% |\n'
        md += f'| Wins | {wins:,} |\n'
        md += f'| Losses | {losses:,} |\n\n'

        md += '## Architecture\n\n'
        md += '- **Entry:** WebSocket price jump detection (real-time, <1s latency)\n'
        md += '- **Exit:** Fixed timer (hold_sec) OR stop loss\n'
        md += '- **Base order:** $100 per trade\n'
        md += '- **No DCA, no trailing, no TP**\n'
        md += '- **Cleanup:** Stuck positions closed every 30s on restart\n\n'

        # Full rankings
        cur.execute("""
            SELECT b.name, b.bot_params::text,
                   COUNT(*) FILTER (WHERE s.status='closed') as closed,
                   COUNT(*) FILTER (WHERE s.status='closed' AND s.pnl_pct > 0) as wins,
                   ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric, 3) as avg_pnl,
                   ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric, 2) as total_pnl,
                   ROUND(MAX(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric, 2) as best,
                   ROUND(MIN(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric, 2) as worst,
                   COUNT(*) FILTER (WHERE s.status='open') as open_now,
                   COUNT(*) FILTER (WHERE s.exit_reason='stop_loss') as sl_exits,
                   COUNT(*) FILTER (WHERE s.exit_reason='timer') as timer_exits,
                   COUNT(*) FILTER (WHERE s.exit_reason='timer_recovery') as recovered,
                   ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed' AND s.pnl_pct > 0)::numeric,3) as avg_win_pct,
                   ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed' AND s.pnl_pct <= 0)::numeric,3) as avg_loss_pct,
                   ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed' AND s.pnl_usdt > 0)::numeric,2) as gross_win,
                   ROUND(SUM(ABS(s.pnl_usdt)) FILTER (WHERE s.status='closed' AND s.pnl_usdt <= 0)::numeric,2) as gross_loss,
                   array_agg(s.pnl_usdt ORDER BY s.pnl_usdt DESC) FILTER (WHERE s.status='closed') as all_pnls
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            GROUP BY b.name, b.bot_params
            HAVING COUNT(*) FILTER (WHERE s.status='closed') > 0
            ORDER BY total_pnl DESC NULLS LAST
        """)
        rows = cur.fetchall()

        md += '## Full Rankings\n\n'
        md += '| Rank | Bot | Trigger% | Window | Hold | SL% | Open | Closed | Win% | Avg Win% | Avg Loss% | PF | Total P&L | Excl Top5 | Robustness% | Timer | SL | Recovered |\n'
        md += '|------|-----|----------|--------|------|-----|------|--------|------|----------|-----------|------|-------|-------|----|-----------|\n'

        for i, r in enumerate(rows, 1):
            name, params_raw, closed, wins_b, avg_pnl, total_pnl_b, best, worst, open_now, sl_exits, timer_exits, recovered, avg_win_pct, avg_loss_pct, gross_win, gross_loss, all_pnls = r
            try:
                p = json.loads(params_raw) if params_raw else {}
            except:
                p = {}
            wr = round(wins_b/closed*100, 1) if closed else 0
            hold = p.get('hold_sec','?')
            trigger = p.get('trigger_pct','?')
            window = p.get('window_sec','?')
            sl = p.get('stop_loss_pct','off')
            pf = round(float(gross_win or 0)/float(gross_loss or 1),2)
            pnls = [float(x) for x in (all_pnls or [])]
            total_f = float(total_pnl_b or 0)
            excl5 = round(sum(pnls[5:]),2) if len(pnls)>5 else total_f
            rob = round(excl5/total_f*100,1) if total_f > 0 else 0
            md += f'| {i} | {name} | {trigger}% | {window}s | {hold}s | {sl} | {open_now} | {closed} | {wr}% | {avg_win_pct}% | {avg_loss_pct}% | {pf} | ${total_f} | ${excl5} | {rob}% | {timer_exits} | {sl_exits} | {recovered} |\n'

        md += '\n'

        # Analysis by trigger%
        md += '## Analysis by Trigger %\n\n'
        md += '> How does trigger sensitivity affect performance?\n\n'
        cur.execute("""
            SELECT (b.bot_params->>'trigger_pct')::numeric as trigger,
                   COUNT(*) FILTER (WHERE s.status='closed') as closed,
                   COUNT(*) FILTER (WHERE s.status='closed' AND s.pnl_pct>0) as wins,
                   ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric,3) as avg_pnl,
                   ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric,2) as total_pnl
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            WHERE s.status='closed'
            GROUP BY trigger ORDER BY trigger
        """)
        md += '| Trigger% | Trades | Win% | Avg P&L% | Total P&L |\n'
        md += '|----------|--------|------|----------|----------|\n'
        for r in cur.fetchall():
            trigger, closed, wins_b, avg_pnl, total_pnl_b = r
            wr = round(wins_b/closed*100,1) if closed else 0
            md += f'| {trigger}% | {closed} | {wr}% | {avg_pnl}% | ${total_pnl_b} |\n'
        md += '\n'

        # Analysis by hold time
        md += '## Analysis by Hold Time\n\n'
        md += '> Does longer holding = better results?\n\n'
        cur.execute("""
            SELECT (b.bot_params->>'hold_sec')::numeric as hold,
                   COUNT(*) FILTER (WHERE s.status='closed') as closed,
                   COUNT(*) FILTER (WHERE s.status='closed' AND s.pnl_pct>0) as wins,
                   ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric,3) as avg_pnl,
                   ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric,2) as total_pnl
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            WHERE s.status='closed'
            GROUP BY hold ORDER BY hold
        """)
        md += '| Hold (sec) | Trades | Win% | Avg P&L% | Total P&L |\n'
        md += '|------------|--------|------|----------|----------|\n'
        for r in cur.fetchall():
            hold, closed, wins_b, avg_pnl, total_pnl_b = r
            wr = round(wins_b/closed*100,1) if closed else 0
            md += f'| {hold}s | {closed} | {wr}% | {avg_pnl}% | ${total_pnl_b} |\n'
        md += '\n'

        # Top coins
        md += '## Top 20 Coins for Scalping\n\n'
        cur.execute("""
            SELECT s.coin,
                   COUNT(*) as trades,
                   COUNT(*) FILTER (WHERE s.pnl_pct>0) as wins,
                   ROUND(AVG(s.pnl_pct)::numeric,3) as avg_pnl,
                   ROUND(SUM(s.pnl_usdt)::numeric,2) as total_pnl
            FROM scalper_positions s
            WHERE s.status='closed'
            GROUP BY s.coin HAVING COUNT(*) >= 5
            ORDER BY avg_pnl DESC LIMIT 20
        """)
        md += '| Coin | Trades | Win% | Avg P&L% | Total P&L |\n'
        md += '|------|--------|------|----------|----------|\n'
        for r in cur.fetchall():
            coin, trades, wins_b, avg_pnl, total_pnl_b = r
            wr = round(wins_b/trades*100,1) if trades else 0
            md += f'| {coin} | {trades} | {wr}% | {avg_pnl}% | ${total_pnl_b} |\n'
        md += '\n'

        # ── BTC REGIME BREAKDOWN ──
        md += '## Scalper Performance by BTC Regime\n\n'
        md += '> bull = BTC >2% above SMA50 · bear = <2% below · sideways = between\n\n'
        cur.execute("""
            SELECT b.name, s.btc_regime,
                COUNT(*) FILTER (WHERE s.status='closed') as trades,
                COUNT(*) FILTER (WHERE s.status='closed' AND s.pnl_pct > 0) as wins,
                ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric,3) as avg_pnl,
                ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric,2) as total_pnl
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            WHERE s.btc_regime IS NOT NULL
            GROUP BY b.name, s.btc_regime
            HAVING COUNT(*) FILTER (WHERE s.status='closed') >= 3
            ORDER BY b.name, s.btc_regime
            LIMIT 50
        """)
        regime_rows = cur.fetchall()
        if regime_rows:
            md += '| Bot | Regime | Trades | Win% | Avg P&L% | Total P&L |\n'
            md += '|-----|--------|--------|------|----------|-----------|\n'
            for r2 in regime_rows:
                bot_name, regime, trades, wins, avg_pnl, total_pnl = r2
                wr = round(wins/trades*100,1) if trades else 0
                md += f'| {bot_name} | {regime} | {trades} | {wr}% | {avg_pnl}% | ${total_pnl} |\n'
            md += '\n'
        else:
            md += '_Not enough regime data yet — collecting now_\n\n'

        # Questions for AI
        md += '## Questions for AI Analysis\n\n'
        md += '1. Which trigger% shows best risk/reward? Is higher trigger better?\n'
        md += '2. What is the optimal hold time? Does longer = better?\n'
        md += '3. Which bots should we expand with more variants?\n'
        md += '4. Are there patterns in which coins scalp best?\n'
        md += '5. Should we add stop loss to all bots or keep some without?\n'
        md += '6. Any signs the strategy is fundamentally flawed?\n'
        md += '7. What new parameter combinations should we test?\n'

    path = '/home/averion/Averion/reports/RESEARCH_REPORT_SCALPER.md'
    with open(path, 'w') as f:
        f.write(md)
    print(f'✅ Scalper report generated: {path}')
    print(f'   {total_bots} bots · {total_closed:,} closed trades · ${total_pnl} total P&L')

if __name__ == '__main__':
    run()
