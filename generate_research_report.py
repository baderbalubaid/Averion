"""
generate_research_report.py
Full research report for all methods — share with AI assistants
"""
import sys, json
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime
db.init_pool()

methods_desc = {
    'E1':'RSI Oversold + VWAP Drop + ATR Spike + Bounce',
    'E2':'Bollinger Band Squeeze Breakout',
    'E3':'Volume Spike + Narrow Range Candle',
    'E4':'SMA Pullback Entry',
    'E5':'Multi-Timeframe EMA Pullback',
    'E6':'Z-Score Mean Reversion',
    'E7':'Volatility Squeeze Breakout',
    'E8':'VWAP + Swing Structure',
    'E9':'Consecutive Red Candles + Volume',
    'E10':'Pure Price Drop',
    'E11':'QFL Base Bounce',
    'E12':'Support/Resistance Reclaim',
    'E13':'EMA Cross + RSI',
    'E14':'StochRSI Oversold + Trend',
    'E15':'OBV Divergence + RSI',
    'E16':'RSI Divergence',
    'E17':'Liquidity Sweep',
    'E18':'High ADX Trend Pullback',
    'E18b':'Low ADX Range Bounce',
    'E19':'Fibonacci Retracement',
    'E20':'VPOC Volume Profile',
    'E21':'Fair Value Gap',
    'E22':'Candlestick Patterns',
    'E23':'Relative Strength vs BTC',
    'E24':'RSI + SMA Pullback',
    'E25':'Supertrend + RSI',
    'E26':'Ichimoku Cloud',
    'E27':'MACD Histogram Reversal',
    'E28':'Keltner Channel Mean Reversion',
    'E29':'Donchian Breakout Pullback',
    'E30':'Hurst Exponent Mean Reversion',
    'E31':'Kalman Filter Deviation',
    'E32':'Session Killzone Sweep',
    'E33':'Williams %R Reversal',
    'E34':'Choppiness Index Exhaustion',
    'E35':'Fisher Transform Reversal',
    'E36':'ALMA Deviation Entry',
    'E37':'BTC Regime Filter',
    'E38':'Relative Volume Breakout',
    'E39':'MFI Oversold Bounce',
    'E40':'Wick Capitulation',
    'E41':'TTM Squeeze Fakeout',
    'E42':'Chaikin Money Flow Divergence',
    'E43':'QQE Momentum',
    'E44':'Multi-Signal Score Bot',
    'E45':'Ensemble Best Methods',
    'E46':'CVD Approximation',
    'E47':'ATR Expansion Breakout',
    'E48':'Volume Before Price (Pump)',
    'E49':'Relative Strength Explosion (Pump)',
    'E50':'Compression Breakout (Pump)',
    'E51':'Top Gainers Pullback (Pump)',
    'E52':'Wyckoff Flatline Breakout (Pump)',
    'E53':'Volatility Expansion Chain (Pump)',
    'E54':'Failed Breakdown Reversal (Pump)',
    'E55':'Relative Volume Leaderboard (Pump)',
    'E56':'Smart Money Footprint (Pump)',
    'E57':'Consensus Pump Engine (Pump)',
    'E58':'WebSocket Momentum Scalper',
    'E59':'Volume Acceleration',
    'E60':'Consecutive Higher Lows',
    'E61':'Sudden Ranking Change',
    'E62':'Multi-Timeframe Strength',
    'E63':'Leader-Laggard Rotation',
    'E64':'False Pump Detector',
    'E65':'Pump Probability Engine',
    'E66':'Bot Consensus Explosion',
    'BM_SIMPLE':'Benchmark: Simple Drop Buy',
    'BM_STATIC':'Benchmark: Fixed Spacing',
    'BM_RANDOM':'Benchmark: Random Entry',
    'BM_HOLD':'Benchmark: Buy and Hold',
}

