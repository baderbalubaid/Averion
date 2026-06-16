"""
generate_scalper_v2_report.py
E58v2 Velocity Scalper Research Report — all 120 bots ranked
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
            JOIN bots b ON b.id=sp.bot_id WHERE b.method='E58v2' AND sp.status='closed'
        """)
        total_closed = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*) FROM scalper_positions sp
            JOIN bots b ON b.id=sp.bot_id WHERE b.method='E58v2' AND sp.status='open'
        """)
        total_open = cur.fetchone()[0]
        cur.execute("""
            SELECT COALESCE(ROUND(SUM(sp.pnl_usdt)::numeric,2),0)
            FROM scalper_positions sp JOIN bots b ON b.id=sp.bot_id
            WHERE b.method='E58v2' AND sp.status='closed'
        """)
        total_pnl = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*) FILTER (WHERE sp.pnl_pct>0),
                   COUNT(*) FILTER (WHERE sp.pnl_pct<=0)
            FROM scalper_positions sp JOIN bots b ON b.id=sp.bot_id
            WHERE b.method='E58v2' AND sp.status='closed'
        """)
        wins, losses = cur.fetchone()

        cur.execute("""
            SELECT btc_regime, COUNT(*) FROM scalper_positions sp
            JOIN bots b ON b.id=sp.bot_id
            WHERE b.method='E58v2' AND sp.status='closed'
            GROUP BY btc_regime
        """)
        regimes = {r[0] or 'unknown': r[1] for r in cur.fetchall()}

        # All 120 bots
        cur.execute("""
            SELECT b.name,
                (b.bot_params->>'vel_3s')::float as vel_3s,
                (b.bot_params->>'vel_10s')::float as vel_10s,
                (b.bot_params->>'accel_ratio')::float as accel_ratio,
                b.bot_params->>'exit_profile' as exit_profile,
                (b.bot_params->>'max_hold_sec')::int as max_hold_sec,
                (b.bot_params->>'trail_pct')::float as trail_pct,
                (b.bot_params->>'stop_loss_pct')::float as stop_loss_pct,
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
                COUNT(sp.id) FILTER (WHERE sp.status='closed' AND sp.pnl_pct<=0) as bot_losses,
                ROUND(AVG(sp.hold_seconds) FILTER (WHERE sp.status='closed')::numeric,1) as avg_hold
            FROM bots b
            LEFT JOIN scalper_positions sp ON sp.bot_id=b.id
            WHERE b.method='E58v2' AND b.is_research=TRUE
            GROUP BY b.id, b.name, b.bot_params
            ORDER BY total_pnl DESC NULLS LAST
        """)
        bots = cur.fetchall()

    md = f'# Averion E58v2 Velocity Scalper Research Report\n\n'
    md += f'> Generated: {now} · Paper trading · MEXC · Velocity + Acceleration Signal\n\n'
    md += '> ⚠️ All trades are paper (simulated). New method — compare vs E58 legacy.\n\n'
    md += '---\n\n'

    md += '## Overview\n\n'
    md += '| Metric | Value |\n|--------|-------|\n'
    md += f'| Total Bots | 120 |\n'
    md += f'| Closed Trades | {total_closed:,} |\n'
    md += f'| Open Positions | {total_open:,} |\n'
    md += f'| Total P&L | ${total_pnl} |\n'
    md += f'| Win Rate | {round(wins/(wins+losses)*100,1) if wins+losses else 0}% |\n\n'

    md += '## Architecture (vs E58 Legacy)\n\n'
    md += '| Feature | E58 Legacy | E58v2 Velocity |\n|---------|-----------|----------------|\n'
    md += '| Signal | Total jump % | Velocity + Acceleration |\n'
    md += '| Entry timing | After pump | During pump |\n'
    md += '| Pump protection | None | Hard reject guards |\n'
    md += '| Exit | Timer only | Trailing + Stop + Timer |\n\n'

    md += '## Signal Parameters\n\n'
    md += '- **vel_3s:** Minimum % move in 3 seconds\n'
    md += '- **vel_10s:** Minimum % move in 10 seconds\n'
    md += '- **accel_ratio:** How much faster recent vs average momentum\n'
    md += '- **Pump guard:** Reject if +8% in 5s / +40% in 30s / +60% in 60s\n\n'

    md += '## Market Regime Coverage\n\n'
    md += '| Regime | Trades |\n|--------|--------|\n'
    for regime, count in sorted(regimes.items()):
        note = '✅' if count >= 30 else '⚠️'
        md += f'| {regime} | {count:,} {note} |\n'
    md += '\n---\n\n'

    md += '## All 120 Bots Ranked\n\n'
    md += '| Rank | Bot | Vel3s | Vel10s | Accel | Exit | Hold | Closed | Win% | Avg P&L% | Total P&L |\n'
    md += '|------|-----|-------|--------|-------|------|------|--------|------|----------|-----------|\n'

    for i, b in enumerate(bots):
        name = b[0]
        vel3 = float(b[1] or 0)
        vel10 = float(b[2] or 0)
        accel = float(b[3] or 0)
        ep = b[4] or '—'
        hold = int(b[5] or 0)
        closed = int(b[9] or 0)
        avg_pnl = float(b[10] or 0)
        total_pnl_b = float(b[11] or 0)
        wins_b = int(b[16] or 0)
        win_rate = round(wins_b/closed*100,1) if closed else 0
        md += f'| {i+1} | **{name}** | {vel3}% | {vel10}% | {accel} | {ep} | {hold}s | {closed:,} | {win_rate}% | {avg_pnl:+.3f}% | ${total_pnl_b:+.2f} |\n'

    md += '\n---\n\n'
    md += '## Top 10 Bot Details\n\n'

    for b in bots[:10]:
        name = b[0]
        vel3 = float(b[1] or 0)
        vel10 = float(b[2] or 0)
        accel = float(b[3] or 0)
        ep = b[4] or '—'
        hold = int(b[5] or 0)
        trail = float(b[6] or 0)
        sl = float(b[7] or 0)
        closed = int(b[9] or 0)
        avg_pnl = float(b[10] or 0)
        total_pnl_b = float(b[11] or 0)
        best = float(b[12] or 0)
        worst = float(b[13] or 0)
        median = float(b[14] or 0)
        std = float(b[15] or 0)
        wins_b = int(b[16] or 0)
        avg_hold = float(b[18] or 0)
        win_rate = round(wins_b/closed*100,1) if closed else 0

        md += f'### {name}\n\n'
        md += f'| Metric | Value |\n|--------|-------|\n'
        md += f'| Vel 3s | {vel3}% |\n'
        md += f'| Vel 10s | {vel10}% |\n'
        md += f'| Accel Ratio | {accel} |\n'
        md += f'| Exit Profile | {ep} |\n'
        md += f'| Max Hold | {hold}s |\n'
        md += f'| Trail % | {trail}% |\n'
        md += f'| Stop Loss | {sl}% |\n'
        md += f'| Closed Trades | {closed:,} |\n'
        md += f'| Win Rate | {win_rate}% |\n'
        md += f'| Avg P&L | {avg_pnl:+.3f}% |\n'
        md += f'| Median P&L | {median:+.3f}% |\n'
        md += f'| Std Deviation | {std:.3f} |\n'
        md += f'| Best | {best:+.2f}% |\n'
        md += f'| Worst | {worst:+.2f}% |\n'
        md += f'| Total P&L | ${total_pnl_b:+.2f} |\n'
        md += f'| Avg Hold | {avg_hold:.1f}s |\n\n'
        md += '---\n\n'

    with open('reports/RESEARCH_SCALPER_V2.md', 'w') as f:
        f.write(md)
    print(f'✅ RESEARCH_SCALPER_V2.md written ({len(bots)} bots)')

    # Reuse scalper CSV generator
    from generate_scalper_report import _generate_scalper_csvs
    _generate_scalper_csvs(bots, 'E58v2', 'SCALPERV2')

if __name__ == '__main__':
    run()
