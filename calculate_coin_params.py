"""
calculate_coin_params.py — Dynamic Coin Parameter Calculator v2
Runs daily · calculates optimal DCA/TP/trailing per coin per category
Uses 30 days hourly OHLCV data from DB

v2 changes (locked spec, June 17 2026):
- spacing = MAX(ATR*1.5, median_drop*0.85), was MIN
- trailing = TP*0.25, was ATR*0.8
- minimum 15 sample events required, else category default
- daily change cap: spacing/TP +-20%, trail +-15%, size_mult +-10%
- circuit breaker freezes coin on extreme single-day anomalies
- stablecoin/pegged asset exclusion list
- new coin hard gate: market_age_days < 30 -> not tradeable
- category limits read from DB table category_limits (admin-editable)
- full audit trail written to coin_parameter_history
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
import numpy as np
import math
from datetime import datetime

db.init_pool()

CALC_VERSION = 'v2'
MIN_SAMPLE_SIZE = 15
NEW_COIN_MIN_AGE_DAYS = 30

DAILY_CAP = {
    'spacing': 0.20,
    'tp':      0.20,
    'trail':   0.15,
    'size':    0.10,
}

STABLECOIN_BLACKLIST = {
    'USDC', 'USDT', 'FDUSD', 'TUSD', 'DAI', 'BUSD', 'USDP', 'GUSD',
    'WBTC', 'WBETH', 'STETH', 'WSTETH', 'CBETH', 'RETH',
}

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def is_stablecoin(coin):
    base = coin.split('/')[0].upper()
    return base in STABLECOIN_BLACKLIST

PEGGED_ATR_PCT_THRESHOLD = 0.20  # below this = behaves like a stablecoin, exclude

def is_pegged_by_volatility(atr_pct):
    """Catches stablecoins/pegged assets not in the name blacklist.
    Grounded in real data: BTC (most stable major coin) shows ~0.35%
    ATR. Known stablecoins (USDC, USDS, FDUSD etc) showed 0.01%-0.2%.
    Threshold set safely below BTC's real floor."""
    return atr_pct is not None and atr_pct < PEGGED_ATR_PCT_THRESHOLD

def load_category_limits():
    """Load category limits from DB table (admin-editable)."""
    limits = {}
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT category, spacing_min, spacing_max, tp_min, tp_max, trail_min, trail_max, size_min, size_max FROM category_limits")
        for row in cur.fetchall():
            cat, smin, smax, tpmin, tpmax, trmin, trmax, szmin, szmax = row
            limits[cat] = {
                'spacing': (float(smin), float(smax)),
                'tp':      (float(tpmin), float(tpmax)),
                'trail':   (float(trmin), float(trmax)),
                'size':    (float(szmin), float(szmax)),
            }
    return limits

def get_previous_params(coin, exchange):
    """Fetch yesterday's stored values for daily change cap + circuit breaker."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT dca_spacing, take_profit_pct, trailing_pct, size_mult, atr_14, median_drop
            FROM coin_parameters WHERE coin=%s AND exchange=%s
        """, (coin, exchange))
        row = cur.fetchone()
    if not row:
        return None
    return {
        'spacing': float(row[0]) if row[0] is not None else None,
        'tp':      float(row[1]) if row[1] is not None else None,
        'trail':   float(row[2]) if row[2] is not None else None,
        'size':    float(row[3]) if row[3] is not None else None,
        'atr_14':  float(row[4]) if row[4] is not None else None,
        'median_drop': float(row[5]) if row[5] is not None else None,
    }