def run():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    with db.get_db() as conn:
        cur = conn.cursor()

        # ── PLATFORM OVERVIEW ──
        cur.execute("SELECT COUNT(*) FROM bots WHERE is_research=TRUE")
        total_bots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT method) FROM bots WHERE is_research=TRUE")
        total_methods = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM positions WHERE status='open'")
        open_pos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM positions WHERE status='closed'")
        closed_pos = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(ROUND(SUM(total_sold_usdt - total_invested)::numeric,2),0) FROM positions WHERE status='closed'")
        total_pnl = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM scalper_positions WHERE status='closed'")
        scalper_closed = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(ROUND(SUM(pnl_usdt)::numeric,2),0) FROM scalper_positions WHERE status='closed'")
        scalper_pnl = cur.fetchone()[0]

        md = f'# Averion Research Report — Full Method Analysis\n\n'
        md += f'> Generated: {now} · Paper trading · MEXC Exchange · {total_bots} bots · {total_methods} methods\n\n'
        md += '---\n\n'
        md += '> ⚠️ **DATA WARNING:** Early-stage paper trading data (~8-12 hours). '
        md += 'Most methods have <30 trades. Results are **not statistically significant** yet. '
        md += 'Use for directional guidance only. Data collection started: 2026-06-10.\n\n'
        md += '---\n\n'

        # Platform overview
        md += '## Platform Overview\n\n'
        md += '| Metric | Value |\n|--------|-------|\n'
        md += f'| Research Bots | {total_bots} |\n'
        md += f'| Methods | {total_methods} |\n'
        md += f'| Open DCA Positions | {open_pos:,} |\n'
        md += f'| Closed DCA Trades | {closed_pos:,} |\n'
        md += f'| DCA Total P&L | ${total_pnl:,} |\n'
        md += f'| Closed Scalper Trades | {scalper_closed:,} |\n'
        md += f'| Scalper Total P&L | ${scalper_pnl} |\n\n'

        # Architecture notes
        md += '## Architecture Notes\n\n'
        md += '- **Exchange:** MEXC Paper trading\n'
        md += '- **Base order:** $100 per trade\n'
        md += '- **TP/DCA/Trail:** Dynamic per coin category (calculated from ATR + OHLCV)\n'
        md += '- **Categories:** mega (>$100B) · large ($10B-$100B) · mid ($1B-$10B) · small ($100M-$1B) · micro (<$100M)\n'
        md += '- **TP guard:** Min 0.5% profit before trailing fires · direct TP if gap < 1%\n'
        md += '- **RARS formula:** Score = WR^0.30 × AP^0.20 × RS^0.15 × DD^0.35\n'
        md += '- **Eligibility:** <30 trades = NOT ELIGIBLE · 30-99 = PROVISIONAL · 100+ = ELIGIBLE\n\n'

        # ── RARS LEADERBOARD ──
        md += '## RARS Champion Leaderboard\n\n'
        md += '| Rank | Method | RARS | Status | Trades | Win% | Avg P&L | Avg DCA | Hold |\n'
        md += '|------|--------|------|--------|--------|------|---------|---------|------|\n'

        cur.execute("""
            SELECT b.method,
                COUNT(*) as trades,
                COUNT(*) FILTER (WHERE p.total_sold_usdt > p.total_invested) as wins,
                ROUND(AVG(p.total_sold_usdt - p.total_invested)::numeric,2) as avg_pnl,
                ROUND(AVG(p.dca_count)::numeric,2) as avg_dca,
                ROUND(AVG(EXTRACT(EPOCH FROM (p.closed_at-p.opened_at))/3600)::numeric,1) as avg_hold
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE p.status='closed' AND b.is_research=TRUE
            GROUP BY b.method HAVING COUNT(*) >= 3
            ORDER BY avg_pnl DESC
        """)
        rars_rows = cur.fetchall()

        # Calculate simple RARS
        import numpy as np
        raw = []
        for r in rars_rows:
            method, trades, wins, avg_pnl, avg_dca, avg_hold = r
            wr = wins/trades if trades > 0 else 0
            rs_raw = 1/(float(avg_hold or 1)+1)
            dd = max(0.01, 1 - float(avg_dca or 0)*0.07)
            raw.append({'method':method,'trades':trades,'wr':wr,'avg_pnl':float(avg_pnl or 0),'rs_raw':rs_raw,'dd':dd,'avg_dca':avg_dca,'avg_hold':avg_hold})

        if raw:
            ap_vals = [r['avg_pnl'] for r in raw]
            rs_vals = [r['rs_raw'] for r in raw]
            ap_min,ap_max = min(ap_vals),max(ap_vals)
            rs_min,rs_max = min(rs_vals),max(rs_vals)

            for i, r in enumerate(raw):
                wr_n = max(r['wr'], 0.01)
                ap_n = max((r['avg_pnl']-ap_min)/(ap_max-ap_min+1e-9), 0.01)
                rs_n = max((r['rs_raw']-rs_min)/(rs_max-rs_min+1e-9), 0.01)
                dd_n = max(r['dd'], 0.01)
                rars = round((wr_n**0.30)*(ap_n**0.20)*(rs_n**0.15)*(dd_n**0.35)*100, 2)
                if r['trades'] < 30: status = 'NOT_ELIGIBLE'; rars = 0
                elif r['trades'] < 100: status = 'PROVISIONAL'
                else: status = 'ELIGIBLE'
                raw[i]['rars'] = rars
                raw[i]['status'] = status

            raw.sort(key=lambda x: -x['rars'])
            for i, r in enumerate(raw, 1):
                wr_pct = round(r['wr']*100, 1)
                md += f'| {i} | **{r["method"]}** | {r["rars"]} | {r["status"]} | {r["trades"]} | {wr_pct}% | ${r["avg_pnl"]} | {r["avg_dca"]} | {r["avg_hold"]}h |\n'
        md += '\n---\n\n'

        # ── PER METHOD DETAIL ──
        cur.execute("""
            SELECT DISTINCT method FROM bots WHERE is_research=TRUE
            ORDER BY method
        """)
        all_methods = [r[0] for r in cur.fetchall()]

        md += '## Method-by-Method Analysis\n\n'

        for method in sorted(all_methods, key=lambda x: (int(''.join(filter(str.isdigit,x)) or 0), x)):
            desc = methods_desc.get(method, '')
            md += f'### {method} — {desc}\n\n'

            # Get bots + params + performance in one table
            cur.execute("""
                SELECT b.name, b.bot_params::text,
                       COUNT(*) FILTER (WHERE p.status='closed') as closed,
                       COUNT(*) FILTER (WHERE p.status='closed' AND p.total_sold_usdt > p.total_invested) as wins,
                       ROUND(AVG(p.total_sold_usdt - p.total_invested) FILTER (WHERE p.status='closed')::numeric,2) as avg_pnl,
                       ROUND(SUM(p.total_sold_usdt - p.total_invested) FILTER (WHERE p.status='closed')::numeric,2) as total_pnl,
                       ROUND(AVG(p.dca_count) FILTER (WHERE p.status='closed')::numeric,2) as avg_dca,
                       ROUND(AVG(EXTRACT(EPOCH FROM (p.closed_at-p.opened_at))/3600) FILTER (WHERE p.status='closed')::numeric,1) as avg_hold,
                       COUNT(*) FILTER (WHERE p.status='open') as open_now
                FROM bots b LEFT JOIN positions p ON p.bot_id=b.id
                WHERE b.method=%s AND b.is_research=TRUE
                GROUP BY b.name, b.bot_params
                ORDER BY avg_pnl DESC NULLS LAST
            """, (method,))
            bot_rows = cur.fetchall()

            if not bot_rows:
                md += '_No data yet_\n\n'
                continue

            # Get param keys from first bot with params
            param_keys = []
            for row in bot_rows:
                p = json.loads(row[1]) if row[1] and row[1] != '{}' else {}
                if p:
                    param_keys = list(p.keys())
                    break

            # Combined table: params + performance
            headers = ['Bot'] + [k.replace('_',' ').title() for k in param_keys] + ['Closed','Win%','Avg P&L','Total P&L','Avg DCA','Hold','Open']
            md += '| ' + ' | '.join(headers) + ' |\n'
            md += '|' + '|'.join(['---']*len(headers)) + '|\n'

            total_closed = total_wins = 0
            total_pnl_m = 0

            for row in bot_rows:
                name, params_raw, closed_b, wins_b, avg_b, total_b, dca_b, hold_b, open_b = row
                p = json.loads(params_raw) if params_raw and params_raw != '{}' else {}
                param_vals = [str(p.get(k,'-')) for k in param_keys]
                wr = round(wins_b/closed_b*100,1) if closed_b else 0
                total_closed += closed_b or 0
                total_wins += wins_b or 0
                total_pnl_m += float(total_b or 0)
                avg_b_str = f'${avg_b}' if avg_b is not None else '—'
                total_b_str = f'${total_b}' if total_b is not None else '—'
                dca_b_str = str(dca_b) if dca_b is not None else '—'
                hold_b_str = f'{hold_b}h' if hold_b is not None else '—'
                md += f'| {name} | ' + ' | '.join(param_vals) + f' | {closed_b} | {wr}% | {avg_b_str} | {total_b_str} | {dca_b_str} | {hold_b_str} | {open_b} |\n'

            # Method summary row
            overall_wr = round(total_wins/total_closed*100,1) if total_closed else 0
            md += f'\n**{method} Summary:** {total_closed} closed · {overall_wr}% win rate · ${round(total_pnl_m,2)} total P&L\n\n'

        # ── E58 SCALPER SECTION ──
        md += '---\n\n## E58 WebSocket Scalper Results\n\n'
        md += '> Separate architecture — detects price jumps via WebSocket, exits after fixed timer\n\n'

        cur.execute("""
            SELECT b.name,
                   (b.bot_params->>'trigger_pct')::numeric as trigger,
                   (b.bot_params->>'window_sec')::numeric as window,
                   (b.bot_params->>'hold_sec')::numeric as hold,
                   COALESCE(b.bot_params->>'stop_loss_pct','off') as sl,
                   COUNT(*) as trades,
                   COUNT(*) FILTER (WHERE s.pnl_pct > 0) as wins,
                   ROUND(AVG(s.pnl_pct)::numeric,3) as avg_pnl,
                   ROUND(MAX(s.pnl_pct)::numeric,2) as best,
                   ROUND(MIN(s.pnl_pct)::numeric,2) as worst,
                   ROUND(SUM(s.pnl_usdt)::numeric,2) as total_pnl
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            WHERE s.status='closed'
            GROUP BY b.name, b.bot_params
            ORDER BY avg_pnl DESC
        """)
        scalper_rows = cur.fetchall()

        md += '| Bot | Trigger% | Window | Hold | SL% | Trades | Win% | Avg PnL% | Best | Worst | Total$ |\n'
        md += '|-----|----------|--------|------|-----|--------|------|----------|------|-------|--------|\n'
        for r in scalper_rows:
            wr = round(r[6]/r[5]*100,1) if r[5] else 0
            md += f'| {r[0]} | {r[1]}% | {r[2]}s | {r[3]}s | {r[4]} | {r[5]} | {wr}% | {r[7]}% | {r[8]}% | {r[9]}% | ${r[10]} |\n'
        md += '\n'

        # ── COIN CATEGORY PERFORMANCE ──
        md += '## Performance by Coin Category\n\n'
        cur.execute("""
            SELECT p.category, COUNT(*) as trades,
                   COUNT(*) FILTER (WHERE p.total_sold_usdt > p.total_invested) as wins,
                   ROUND(AVG(p.total_sold_usdt - p.total_invested)::numeric,2) as avg_pnl,
                   ROUND(AVG(p.dca_count)::numeric,2) as avg_dca,
                   ROUND(AVG(EXTRACT(EPOCH FROM (p.closed_at-p.opened_at))/3600)::numeric,1) as avg_hold
            FROM positions p WHERE p.status='closed'
            GROUP BY p.category ORDER BY avg_pnl DESC
        """)
        md += '| Category | Trades | Win% | Avg P&L | Avg DCA | Hold |\n'
        md += '|----------|--------|------|---------|---------|------|\n'
        for r in cur.fetchall():
            wr = round(r[2]/r[1]*100,1) if r[1] else 0
            md += f'| {r[0]} | {r[1]} | {wr}% | ${r[3]} | {r[4]} | {r[5]}h |\n'
        md += '\n'

        # ── 1. MARKET CAP BREAKDOWN PER TOP METHODS ──
        md += '## Market Cap Performance by Top Methods\n\n'
        md += '> Which coin sizes respond best to each method\n\n'
        cur.execute("""
            SELECT b.method, p.category,
                COUNT(*) as trades,
                COUNT(*) FILTER (WHERE p.total_sold_usdt > p.total_invested) as wins,
                ROUND(AVG(p.total_sold_usdt - p.total_invested)::numeric,2) as avg_pnl,
                ROUND(AVG(p.dca_count)::numeric,2) as avg_dca
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE p.status='closed' AND b.is_research=TRUE
            AND b.method IN (
                SELECT b2.method FROM positions p2
                JOIN bots b2 ON b2.id=p2.bot_id
                WHERE p2.status='closed' AND b2.is_research=TRUE
                GROUP BY b2.method ORDER BY COUNT(*) DESC LIMIT 15
            )
            GROUP BY b.method, p.category
            ORDER BY b.method, avg_pnl DESC
        """)
        md += '| Method | Category | Trades | Win% | Avg P&L | Avg DCA |\n'
        md += '|--------|----------|--------|------|---------|---------|\n'
        for r in cur.fetchall():
            wr = round(r[3]/r[2]*100,1) if r[2] else 0
            md += f'| {r[0]} | {r[1]} | {r[2]} | {wr}% | ${r[3]} | ${r[4]} | {r[5]} |\n'
        md += '\n'

        # ── 2. BEST PARAM PER METHOD ──
        md += '## Best Performing Bot Per Method\n\n'
        cur.execute("""
            SELECT DISTINCT ON (b.method)
                b.method, b.name, b.bot_params::text,
                COUNT(*) FILTER (WHERE p.status='closed') as closed,
                ROUND(AVG(p.total_sold_usdt - p.total_invested) FILTER (WHERE p.status='closed')::numeric,2) as avg_pnl
            FROM bots b LEFT JOIN positions p ON p.bot_id=b.id
            WHERE b.is_research=TRUE
            GROUP BY b.method, b.name, b.bot_params
            HAVING COUNT(*) FILTER (WHERE p.status='closed') >= 3
            ORDER BY b.method, avg_pnl DESC NULLS LAST
        """)
        import json as _json
        md += '| Method | Best Bot | Closed | Avg P&L | Winning Params |\n'
        md += '|--------|----------|--------|---------|----------------|\n'
        for r in cur.fetchall():
            try:
                params = _json.loads(r[2]) if r[2] else {}
                param_str = ' · '.join(f'{k}={v}' for k,v in params.items())
            except:
                param_str = '—'
            md += f'| {r[0]} | {r[1]} | {r[3]} | ${r[4]} | {param_str} |\n'
        md += '\n'

        # ── 3. METHODS WITH ZERO ACTIVITY ──
        md += '## Methods With Zero Activity\n\n'
        md += '> These may be too strict or wrong market conditions\n\n'
        cur.execute("""
            SELECT b.method, COUNT(DISTINCT b.id) as bots
            FROM bots b
            WHERE b.is_research=TRUE
            AND NOT EXISTS (SELECT 1 FROM positions p WHERE p.bot_id=b.id)
            GROUP BY b.method ORDER BY b.method
        """)
        zero_rows = cur.fetchall()
        if zero_rows:
            md += '| Method | Bots | Recommendation |\n'
            md += '|--------|------|----------------|\n'
            for r in zero_rows:
                md += f'| {r[0]} | {r[1]} | No trades · check signal conditions · may need different market regime |\n'
        else:
            md += '_All methods have at least some activity_ \n'
        md += '\n'

        # ── 4. TIME-IN-TRADE VS DRAWDOWN ──
        md += '## Capital Efficiency — Hold Time vs Drawdown\n\n'
        md += '> Methods that exit quickly with low DCA = better capital efficiency\n\n'
        cur.execute("""
            SELECT b.method,
                ROUND(AVG(EXTRACT(EPOCH FROM (p.closed_at-p.opened_at))/3600)::numeric,1) as avg_hold_hrs,
                ROUND(MAX(EXTRACT(EPOCH FROM (p.closed_at-p.opened_at))/3600)::numeric,1) as max_hold_hrs,
                ROUND(AVG(p.dca_count)::numeric,2) as avg_dca,
                ROUND(MAX(p.dca_count)::numeric,0) as max_dca,
                COUNT(*) as trades
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE p.status='closed' AND b.is_research=TRUE
            GROUP BY b.method HAVING COUNT(*) >= 5
            ORDER BY avg_hold_hrs ASC
        """)
        md += '| Method | Avg Hold | Max Hold | Avg DCA | Max DCA | Trades |\n'
        md += '|--------|----------|----------|---------|---------|--------|\n'
        for r in cur.fetchall():
            md += f'| {r[0]} | {r[1]}h | {r[2]}h | {r[3]} | {r[4]} | {r[5]} |\n'
        md += '\n'

        # ── 5. DATA COLLECTION DURATION ──
        cur.execute("SELECT MIN(opened_at), MAX(opened_at) FROM positions WHERE is_research=TRUE")
        time_row = cur.fetchone()
        if time_row and time_row[0] and time_row[1]:
            duration = time_row[1] - time_row[0]
            hours = round(duration.total_seconds()/3600, 1)
            md += f'## Data Collection Duration\n\n'
            md += f'| Metric | Value |\n|--------|-------|\n'
            md += f'| First position opened | {time_row[0].strftime("%Y-%m-%d %H:%M")} |\n'
            md += f'| Latest position opened | {time_row[1].strftime("%Y-%m-%d %H:%M")} |\n'
            md += f'| Data collection window | {hours} hours ({round(hours/24,1)} days) |\n'
            md += f'| Statistical confidence | {"LOW - need 100+ trades per method" if hours < 48 else "MEDIUM - growing" if hours < 168 else "HIGH - good sample"} |\n\n'

        # ── 6. SCALPER ACTIVITY SUMMARY ──
        md += '## E58 Scalper — Activity Summary\n\n'
        cur.execute("""
            SELECT b.name,
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE s.status='open') as open_now,
                COUNT(*) FILTER (WHERE s.exit_reason='timer') as timer_exits,
                COUNT(*) FILTER (WHERE s.exit_reason='stop_loss') as sl_exits,
                ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric,3) as avg_pnl,
                ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric,2) as total_pnl,
                ROUND(MAX(s.max_profit_seen)::numeric,2) as best_peak,
                ROUND(MIN(s.max_loss_seen)::numeric,2) as worst_dip
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            GROUP BY b.name ORDER BY avg_pnl DESC NULLS LAST
        """)
        md += '| Bot | Total | Open | Timer | SL | Avg PnL% | Total$ | Best Peak | Worst Dip |\n'
        md += '|-----|-------|------|-------|----|----------|--------|-----------|-----------|\n'
        for r in cur.fetchall():
            md += f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}% | ${r[6]} | {r[7]}% | {r[8]}% |\n'
        md += '\n'

        # ── QUESTIONS FOR AI ──
        md += '## Questions for AI Analysis\n\n'
        md += '1. Which DCA methods show most consistent edge? Which to promote as champion?\n'
        md += '2. Which scalper parameters show best risk/reward? Best trigger% and hold time?\n'
        md += '3. Are there patterns in which coin categories respond best to which methods?\n'
        md += '4. What new parameter variations should we test?\n'
        md += '5. Any signs of overfitting, luck, or data quality issues?\n'
        md += '6. Which methods should we drop or expand based on data?\n'
        md += '7. For pump detection — which precursor signals show most promise?\n'
        md += '8. Is there a consensus signal pattern across multiple methods on same coin?\n'

    path = '/home/averion/Averion/docs/RESEARCH_REPORT_FULL.md'
    with open(path, 'w') as f:
        f.write(md)
    print(f'✅ Full research report generated!')
    print(f'   File: {path}')

if __name__ == '__main__':
    run()
