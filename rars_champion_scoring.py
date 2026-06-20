"""
rars_champion_scoring.py — Regime-aware, weighted RARS scoring
Replaces print-only rars_scoring.py with real persistence.
LOCKED June 18 2026 via 3-way AI review (Claude+ChatGPT+Gemini).
Old multiplicative formula archived as calculate_legacy_rars(),
kept only for score_legacy reference column, NOT used for champion
selection anymore.
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv('/home/averion/Averion/.env')
import database as db
from datetime import datetime, timedelta, timezone

db.init_pool()

REGIMES = ['bull', 'bear', 'sideways']
WINDOWS = {'30d': 30, '90d': 90, 'lifetime': None}

def get_weights(system_type, regime):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT metric_name, weight FROM rars_weight_config
            WHERE system_type=%s AND regime=%s AND enabled=TRUE
        """, (system_type, regime))
        return {r[0]: float(r[1]) for r in cur.fetchall()}

def window_start(window_key):
    days = WINDOWS[window_key]
    if days is None:
        return None
    return datetime.now(timezone.utc) - timedelta(days=days)

def fetch_dca_trades(regime, win_start):
    with db.get_db() as conn:
        cur = conn.cursor()
        query = """
            SELECT b.name, p.total_invested, p.total_sold_usdt,
                   p.opened_at, p.closed_at, p.dca_count, b.method
            FROM positions p JOIN bots b ON b.id = p.bot_id
            WHERE p.status='closed' AND b.is_research=TRUE
            AND p.btc_regime=%s
        """
        params = [regime]
        if win_start:
            query += " AND p.closed_at >= %s"
            params.append(win_start)
        cur.execute(query, params)
        return cur.fetchall()

def compute_dca_raw_metrics(rows):
    """Group DCA trade rows by bot_name, compute raw (unweighted) metrics."""
    methods = {}
    for bot_name, invested, sold, opened, closed, dca_count, method in rows:
        if bot_name not in methods:
            methods[bot_name] = {'trades': [], 'method': method}
        invested = float(invested or 0)
        sold = float(sold or 0)
        pnl = sold - invested
        hold_hours = 0
        if opened and closed:
            hold_hours = (closed - opened).total_seconds() / 3600
        methods[bot_name]['trades'].append({
            'pnl': pnl, 'invested': invested, 'dca_count': int(dca_count or 0),
            'hold_hours': max(hold_hours, 0.01), 'opened': opened, 'closed': closed,
        })

    raw = {}
    for bot_name, data in methods.items():
        trades = data['trades']
        method = data['method']
        n = len(trades)
        pnls = sorted([t['pnl'] for t in trades], reverse=True)
        wins = [p for p in pnls if p > 0]
        net_profit = sum(pnls)
        win_rate = len(wins) / n if n else 0
        avg_pnl = net_profit / n if n else 0
        avg_hold = sum(t['hold_hours'] for t in trades) / n if n else 0
        recovery_speed_raw = 1 / (avg_hold + 1)
        avg_dca = sum(t['dca_count'] for t in trades) / n if n else 0
        stuck_penalty_raw = avg_dca
        excl_top5 = sum(pnls[5:]) if n > 5 else net_profit
        robustness = round(excl_top5 / net_profit * 100, 1) if net_profit > 0 else 0
        active_days = len(set(t['closed'].date() for t in trades if t['closed']))

        raw[bot_name] = {
            'method': method, 'trade_count': n, 'net_profit': net_profit,
            'win_rate': win_rate, 'avg_pnl': avg_pnl,
            'recovery_speed_raw': recovery_speed_raw,
            'stuck_penalty_raw': stuck_penalty_raw,
            'excl_top5_pnl': round(excl_top5, 2),
            'robustness_pct': robustness, 'active_days': active_days,
        }
    return raw

import redis
_redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

def fetch_open_dca_positions(regime, win_start):
    with db.get_db() as conn:
        cur = conn.cursor()
        query = """
            SELECT b.name, p.coin, p.avg_cost, p.total_invested, p.opened_at
            FROM positions p JOIN bots b ON b.id = p.bot_id
            WHERE p.status='open' AND b.is_research=TRUE AND p.btc_regime=%s
        """
        params = [regime]
        if win_start:
            query += " AND p.opened_at >= %s"
            params.append(win_start)
        cur.execute(query, params)
        return cur.fetchall()

