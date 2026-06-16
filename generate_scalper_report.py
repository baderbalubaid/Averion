"""
generate_scalper_report.py
E58 Legacy Scalper Research Report — all 120 bots ranked
"""
import sys, csv
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv; load_dotenv()
import database as db
from datetime import datetime
db.init_pool()

def run():
    now = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    with db.get_db() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*) FROM scalper_positions sp
            JOIN bots b ON b.id=sp.bot_id WHERE b.method='E58' AND sp.status='closed'
        """)
        total_closed = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*) FROM scalper_positions sp
            JOIN bots b ON b.id=sp.bot_id WHERE b.method='E58' AND sp.status='open'
        """)
        total_open = cur.fetchone()[0]
        cur.execute("""
            SELECT COALESCE(ROUND(SUM(sp.pnl_usdt)::numeric,2),0)
            FROM scalper_positions sp JOIN bots b ON b.id=sp.bot_id
            WHERE b.method='E58' AND sp.status='closed'
        """)
        total_pnl = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*) FILTER (WHERE sp.pnl_pct>0),
                   COUNT(*) FILTER (WHERE sp.pnl_pct<=0)
            FROM scalper_positions sp JOIN bots b ON b.id=sp.bot_id
            WHERE b.method='E58' AND sp.status='closed'
        """)
        wins, losses = cur.fetchone()

        # Regime coverage
        cur.execute("""
            SELECT btc_regime, COUNT(*) FROM scalper_positions sp
            JOIN bots b ON b.id=sp.bot_id
            WHERE b.method='E58' AND sp.status='closed'
            GROUP BY btc_regime
        """)
        regimes = {r[0] or 'unknown': r[1] for r in cur.fetchall()}

        # All 120 bots ranked
        cur.execute("""
            SELECT b.name, b.bot_params,
                (b.bot_params->>'trigger_pct')::float as trigger_pct,
                (b.bot_params->>'window_sec')::float as window_sec,
                (b.bot_params->>'hold_sec')::float as hold_sec,
                COUNT(sp.id) FILTER (WHERE sp.status='open') as open_now,
                COUNT(sp.id) FILTER (WHERE sp.status='closed') as closed,
                ROUND(AVG(sp.pnl_pct) FILTER (WHERE sp.status='closed')::numeric,3) as avg_pnl,
                ROUND(SUM(sp.pnl_usdt) FILTER (WHERE sp.status='closed')::numeric,4) as total_pnl,
                ROUND(MAX(sp.pnl_pct) FILTER (WHERE sp.status='closed')::numeric,2) as best,
                ROUND(MIN(sp.pnl_pct) FILTER (WHERE sp.status='closed')::numeric,2) as worst,
                ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sp.pnl_pct)
                    FILTER (WHERE sp.status='closed')::numeric,3) as median_pnl,
                ROUND(STDDEV(sp.pnl_pct) FILTER (WHERE sp.status='closed')::numeric,3) as std_dev,
                COUNT(sp.id) FILTER (WHERE sp.status='closed' AND sp.pnl_pct>0) as wins,
                COUNT(sp.id) FILTER (WHERE sp.status='closed' AND sp.pnl_pct<=0) as losses,
                ROUND(AVG(sp.hold_seconds) FILTER (WHERE sp.status='closed')::numeric,1) as avg_hold
            FROM bots b
            LEFT JOIN scalper_positions sp ON sp.bot_id=b.id
            WHERE b.method='E58' AND b.is_research=TRUE
            GROUP BY b.id, b.name, b.bot_params
            ORDER BY total_pnl DESC NULLS LAST
        """)
        bots = cur.fetchall()

        # Regime per bot (top 20 only for markdown)
        cur.execute("""
            SELECT b.name, sp.btc_regime,
                COUNT(*) as trades,
                ROUND(AVG(sp.pnl_pct)::numeric,3) as avg_pnl,
                COUNT(*) FILTER (WHERE sp.pnl_pct>0)*100/COUNT(*) as win_rate
            FROM scalper_positions sp JOIN bots b ON b.id=sp.bot_id
            WHERE b.method='E58' AND sp.status='closed' AND sp.btc_regime IS NOT NULL
            GROUP BY b.name, sp.btc_regime
        """)
        regime_data = {}
        for r in cur.fetchall():
            if r[0] not in regime_data:
                regime_data[r[0]] = {}
            regime_data[r[0]][r[1] or 'unknown'] = {
                'trades':r[2], 'avg_pnl':float(r[3] or 0), 'win_rate':r[4]
            }

    md = f'# Averion E58 Scalper Research Report\n\n'
    md += f'> Generated: {now} · Paper trading · MEXC · WebSocket Momentum Scalper\n\n'
    md += '> ⚠️ All trades are paper (simulated). Signal: price jump detection.\n\n'
    md += '---\n\n'

    md += '## Overview\n\n'
    md += '| Metric | Value |\n|--------|-------|\n'
    md += f'| Total Bots | 120 |\n'
    md += f'| Closed Trades | {total_closed:,} |\n'
    md += f'| Open Positions | {total_open:,} |\n'
    md += f'| Total P&L | ${total_pnl} |\n'
    md += f'| Win Rate | {round(wins/(wins+losses)*100,1) if wins+losses else 0}% |\n\n'

    md += '## Architecture\n\n'
    md += '- **Signal:** Price jump >= trigger_pct% in window_sec seconds\n'
    md += '- **Exit:** Fixed timer (hold_sec) OR stop loss\n'
    md += '- **Base order:** $100 per trade\n\n'

    md += '## Market Regime Coverage\n\n'
    md += '> ⚠️ Regime analysis preliminary — currently only bear market data.\n\n'
    md += '| Regime | Trades |\n|--------|--------|\n'
    for regime, count in sorted(regimes.items()):
        note = '✅' if count >= 30 else '⚠️'
        md += f'| {regime} | {count:,} {note} |\n'
    md += '\n---\n\n'

    md += '## All 120 Bots Ranked\n\n'
    md += '| Rank | Bot | Trigger% | Window | Hold | Closed | Win% | Avg P&L% | Median% | Std | Total P&L | Score |\n'
    md += '|------|-----|----------|--------|------|--------|------|----------|---------|-----|-----------|-------|\n'

    for i, b in enumerate(bots):
        name = b[0]
        trigger = float(b[2] or 0)
        window = float(b[3] or 0)
        hold = float(b[4] or 0)
        closed = int(b[6] or 0)
        avg_pnl = float(b[7] or 0)
        total_pnl_b = float(b[8] or 0)
        median = float(b[11] or 0)
        std = float(b[12] or 0)
        wins_b = int(b[13] or 0)
        win_rate = round(wins_b/closed*100,1) if closed else 0
        speed = 1.0/max(hold, 1)
        score = round(win_rate * avg_pnl * speed, 4) if closed > 0 else 0
        md += f'| {i+1} | **{name}** | {trigger}% | {window}s | {hold}s | {closed:,} | {win_rate}% | {avg_pnl:+.3f}% | {median:+.3f}% | {std:.3f} | ${total_pnl_b:+.2f} | {score} |\n'

    md += '\n---\n\n'
    md += '## Top 10 Bot Details\n\n'

    for b in bots[:10]:
        name = b[0]
        trigger = float(b[2] or 0)
        window = float(b[3] or 0)
        hold = float(b[4] or 0)
        closed = int(b[6] or 0)
        avg_pnl = float(b[7] or 0)
        total_pnl_b = float(b[8] or 0)
        best = float(b[9] or 0)
        worst = float(b[10] or 0)
        median = float(b[11] or 0)
        std = float(b[12] or 0)
        wins_b = int(b[13] or 0)
        losses_b = int(b[14] or 0)
        avg_hold = float(b[15] or 0)
        win_rate = round(wins_b/closed*100,1) if closed else 0

        md += f'### {name}\n\n'
        md += f'| Metric | Value |\n|--------|-------|\n'
        md += f'| Trigger | {trigger}% in {window}s |\n'
        md += f'| Hold | {hold}s |\n'
        md += f'| Closed Trades | {closed:,} |\n'
        md += f'| Win Rate | {win_rate}% |\n'
        md += f'| Avg P&L | {avg_pnl:+.3f}% |\n'
        md += f'| Median P&L | {median:+.3f}% |\n'
        md += f'| Std Deviation | {std:.3f} |\n'
        md += f'| Best | {best:+.2f}% |\n'
        md += f'| Worst | {worst:+.2f}% |\n'
        md += f'| Total P&L | ${total_pnl_b:+.2f} |\n'
        md += f'| Avg Hold | {avg_hold:.1f}s |\n\n'

        if name in regime_data:
            md += f'**Regime Breakdown:**\n\n'
            md += '| Regime | Trades | Win% | Avg P&L% |\n|--------|--------|------|----------|\n'
            for regime, stats in sorted(regime_data[name].items()):
                note = '' if stats['trades'] >= 30 else ' ⚠️'
                md += f'| {regime} | {stats["trades"]}{note} | {stats["win_rate"]}% | {stats["avg_pnl"]:+.3f}% |\n'
            md += '\n'
        md += '---\n\n'

    with open('reports/RESEARCH_SCALPER.md', 'w') as f:
        f.write(md)
    print(f'✅ RESEARCH_SCALPER.md written ({len(bots)} bots)')

    _generate_scalper_csvs(bots, 'E58', 'SCALPER')

def _generate_scalper_csvs(bots, method, prefix):
    with db.get_db() as conn:
        cur = conn.cursor()

        for rank_type in ['rars', 'score']:
            if rank_type == 'rars':
                ranked = sorted(bots, key=lambda x: float(x[8] or 0), reverse=True)[:5]
            else:
                scored = []
                for b in bots:
                    closed = int(b[6] or 0)
                    if closed == 0: continue
                    total = float(b[8] or 0)
                    wins_b = int(b[13] or 0)
                    wr = wins_b/closed*100 if closed else 0
                    gp = gl = 0
                    cur.execute("""
                        SELECT COALESCE(SUM(sp.pnl_usdt) FILTER (WHERE sp.pnl_usdt>0),0),
                               COALESCE(ABS(SUM(sp.pnl_usdt) FILTER (WHERE sp.pnl_usdt<0)),0.001)
                        FROM scalper_positions sp JOIN bots b2 ON b2.id=sp.bot_id
                        WHERE b2.name=%s AND b2.method=%s AND sp.status='closed'
                    """, (b[0], method))
                    gp, gl = cur.fetchone()
                    pf = float(gp)/float(gl)
                    score = 0.40*total + 0.30*wr + 0.20*pf + 0.10*(closed/10)
                    scored.append((score, b))
                ranked = [x[1] for x in sorted(scored, key=lambda x: x[0], reverse=True)[:5]]

            top_names = [b[0] for b in ranked]
            if not top_names:
                print(f'⚠️ No bots for {prefix} {rank_type.upper()}')
                continue

            # Bots summary
            bots_file = f'reports/TOP5_{prefix}_{rank_type.upper()}_BOTS.csv'
            with open(bots_file, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['name','trigger_pct','window_sec','hold_sec','closed','win_rate','avg_pnl','total_pnl','median_pnl','std_dev'])
                for b in ranked:
                    closed = int(b[6] or 0)
                    wins_b = int(b[13] or 0)
                    wr = round(wins_b/closed*100,1) if closed else 0
                    w.writerow([b[0], b[2], b[3], b[4], closed, wr,
                               round(float(b[7] or 0),3), round(float(b[8] or 0),4),
                               round(float(b[11] or 0),3), round(float(b[12] or 0),3)])
            print(f'✅ {bots_file}')

            # All trades for top 5
            cur.execute("""
                SELECT b.name, sp.coin,
                    sp.entry_price, sp.exit_price, sp.pnl_pct, sp.pnl_usdt,
                    sp.hold_seconds, sp.exit_reason,
                    sp.trigger_jump_pct, sp.trigger_window_sec,
                    sp.btc_regime, sp.btc_24h_change_pct, sp.btc_dominance,
                    sp.market_age_days, sp.entry_time, sp.exit_time,
                    sp.max_profit_seen, sp.max_loss_seen
                FROM scalper_positions sp JOIN bots b ON b.id=sp.bot_id
                WHERE b.name=ANY(%s) AND b.method=%s AND sp.status='closed'
                ORDER BY b.name, sp.pnl_usdt DESC
            """, (top_names, method))

            trade_rows = cur.fetchall()
            trades_file = f'reports/TOP5_{prefix}_{rank_type.upper()}_TRADES.csv'
            with open(trades_file, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['bot','coin','entry_price','exit_price','pnl_pct','pnl_usdt',
                           'hold_sec','exit_reason','trigger_jump','trigger_window',
                           'btc_regime','btc_24h_change','btc_dominance',
                           'market_age_days','entry_time','exit_time',
                           'max_profit_seen','max_loss_seen'])
                for r in trade_rows:
                    w.writerow([round(float(x),6) if isinstance(x,(int,float)) and x is not None else x for x in r])
            print(f'✅ {trades_file} ({len(trade_rows)} trades)')

if __name__ == '__main__':
    run()