def get_first_seen_days(coin):
    """Days since coin was first seen by Averion (survives wipes)."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT EXTRACT(DAY FROM NOW() - first_seen_at)::int FROM coin_first_seen WHERE coin=%s", (coin,))
        row = cur.fetchone()
    return int(row[0]) if row and row[0] is not None else 0

def check_new_coin_eligibility(coin, category):
    """
    Returns (eligible, blend_pct_own_data, reason).
    blend_pct_own_data: 0.0 = pure category default, 1.0 = pure coin data, 0.3 = 31-90 day blend
    """
    if category in ('mega', 'large', 'mid'):
        return True, 1.0, None

    age_days = get_first_seen_days(coin)
    if age_days < NEW_COIN_MIN_AGE_DAYS:
        return False, 0.0, 'new_coin_under_30_days'
    elif age_days < 90:
        return True, 0.3, None  # 31-90 days: 70% default / 30% own data
    else:
        return True, 1.0, None  # 90+ days: own data, subject to sample-size gate separately

def apply_daily_cap(new_value, prev_value, cap_pct):
    """Limit how much a value can change from yesterday in one day."""
    if prev_value is None or prev_value == 0:
        return new_value
    max_up = prev_value * (1 + cap_pct)
    max_down = prev_value * (1 - cap_pct)
    return clamp(new_value, max_down, max_up)

def check_circuit_breaker(atr_pct, median_drop, prev, ohlcv_rows, closes):
    """Returns frozen_reason string if anomaly detected, else None."""
    if prev is None:
        return None

    if prev['atr_14'] and atr_14_raw_check(atr_pct, prev):
        pass  # handled below with actual atr_14 not pct, kept simple

    # price gap > 50% in a single day (compare last two closes)
    if len(closes) >= 2 and closes[-2] > 0:
        gap = abs(closes[-1] - closes[-2]) / closes[-2]
        if gap > 0.50:
            return 'price_gap_over_50pct'

    # median_drop changed > 2x from yesterday
    if prev['median_drop'] and prev['median_drop'] > 0:
        if median_drop > prev['median_drop'] * 2:
            return 'median_drop_2x_spike'

    return None

def atr_14_raw_check(atr_pct, prev):
    return False  # placeholder, real ATR-vs-ATR check done in caller with raw atr_14

def calculate_params_for_coin(coin, ohlcv_rows, category, limits, prev, blend_pct_own_data=1.0):
    """Calculate optimal DCA/TP/trail from OHLCV data. Returns dict or None."""
    if not ohlcv_rows or len(ohlcv_rows) < 24:
        return None

    closes = np.array([float(r[4]) for r in ohlcv_rows])
    highs  = np.array([float(r[2]) for r in ohlcv_rows])
    lows   = np.array([float(r[3]) for r in ohlcv_rows])
    volumes = np.array([float(r[5]) for r in ohlcv_rows]) if len(ohlcv_rows[0]) > 5 else None

    # ATR-14
    tr = np.maximum(highs[1:] - lows[1:],
         np.maximum(np.abs(highs[1:] - closes[:-1]),
                    np.abs(lows[1:] - closes[:-1])))
    atr_14 = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
    atr_pct = (atr_14 / closes[-1] * 100) if closes[-1] > 0 else 0

    # Zero volume check (last 24h = last 24 hourly candles)
    zero_volume_24h = False
    if volumes is not None and len(volumes) >= 24:
        zero_volume_24h = float(np.sum(volumes[-24:])) == 0

    # Drops (for spacing)
    drops = []
    for i in range(1, len(closes)):
        if closes[i] < closes[i-1] and closes[i-1] > 0:
            drop = (closes[i-1] - closes[i]) / closes[i-1] * 100
            if drop > 0.1:
                drops.append(drop)

    # Recoveries (for TP)
    recoveries = []
    for i in range(2, len(closes)):
        if closes[i] > closes[i-1] and closes[i-1] < closes[i-2]:
            recovery = (closes[i] - closes[i-1]) / closes[i-1] * 100
            if recovery > 0.1:
                recoveries.append(recovery)

    sample_drops = len(drops)
    sample_recoveries = len(recoveries)
    insufficient_sample = sample_drops < MIN_SAMPLE_SIZE or sample_recoveries < MIN_SAMPLE_SIZE

    # Circuit breaker checks (only meaningful if we have a previous value)
    frozen_reason = None
    if prev is not None:
        if len(closes) >= 2 and closes[-2] > 0:
            gap = abs(closes[-1] - closes[-2]) / closes[-2]
            if gap > 0.50:
                frozen_reason = 'price_gap_over_50pct'
        if frozen_reason is None and prev['atr_14'] and prev['atr_14'] > 0:
            if atr_14 > prev['atr_14'] * 3:
                frozen_reason = 'atr_3x_spike'
        if frozen_reason is None and prev['median_drop'] and prev['median_drop'] > 0 and drops:
            median_drop_today = float(np.median(drops))
            if median_drop_today > prev['median_drop'] * 2:
                frozen_reason = 'median_drop_2x_spike'
        if frozen_reason is None and zero_volume_24h:
            frozen_reason = 'zero_volume_24h'

    if frozen_reason:
        return {'frozen': True, 'frozen_reason': frozen_reason,
                'sample_count_drops': sample_drops, 'sample_count_recoveries': sample_recoveries}

    if insufficient_sample:
        mid_spacing = (limits['spacing'][0] + limits['spacing'][1]) / 2
        mid_tp = (limits['tp'][0] + limits['tp'][1]) / 2
        mid_trail = (limits['trail'][0] + limits['trail'][1]) / 2
        mid_size = (limits['size'][0] + limits['size'][1]) / 2
        return {
            'dca_spacing': round(mid_spacing, 1), 'take_profit_pct': round(mid_tp, 1),
            'trailing_pct': round(mid_trail, 1), 'size_mult': round(mid_size, 2),
            'atr_14': round(float(atr_14), 8), 'atr_pct': round(float(atr_pct), 4),
            'median_drop': None, 'median_recovery': None,
            'volatility_pct': None, 'data_quality': 'insufficient_sample',
            'sample_count_drops': sample_drops, 'sample_count_recoveries': sample_recoveries,
            'frozen': False, 'frozen_reason': None,
        }

    median_drop = float(np.median(drops))
    median_recovery = float(np.median(recoveries))

    # v2: MAX instead of MIN
    spacing_raw = max(atr_pct * 1.5, median_drop * 0.85)
    spacing = clamp(round(spacing_raw, 1), *limits['spacing'])

    # 31-90 day new-coin blend: final calculated value blended with
    # category default midpoint. blend_pct_own_data=1.0 = pure own data
    # (established coins, or 90+ day coins past sample-size gate).
    # blend_pct_own_data=0.3 = 70% category default / 30% own data.
    if blend_pct_own_data < 1.0:
        mid_spacing = (limits['spacing'][0] + limits['spacing'][1]) / 2
        spacing = spacing * blend_pct_own_data + mid_spacing * (1 - blend_pct_own_data)
        spacing = clamp(round(spacing, 1), *limits['spacing'])

    spacing = apply_daily_cap(spacing, prev['spacing'] if prev else None, DAILY_CAP['spacing'])
    spacing = clamp(round(spacing, 1), *limits['spacing'])

    tp_raw = median_recovery * 0.8
    tp = clamp(round(tp_raw, 1), *limits['tp'])

    if blend_pct_own_data < 1.0:
        mid_tp = (limits['tp'][0] + limits['tp'][1]) / 2
        tp = tp * blend_pct_own_data + mid_tp * (1 - blend_pct_own_data)
        tp = clamp(round(tp, 1), *limits['tp'])
    tp = apply_daily_cap(tp, prev['tp'] if prev else None, DAILY_CAP['tp'])
    tp = clamp(round(tp, 1), *limits['tp'])

    # v2: trailing derived from TP, not raw ATR
    trail_raw = tp * 0.25
    trail = clamp(round(trail_raw, 1), *limits['trail'])
    trail = apply_daily_cap(trail, prev['trail'] if prev else None, DAILY_CAP['trail'])
    trail = clamp(round(trail, 1), *limits['trail'])

    size_mult = clamp(1 + atr_pct/10, *limits['size'])

    if blend_pct_own_data < 1.0:
        mid_size = (limits['size'][0] + limits['size'][1]) / 2
        size_mult = size_mult * blend_pct_own_data + mid_size * (1 - blend_pct_own_data)
        size_mult = clamp(size_mult, *limits['size'])

    size_mult = apply_daily_cap(size_mult, prev['size'] if prev else None, DAILY_CAP['size'])
    size_mult = round(clamp(size_mult, *limits['size']), 2)

    returns = np.diff(closes) / closes[:-1] * 100
    volatility = round(float(np.std(returns)), 2)

    return {
        'dca_spacing': spacing, 'take_profit_pct': tp, 'trailing_pct': trail,
        'size_mult': size_mult, 'atr_14': round(float(atr_14), 8),
        'atr_pct': round(float(atr_pct), 4),
        'median_drop': round(median_drop, 2), 'median_recovery': round(median_recovery, 2),
        'volatility_pct': volatility,
        'data_quality': 'calculated' if len(ohlcv_rows) >= 168 else 'partial',
        'sample_count_drops': sample_drops, 'sample_count_recoveries': sample_recoveries,
        'frozen': False, 'frozen_reason': None,
    }

def run():
    print(f'⚙️  Calculating coin parameters v2 — {datetime.now().strftime("%Y-%m-%d %H:%M")}')

    limits_by_category = load_category_limits()

    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (coin) coin, category
            FROM coin_history
            ORDER BY coin, id DESC
        """)
        coins = cur.fetchall()

    print(f'Processing {len(coins)} coins...')

    calculated = estimated = errors = frozen_count = excluded = 0

    for coin, category in coins:
        try:
            limits = limits_by_category.get(category, limits_by_category.get('micro'))
            prev = get_previous_params(coin, 'MEXC')

            tradeable = True
            exclusion_reason = None
            blend_pct_own_data = 1.0

            if is_stablecoin(coin):
                tradeable = False
                exclusion_reason = 'stablecoin_excluded'
                excluded += 1

            if tradeable:
                eligible, blend_pct_own_data, new_coin_reason = check_new_coin_eligibility(coin, category)
                if not eligible:
                    tradeable = False
                    exclusion_reason = new_coin_reason
                    excluded += 1

            rows = db.get_ohlcv(coin, 'mexc', limit=720)

            if rows and len(rows) >= 24:
                params = calculate_params_for_coin(coin, rows, category, limits, prev, blend_pct_own_data)
            else:
                params = None

            # Volatility-based pegged-asset check: catches stablecoins not
            # in the name blacklist (e.g. USDS, FDUSD slipped through earlier)
            if tradeable and params and not params.get('frozen') and is_pegged_by_volatility(params.get('atr_pct')):
                tradeable = False
                exclusion_reason = 'pegged_low_volatility'
                excluded += 1

            if not params:
                mid_spacing = (limits['spacing'][0] + limits['spacing'][1]) / 2
                mid_tp = (limits['tp'][0] + limits['tp'][1]) / 2
                mid_trail = (limits['trail'][0] + limits['trail'][1]) / 2
                mid_size = (limits['size'][0] + limits['size'][1]) / 2
                params = {
                    'dca_spacing': round(mid_spacing, 1), 'take_profit_pct': round(mid_tp, 1),
                    'trailing_pct': round(mid_trail, 1), 'size_mult': round(mid_size, 2),
                    'atr_14': None, 'median_drop': None, 'median_recovery': None,
                    'volatility_pct': None, 'data_quality': 'estimated',
                    'sample_count_drops': 0, 'sample_count_recoveries': 0,
                    'frozen': False, 'frozen_reason': None,
                }
                estimated += 1
            elif params.get('frozen'):
                frozen_count += 1
                # Keep previous values, just log the freeze, skip update
                with db.get_db() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE coin_parameters SET frozen=TRUE, frozen_reason=%s, calculated_at=NOW()
                        WHERE coin=%s AND exchange='MEXC'
                    """, (params['frozen_reason'], coin))
                    cur.execute("""
                        INSERT INTO coin_parameter_history
                            (coin, exchange, category, old_spacing, new_spacing, old_tp, new_tp,
                             old_trail, new_trail, old_size_mult, new_size_mult,
                             sample_count_drops, sample_count_recoveries, data_quality,
                             frozen_reason, calculation_version)
                        VALUES (%s,'MEXC',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'frozen',%s,%s)
                    """, (coin, category,
                          prev['spacing'] if prev else None, prev['spacing'] if prev else None,
                          prev['tp'] if prev else None, prev['tp'] if prev else None,
                          prev['trail'] if prev else None, prev['trail'] if prev else None,
                          prev['size'] if prev else None, prev['size'] if prev else None,
                          params['sample_count_drops'], params['sample_count_recoveries'],
                          params['frozen_reason'], CALC_VERSION))
                continue
            else:
                calculated += 1

            with db.get_db() as conn:
                cur = conn.cursor()
                for k in params:
                    if params[k] is not None and hasattr(params[k], '__float__'):
                        v = float(params[k])
                        params[k] = None if (math.isnan(v) or math.isinf(v)) else v

                cur.execute("""
                    INSERT INTO coin_parameters
                        (coin, exchange, category, dca_spacing, take_profit_pct,
                         trailing_pct, size_mult, atr_14, median_drop,
                         median_recovery, volatility_pct, data_quality, calculated_at,
                         sample_count_drops, sample_count_recoveries, calculation_version,
                         frozen, frozen_reason, tradeable)
                    VALUES (%s,'MEXC',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),%s,%s,%s,FALSE,%s,%s)
                    ON CONFLICT (coin, exchange) DO UPDATE SET
                        category=EXCLUDED.category, dca_spacing=EXCLUDED.dca_spacing,
                        take_profit_pct=EXCLUDED.take_profit_pct, trailing_pct=EXCLUDED.trailing_pct,
                        size_mult=EXCLUDED.size_mult, atr_14=EXCLUDED.atr_14,
                        median_drop=EXCLUDED.median_drop, median_recovery=EXCLUDED.median_recovery,
                        volatility_pct=EXCLUDED.volatility_pct, data_quality=EXCLUDED.data_quality,
                        calculated_at=NOW(), sample_count_drops=EXCLUDED.sample_count_drops,
                        sample_count_recoveries=EXCLUDED.sample_count_recoveries,
                        calculation_version=EXCLUDED.calculation_version,
                        frozen=FALSE, frozen_reason=EXCLUDED.frozen_reason,
                        tradeable=EXCLUDED.tradeable
                """, (coin, category, params['dca_spacing'], params['take_profit_pct'],
                      params['trailing_pct'], params['size_mult'], params['atr_14'],
                      params['median_drop'], params['median_recovery'], params['volatility_pct'],
                      params['data_quality'], params['sample_count_drops'],
                      params['sample_count_recoveries'], CALC_VERSION,
                      exclusion_reason, tradeable))

                cur.execute("""
                    INSERT INTO coin_parameter_history
                        (coin, exchange, category, old_spacing, new_spacing, old_tp, new_tp,
                         old_trail, new_trail, old_size_mult, new_size_mult,
                         sample_count_drops, sample_count_recoveries, data_quality,
                         frozen_reason, calculation_version)
                    VALUES (%s,'MEXC',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (coin, category,
                      prev['spacing'] if prev else None, params['dca_spacing'],
                      prev['tp'] if prev else None, params['take_profit_pct'],
                      prev['trail'] if prev else None, params['trailing_pct'],
                      prev['size'] if prev else None, params['size_mult'],
                      params['sample_count_drops'], params['sample_count_recoveries'],
                      params['data_quality'], exclusion_reason, CALC_VERSION))

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f'  ⚠️ {coin}: {e}')

    print(f'\n✅ Done!')
    print(f'  Calculated: {calculated} coins')
    print(f'  Estimated (category default): {estimated} coins')
    print(f'  Frozen (circuit breaker): {frozen_count} coins')
    print(f'  Excluded (stablecoin/new): {excluded} coins')
    print(f'  Errors: {errors}')
    print(f'RECORDS_PROCESSED:{len(coins)}')

    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT coin, category, dca_spacing, take_profit_pct, trailing_pct, data_quality, tradeable
            FROM coin_parameters ORDER BY category, coin LIMIT 10
        """)
        print(f'\n📊 Sample parameters:')
        print(f'{"Coin":<10} {"Cat":<8} {"DCA%":<8} {"TP%":<8} {"Trail%":<8} {"Quality":<20} {"Tradeable"}')
        print('-'*75)
        for r in cur.fetchall():
            print(f'{r[0]:<10} {r[1]:<8} {r[2]:<8} {r[3]:<8} {r[4]:<8} {r[5]:<20} {r[6]}')

if __name__ == '__main__':
    run()