def compute_open_position_metrics(open_rows):
    """Real-time metrics from currently-open positions using live
    Redis prices. Returns {method: {'capital_recovery_health':...,
    'max_drawdown_raw':...}}.

    capital_recovery_health: graduated stuck-capital penalty.
      warning: >72h old AND <-3% unrealized -> 0.3x weight
      bad:     >7d old  AND <-7% unrealized -> 0.6x weight
      critical:>14d old AND <-10% unrealized -> 1.0x weight
      1.0 = perfectly healthy, lower = more stuck capital.

    max_drawdown_raw: the worst (most negative) unrealized pct
    currently sitting in any open position for that method. This is
    CURRENT drawdown, not true historical peak-to-trough (we don't
    have continuous floating-PnL history to compute that yet) - but
    it's a real, honest, currently-available signal."""
    from datetime import datetime, timezone
    by_method = {}
    for method, coin, avg_cost, invested, opened in open_rows:
        avg_cost = float(avg_cost or 0)
        invested = float(invested or 0)
        if avg_cost <= 0 or invested <= 0 or not opened:
            continue
        if opened.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(timezone.utc)
        price_raw = _redis.get(f'price:MEXC Paper:{coin}/USDT')
        if not price_raw:
            continue
        current_price = float(price_raw)
        unrealized_pct = (current_price - avg_cost) / avg_cost * 100
        age_hours = (now - opened).total_seconds() / 3600

        if method not in by_method:
            by_method[method] = {'total_invested': 0.0, 'stuck_weighted': 0.0, 'worst_pct': 0.0}
        by_method[method]['total_invested'] += invested
        by_method[method]['worst_pct'] = min(by_method[method]['worst_pct'], unrealized_pct)

        tier_weight = 0.0
        if age_hours > 336 and unrealized_pct < -10:
            tier_weight = 1.0
        elif age_hours > 168 and unrealized_pct < -7:
            tier_weight = 0.6
        elif age_hours > 72 and unrealized_pct < -3:
            tier_weight = 0.3
        by_method[method]['stuck_weighted'] += invested * tier_weight

    result = {}
    for method, d in by_method.items():
        stuck_pct = d['stuck_weighted'] / d['total_invested'] if d['total_invested'] > 0 else 0
        result[method] = {
            'capital_recovery_health': max(0.0, 1.0 - stuck_pct),
            'max_drawdown_raw': d['worst_pct'],
        }
    return result

DCA_METRICS = ['net_profit', 'avg_pnl', 'max_drawdown', 'capital_recovery_health',
               'recovery_speed', 'trade_count_confidence']

def normalize_metric(values_by_method, metric):
    """Min-max normalize one metric across all methods, floor 0.01."""
    vals = list(values_by_method.values())
    vmin, vmax = min(vals), max(vals)
    out = {}
    for method, v in values_by_method.items():
        if vmax - vmin < 1e-9:
            out[method] = 0.5
        else:
            out[method] = (v - vmin) / (vmax - vmin)
        out[method] = max(0.01, min(1.0, out[method]))
    return out

def calculate_dca_scores(regime, window_key):
    """Real weighted RARS for DCA methods in one regime+window.
    Does NOT apply eligibility gates (30 trades/7 days) - that's the
    job of champion promotion logic (build step 2), not this scoring
    writer. This function just computes and returns real numbers."""
    win_start = window_start(window_key)
    closed_rows = fetch_dca_trades(regime, win_start)
    raw_closed = compute_dca_raw_metrics(closed_rows)
    open_rows = fetch_open_dca_positions(regime, win_start)
    raw_open = compute_open_position_metrics(open_rows)

    methods = set(raw_closed.keys()) | set(raw_open.keys())
    if not methods:
        return []

    raw = {}
    for m in methods:
        c = raw_closed.get(m, {})
        o = raw_open.get(m, {})
        raw[m] = {
            'net_profit': c.get('net_profit', 0),
            'avg_pnl': c.get('avg_pnl', 0),
            'max_drawdown': o.get('max_drawdown_raw', 0),
            'capital_recovery_health': o.get('capital_recovery_health', 1.0),
            'recovery_speed': c.get('recovery_speed_raw', 0),
            'trade_count_confidence': c.get('trade_count', 0),
        }

    normalized = {m: {} for m in methods}
    for metric in DCA_METRICS:
        vals_by_method = {m: raw[m][metric] for m in methods}
        norm = normalize_metric(vals_by_method, metric)
        for m in methods:
            normalized[m][metric] = norm[m]

    weights = get_weights('DCA', regime)
    results = []
    for m in methods:
        weighted_sum = sum(normalized[m][metric] * weight
                            for metric, weight in weights.items()
                            if metric in normalized[m])
        rars_score = round(weighted_sum * 100, 2)
        c = raw_closed.get(m, {})
        results.append({
            'bot_name': m,
            'method_family': c.get('method', m.rsplit('-',1)[0]),
            'rars_score': rars_score,
            'trade_count': c.get('trade_count', 0),
            'active_days': c.get('active_days', 0),
            'excl_top5_pnl': c.get('excl_top5_pnl', 0),
            'robustness_pct': c.get('robustness_pct', 0),
        })
    results.sort(key=lambda x: -x['rars_score'])
    return results

