"""
generate_dca_report.py
DCA Research Report — E1-E66 method summaries + regime analysis
"""
import sys, csv
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv; load_dotenv()
import database as db
from datetime import datetime
db.init_pool()

METHODS_DESC = {
    'E1':'RSI Oversold + VWAP Drop + ATR Spike',
    'E2':'Bollinger Band Squeeze Breakout',
    'E3':'Volume Spike + Narrow Range',
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
    'E18':'ADX Trend Pullback',
    'E18b':'Low ADX Ranging Market',
    'E19':'Fibonacci Retracement',
    'E20':'VPOC Volume Profile',
    'E21':'Fair Value Gap',
    'E22':'Hammer/Engulfing at Support',
    'E23':'BTC Relative Strength',
    'E24':'MACD + RSI Confluence',
    'E25':'Pivot Point Bounce',
    'E26':'Ichimoku Cloud Support',
    'E27':'MACD Histogram Reversal',
    'E28':'Williams %R Oversold',
    'E29':'CCI Oversold Reversal',
    'E30':'Elder Ray Bear Power',
    'E31':'Kalman Filter Deviation',
    'E32':'Session Killzone Sweep',
    'E33':'VWAP Standard Deviation Band',
    'E34':'Heikin-Ashi Reversal',
    'E35':'Supertrend Bounce',
    'E36':'Parabolic SAR Flip',
    'E37':'Donchian Channel Breakout',
    'E38':'Keltner Channel Mean Reversion',
    'E39':'Linear Regression Deviation',
    'E40':'Hull Moving Average Cross',
    'E41':'Chande Momentum Oscillator',
    'E42':'Detrended Price Oscillator',
    'E43':'Price Channel Breakout',
    'E44':'Mass Index Reversal',
    'E45':'Aroon Indicator Cross',
    'E46':'Ultimate Oscillator Oversold',
    'E47':'ATR Expansion Breakout',
    'E48':'Vortex Indicator Cross',
    'E49':'TRIX Signal Cross',
    'E50':'Klinger Volume Oscillator',
    'E51':'Force Index Reversal',
    'E52':'Ease of Movement',
    'E53':'Negative Volume Index',
    'E54':'Support Reclaim + Breakdown',
    'E55':'Waddah Attar Explosion',
    'E56':'Squeeze Momentum',
    'E57':'Laguerre RSI',
    'E59':'Adaptive RSI',
    'E60':'Market Structure Break',
    'E61':'Supply/Demand Zone',
    'E62':'Order Block Entry',
    'E63':'Breaker Block',
    'E64':'Imbalance Fill',
    'E65':'Premium/Discount Zone',
    'E66':'Bot Consensus Explosion',
}

def run():
    now = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    with db.get_db() as conn:
        cur = conn.cursor()

        # Overall stats
        cur.execute("""
            SELECT COUNT(*) FROM positions p
            JOIN bots b ON b.id=p.bot_id
            WHERE b.is_research=TRUE AND p.status='closed' AND p.closed_at IS NOT NULL
        """)
        total_closed = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM positions p
            JOIN bots b ON b.id=p.bot_id
            WHERE b.is_research=TRUE AND p.status='open'
        """)
        total_open = cur.fetchone()[0]

        cur.execute("""
            SELECT COALESCE(ROUND(SUM((p.total_sold_usdt - p.total_invested))::numeric,2),0)
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE b.is_research=TRUE AND p.status='closed' AND p.closed_at IS NOT NULL
        """)
        total_pnl = cur.fetchone()[0]

        # Regime distribution
        cur.execute("""
            SELECT regime_at_open, COUNT(*)
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE b.is_research=TRUE AND p.status='closed' AND p.closed_at IS NOT NULL
            GROUP BY regime_at_open
        """)
        regimes = {r[0] or 'unknown': r[1] for r in cur.fetchall()}

        # Per method aggregated stats
        cur.execute("""
            SELECT
                b.method,
                COUNT(DISTINCT b.id) as bots,
                COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) as trades,
                COUNT(p.id) FILTER (WHERE p.status='open') as open_now,
                ROUND(AVG(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,3) as avg_pnl,
                ROUND(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as total_pnl,
                ROUND(MAX(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as best,
                ROUND(MIN(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as worst,
                ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,3) as median_pnl,
                ROUND(STDDEV(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,3) as std_dev,
                COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100) > 0) as wins,
                ROUND(AVG(EXTRACT(EPOCH FROM (p.closed_at - p.opened_at))/3600) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,1) as avg_hold_hrs
            FROM bots b
            LEFT JOIN positions p ON p.bot_id=b.id
            WHERE b.is_research=TRUE AND b.method NOT IN ('E58','E58v2')
            AND (b.is_template=FALSE OR b.is_template IS NULL)
            GROUP BY b.method
            HAVING COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) > 0
            ORDER BY total_pnl DESC NULLS LAST
        """)
        methods = cur.fetchall()

        # Regime per method
        cur.execute("""
            SELECT b.method, p.regime_at_open,
                COUNT(*) as trades,
                ROUND(AVG(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100))::numeric,3) as avg_pnl,
                COUNT(*) FILTER (WHERE ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)>0)*100/COUNT(*) as win_rate
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE b.is_research=TRUE AND p.status='closed' AND p.closed_at IS NOT NULL
            AND p.regime_at_open IS NOT NULL
            GROUP BY b.method, p.regime_at_open
            ORDER BY b.method, p.regime_at_open
        """)
        regime_data = {}
        for r in cur.fetchall():
            m = r[0]
            if m not in regime_data:
                regime_data[m] = {}
            regime_data[m][r[1] or 'unknown'] = {'trades':r[2],'avg_pnl':float(r[3] or 0),'win_rate':r[4]}

    # Build markdown
    md = f'# Averion DCA Research Report\n\n'
    md += f'> Generated: {now} · Paper trading · MEXC\n\n'
    md += '> ⚠️ All trades are paper (simulated). Use for directional research only.\n\n'
    md += '---\n\n'

    md += '## Overview\n\n'
    md += f'| Metric | Value |\n|--------|-------|\n'
    md += f'| Total Closed Trades | {total_closed:,} |\n'
    md += f'| Open Positions | {total_open:,} |\n'
    md += f'| Total P&L | ${total_pnl} |\n'
    md += f'| Active Methods | {len(methods)} |\n\n'

    md += '## Market Regime Coverage\n\n'
    md += '> ⚠️ Regime analysis is preliminary. Conclusions require multiple regime samples.\n\n'
    md += '| Regime | Trades |\n|--------|--------|\n'
    for regime, count in sorted(regimes.items()):
        status = '✅' if count >= 30 else '⚠️ insufficient'
        md += f'| {regime} | {count:,} {status} |\n'
    md += '\n---\n\n'

    md += '## Method Rankings\n\n'
    md += '| Rank | Method | Description | Bots | Trades | Win% | Avg P&L% | Median P&L% | Std Dev | Total P&L | Avg Hold |\n'
    md += '|------|--------|-------------|------|--------|------|----------|-------------|---------|-----------|----------|\n'

    for i, m in enumerate(methods):
        method, bots, trades, open_now, avg_pnl, total_pnl_m, best, worst, median, std, wins, avg_hold = m
        win_rate = round(wins/trades*100,1) if trades else 0
        desc = METHODS_DESC.get(method, '—')
        avg_pnl = float(avg_pnl or 0)
        median = float(median or 0)
        std = float(std or 0)
        total_pnl_m = float(total_pnl_m or 0)
        avg_hold = float(avg_hold or 0)
        md += f'| {i+1} | **{method}** | {desc} | {bots} | {trades:,} | {win_rate}% | {avg_pnl:+.3f}% | {median:+.3f}% | {std:.3f} | ${total_pnl_m:+.2f} | {avg_hold:.1f}h |\n'

    md += '\n---\n\n'
    md += '## Method Details\n\n'

    for m in methods:
        method, bots, trades, open_now, avg_pnl, total_pnl_m, best, worst, median, std, wins, avg_hold = m
        win_rate = round(wins/trades*100,1) if trades else 0
        profit_factor = 0
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    COALESCE(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE (p.total_sold_usdt - p.total_invested)>0),0),
                    COALESCE(ABS(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE (p.total_sold_usdt - p.total_invested)<0)),0.001)
                FROM positions p JOIN bots b ON b.id=p.bot_id
                WHERE b.method=%s AND b.is_research=TRUE AND p.status='closed' AND p.closed_at IS NOT NULL
            """, (method,))
            gp, gl = cur.fetchone()
            profit_factor = round(float(gp)/float(gl), 2)

            # Max streak
            cur.execute("""
                SELECT (total_sold_usdt - total_invested) > 0 as win FROM positions p
                JOIN bots b ON b.id=p.bot_id
                WHERE b.method=%s AND b.is_research=TRUE AND p.status='closed' AND p.closed_at IS NOT NULL
                ORDER BY p.closed_at ASC
            """, (method,))
            results = [r[0] for r in cur.fetchall()]

        max_win_streak = max_loss_streak = cur_win = cur_loss = 0
        for r in results:
            if r:
                cur_win += 1; cur_loss = 0
            else:
                cur_loss += 1; cur_win = 0
            max_win_streak = max(max_win_streak, cur_win)
            max_loss_streak = max(max_loss_streak, cur_loss)

        md += f'### {method} — {METHODS_DESC.get(method,"")}\n\n'
        md += f'**Summary**\n\n'
        md += f'| Metric | Value |\n|--------|-------|\n'
        md += f'| Bots | {bots} |\n'
        md += f'| Closed Trades | {trades:,} |\n'
        md += f'| Open Now | {open_now} |\n'
        md += f'| Win Rate | {win_rate}% |\n'
        md += f'| Avg P&L | {float(avg_pnl or 0):+.3f}% |\n'
        md += f'| Median P&L | {float(median or 0):+.3f}% |\n'
        md += f'| Std Deviation | {float(std or 0):.3f} |\n'
        md += f'| Best Trade | {float(best or 0):+.2f}% |\n'
        md += f'| Worst Trade | {float(worst or 0):+.2f}% |\n'
        md += f'| Total P&L | ${float(total_pnl_m or 0):+.2f} |\n'
        md += f'| Profit Factor | {profit_factor} |\n'
        md += f'| Avg Hold | {float(avg_hold or 0):.1f}h |\n'
        md += f'| Max Win Streak | {max_win_streak} |\n'
        md += f'| Max Loss Streak | {max_loss_streak} |\n\n'

        # Regime breakdown
        if method in regime_data:
            md += f'**Market Regime Breakdown**\n\n'
            md += f'| Regime | Trades | Win% | Avg P&L% |\n|--------|--------|------|----------|\n'
            for regime, stats in sorted(regime_data[method].items()):
                note = '' if stats['trades'] >= 30 else ' ⚠️'
                md += f'| {regime} | {stats["trades"]}{note} | {stats["win_rate"]}% | {stats["avg_pnl"]:+.3f}% |\n'
            md += '\n'
        else:
            md += f'**Market Regime:** No regime data captured yet.\n\n'

        md += '---\n\n'

    with open('reports/RESEARCH_DCA.md', 'w') as f:
        f.write(md)
    print(f'✅ RESEARCH_DCA.md written ({len(methods)} methods)')

    # Generate CSV files
    _generate_dca_csvs(methods)