SCALPER_METRICS = ['net_profit', 'avg_pnl', 'max_drawdown',
                   'win_rate', 'profit_factor', 'trade_count_confidence',
                   'execution_slippage_penalty']

def fetch_scalper_trades(regime, win_start):
    with db.get_db() as conn:
        cur = conn.cursor()
        query = """
            SELECT b.name, sp.pnl_usdt, sp.pnl_pct,
                   sp.entry_time, sp.exit_time, sp.hold_seconds,
                   sp.max_loss_seen, sp.entry_price, sp.exit_price,
                   sp.base_order, b.method
            FROM scalper_positions sp JOIN bots b ON b.id = sp.bot_id
            WHERE sp.status='closed' AND b.is_research=TRUE
            AND sp.btc_regime=%s
        """
        params = [regime]
        if win_start:
            query += " AND sp.exit_time >= %s"
            params.append(win_start)
        cur.execute(query, params)
        return cur.fetchall()

def compute_scalper_raw_metrics(rows):
    methods = {}
    for row in rows:
        bot_name = row[0]
        method = row[10]
        if bot_name not in methods:
            methods[bot_name] = {'trades': [], 'method': method}
        pnl_usdt = float(row[1] or 0)
        pnl_pct = float(row[2] or 0)
        hold_sec = int(row[5] or 0)
        max_loss = float(row[6] or 0)
        entry = float(row[7] or 0)
        exit_ = float(row[8] or 0)
        slippage = abs(exit_ - entry) / entry * 100 if entry > 0 else 0
        exit_time = row[4]
        methods[bot_name]['trades'].append({
            'pnl_usdt': pnl_usdt, 'pnl_pct': pnl_pct,
            'hold_sec': hold_sec, 'max_loss': max_loss,
            'slippage': slippage, 'exit_time': exit_time,
        })

    raw = {}
    for bot_name, data in methods.items():
        trades = data['trades']
        method = data['method']
        n = len(trades)
        pnls = sorted([t['pnl_usdt'] for t in trades], reverse=True)
        wins = [p for p in pnls if p > 0]
        losses = [abs(p) for p in pnls if p <= 0]
        net_profit = sum(pnls)
        win_rate = len(wins) / n if n else 0
        avg_pnl = net_profit / n if n else 0
        gross_win = sum(wins)
        gross_loss = sum(losses)
        profit_factor = gross_win / gross_loss if gross_loss > 0 else gross_win
        max_drawdown = min(t['max_loss'] for t in trades)
        avg_slippage = sum(t['slippage'] for t in trades) / n if n else 0
        excl_top5 = sum(pnls[5:]) if n > 5 else net_profit
        robustness = round(excl_top5 / net_profit * 100, 1) if net_profit > 0 else 0
        active_days = len(set(
            t['exit_time'].date()
            for t in trades if t.get('exit_time')
        ))
        raw[bot_name] = {
            'method': method, 'trade_count': n, 'net_profit': net_profit,
            'win_rate': win_rate, 'avg_pnl': avg_pnl,
            'profit_factor': profit_factor, 'max_drawdown': max_drawdown,
            'execution_slippage_penalty': avg_slippage,
            'trade_count_confidence': n, 'excl_top5_pnl': round(excl_top5, 2),
            'robustness_pct': robustness, 'active_days': active_days,
        }
    return raw

def calculate_scalper_scores(regime, window_key):
    win_start = window_start(window_key)
    rows = fetch_scalper_trades(regime, win_start)
    raw = compute_scalper_raw_metrics(rows)
    if not raw:
        return []

    normalized = {m: {} for m in raw}
    for metric in SCALPER_METRICS:
        vals = {m: raw[m].get(metric, 0) for m in raw}
        norm = normalize_metric(vals, metric)
        for m in raw:
            normalized[m][metric] = norm[m]

    # execution_slippage_penalty: lower is better, so invert
    for m in raw:
        normalized[m]['execution_slippage_penalty'] = max(
            0.01, 1.0 - normalized[m]['execution_slippage_penalty'])
    # max_drawdown: less negative is better, invert
    for m in raw:
        normalized[m]['max_drawdown'] = max(
            0.01, 1.0 - abs(normalized[m]['max_drawdown']))

    weights = get_weights('SCALPER', regime)
    results = []
    for m in raw:
        weighted_sum = sum(normalized[m].get(metric, 0) * weight
                            for metric, weight in weights.items())
        rars_score = round(weighted_sum * 100, 2)
        results.append({
            'bot_name': m,
            'method_family': raw[m].get('method', m.rsplit('-',1)[0]),
            'rars_score': rars_score,
            'trade_count': raw[m]['trade_count'],
            'active_days': raw[m]['active_days'],
            'excl_top5_pnl': raw[m]['excl_top5_pnl'],
            'robustness_pct': raw[m]['robustness_pct'],
        })
    results.sort(key=lambda x: -x['rars_score'])
    return results

def write_scores_to_db(system_type, regime, window_key, results):
    """Write scored results to rars_scores table.
    method column stores bot_name (e.g. 'E31-4') not method family
    (e.g. 'E31') — this is intentional, champion is a specific bot
    configuration, not just a method family."""
    if not results:
        return 0
    with db.get_db() as conn:
        cur = conn.cursor()
        for r in results:
            # Anomaly detection (ADDED June 20 2026, per SYSTEM_MAP
            # spec): compares this score to ~7 days ago for the same
            # bot+regime+window. Flags when RARS swung >8% while
            # trade_count stayed roughly flat - that combination means
            # old trades rolled out of the rolling window, not a real
            # behavior change. 6-day lower bound (not exactly 7) gives
            # buffer for cron scheduling jitter while still excluding
            # any earlier-today entries if scoring ran more than once.
            cur.execute("""
                SELECT rars_score, trade_count FROM rars_scores
                WHERE system_type=%s AND method=%s AND regime=%s
                AND score_window=%s AND calculated_at < NOW() - INTERVAL '6 days'
                ORDER BY calculated_at DESC LIMIT 1
            """, (system_type, r['bot_name'], regime, window_key))
            prev = cur.fetchone()
            anomaly = False
            if prev and prev[0] and float(prev[0]) != 0:
                prev_score, prev_trade_count = float(prev[0]), prev[1]
                pct_swing = abs(r['rars_score'] - prev_score) / abs(prev_score) * 100
                trade_count_diff = abs(r['trade_count'] - prev_trade_count)
                if pct_swing > 8 and trade_count_diff <= 2:
                    anomaly = True

            cur.execute("""
                INSERT INTO rars_scores (
                    system_type, method, regime, score_window,
                    rars_score, excl_top5_pnl, robustness_pct,
                    trade_count, active_days, anomaly_flag, calculated_at
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """, (system_type, r['bot_name'], regime, window_key,
                  r['rars_score'], r.get('excl_top5_pnl', 0),
                  r.get('robustness_pct', 0), r['trade_count'],
                  r.get('active_days', 0), anomaly))
        conn.commit()
    return len(results)

def run_daily_scoring():
    """Main entry point - score all systems/regimes/windows and
    write to rars_scores. Called by daily_cron.sh."""
    total = 0
    for regime in REGIMES:
        for window_key in WINDOWS.keys():
            dca = calculate_dca_scores(regime, window_key)
            n = write_scores_to_db('DCA', regime, window_key, dca)
            print(f"✅ DCA {regime}/{window_key}: {n} methods scored")
            total += n

            scalper = calculate_scalper_scores(regime, window_key)
            n = write_scores_to_db('SCALPER', regime, window_key, scalper)
            print(f"✅ SCALPER {regime}/{window_key}: {n} methods scored")
            total += n

    print(f"RECORDS_PROCESSED:{total}")
    return total

if __name__ == '__main__':
    print("=== RARS Champion Scoring Run ===")
    run_daily_scoring()
    print("=== Done ==="  )

print("✅ Chunk 7 loaded: DB writer + main entry point ready")