def _generate_dca_csvs(methods):
    with db.get_db() as conn:
        cur = conn.cursor()

        for rank_type in ['rars', 'score']:
            if rank_type == 'rars':
                # RARS: 35% cap efficiency / 30% drawdown / 20% win rate / 15% profit factor
                cur.execute("""
                    SELECT b.method,
                        COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) as trades,
                        ROUND(AVG(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,3) as avg_pnl,
                        ROUND(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as total_pnl,
                        COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)>0)*100.0/
                            NULLIF(COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL),0) as win_rate,
                        ROUND(MIN(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as max_dd,
                        COALESCE(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND (p.total_sold_usdt - p.total_invested)>0),0) as gross_profit,
                        COALESCE(ABS(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND (p.total_sold_usdt - p.total_invested)<0)),0.001) as gross_loss
                    FROM bots b LEFT JOIN positions p ON p.bot_id=b.id
                    WHERE b.is_research=TRUE AND b.method NOT IN ('E58','E58v2')
                    GROUP BY b.method
                    HAVING COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) >= 30
                    ORDER BY total_pnl DESC
                    LIMIT 5
                """)
            else:
                cur.execute("""
                    SELECT b.method,
                        COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) as trades,
                        ROUND(AVG(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,3) as avg_pnl,
                        ROUND(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as total_pnl,
                        COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)>0)*100.0/
                            NULLIF(COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL),0) as win_rate,
                        ROUND(MIN(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as max_dd,
                        COALESCE(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND (p.total_sold_usdt - p.total_invested)>0),0) as gross_profit,
                        COALESCE(ABS(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND (p.total_sold_usdt - p.total_invested)<0)),0.001) as gross_loss
                    FROM bots b LEFT JOIN positions p ON p.bot_id=b.id
                    WHERE b.is_research=TRUE AND b.method NOT IN ('E58','E58v2')
                    GROUP BY b.method
                    HAVING COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) >= 30
                    ORDER BY (
                        0.40*SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) +
                        0.30*COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)>0)*100.0/NULLIF(COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL),0) +
                        0.20*COALESCE(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND (p.total_sold_usdt - p.total_invested)>0),0)/NULLIF(COALESCE(ABS(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND (p.total_sold_usdt - p.total_invested)<0)),0.001),0) +
                        0.10*COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)
                    ) DESC
                    LIMIT 5
                """)

            top_methods = [r[0] for r in cur.fetchall()]
            if not top_methods:
                print(f'⚠️ No methods with ≥30 trades for DCA {rank_type.upper()}')
                continue

            # Bots summary CSV
            cur.execute("""
                SELECT b.name, b.method, b.bot_params::text,
                    COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL) as trades,
                    ROUND(AVG(((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,3) as avg_pnl,
                    ROUND(SUM((p.total_sold_usdt - p.total_invested)) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL)::numeric,2) as total_pnl,
                    COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL AND ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100)>0)*100.0/
                        NULLIF(COUNT(p.id) FILTER (WHERE p.status='closed' AND p.closed_at IS NOT NULL),0) as win_rate
                FROM bots b LEFT JOIN positions p ON p.bot_id=b.id
                WHERE b.is_research=TRUE AND b.method=ANY(%s)
                GROUP BY b.id, b.name, b.method, b.bot_params
                ORDER BY total_pnl DESC
            """, (top_methods,))

            bot_rows = cur.fetchall()
            bots_file = f'reports/TOP5_DCA_{rank_type.upper()}_BOTS.csv'
            with open(bots_file, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['name','method','params','trades','avg_pnl_pct','total_pnl_usdt','win_rate_pct'])
                for r in bot_rows:
                    w.writerow(r)
            print(f'✅ {bots_file} ({len(bot_rows)} bots)')

            # Trades CSV
            cur.execute("""
                SELECT b.name, b.method, p.coin,
                    p.avg_cost, p.avg_sell_price, ((p.total_sold_usdt - p.total_invested) / NULLIF(p.total_invested, 0) * 100), (p.total_sold_usdt - p.total_invested),
                    p.dca_count, p.total_invested,
                    EXTRACT(EPOCH FROM (p.closed_at - p.opened_at))/3600 as hold_hrs,
                    p.close_reason,
                    p.regime_at_open, p.btc_24h_change_pct, p.btc_dominance,
                    p.market_age_days, p.opened_at, p.closed_at,
                    p.category
                FROM positions p JOIN bots b ON b.id=p.bot_id
                WHERE b.is_research=TRUE AND b.method=ANY(%s)
                AND p.status='closed' AND p.closed_at IS NOT NULL
                ORDER BY b.method, (p.total_sold_usdt - p.total_invested) DESC
            """, (top_methods,))

            trade_rows = cur.fetchall()
            trades_file = f'reports/TOP5_DCA_{rank_type.upper()}_TRADES.csv'
            with open(trades_file, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(['bot','method','coin','avg_cost','exit_price',
                           'pnl_pct','pnl_usdt','dca_count','invested',
                           'hold_hrs','exit_reason','btc_regime','btc_24h_change',
                           'btc_dominance','market_age_days','opened_at','exit_time','category'])
                for r in trade_rows:
                    w.writerow([round(float(x),6) if isinstance(x, (int,float)) else x for x in r])
            print(f'✅ {trades_file} ({len(trade_rows)} trades)')

if __name__ == '__main__':
    run()
