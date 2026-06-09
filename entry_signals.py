"""
entry_signals.py — Entry signal checker for all research methods E1-E26
Returns True/False for each method based on OHLCV data + bot params
Called by bot_loop.py before opening any position
"""

import database as db
import indicators as ind


def get_ohlcv_data(coin, exchange='mexc', limit=200):
    """Fetch OHLCV from DB and convert to arrays."""
    rows = db.get_ohlcv(coin, exchange, limit=limit)
    if not rows or len(rows) < 20:
        return None
    return ind.to_arrays(rows)


def check_entry_signal(method, params, coin, exchange='mexc', btc_data=None, ohlcv_data=None):
    """
    Main entry point. Returns True if entry signal fires.
    method: 'E1' through 'E26' or 'E18b'
    params: dict of parameters from bot_params JSON field
    coin: e.g. 'BTC'
    btc_data: pre-fetched BTC data dict (for E23 relative strength)
    ohlcv_data: pre-fetched OHLCV arrays (skip DB fetch if provided)
    """
    d = ohlcv_data if ohlcv_data is not None else get_ohlcv_data(coin, exchange)
    if d is None:
        return False

    try:
        fn = SIGNAL_MAP.get(method)
        if fn is None:
            return False
        return bool(fn(d, params, btc_data))
    except Exception as e:
        return False


# ═══════════════════════════════
# E1 — VWAP + RSI + ATR + Bounce
# ═══════════════════════════════
def signal_e1(d, p, _):
    if not ind.enough(d, 50):
        return False
    rsi_threshold = p.get('rsi_threshold', 30)
    vwap_pct      = p.get('vwap_pct', 3.0)
    atr_mult      = p.get('atr_mult', 1.5)

    rsi  = ind.calc_rsi(d['close'], 14)
    vwap = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], 24)
    atr  = ind.calc_atr(d['high'], d['low'], d['close'], 14)
    if rsi is None or vwap is None or atr is None:
        return False

    price = d['close'][-1]
    rsi_ok   = rsi < rsi_threshold
    vwap_ok  = price < vwap * (1 - vwap_pct / 100)
    atr_ok   = (d['high'][-1] - d['low'][-1]) > atr * atr_mult
    bounce   = d['close'][-1] > d['close'][-2]
    return rsi_ok and vwap_ok and atr_ok and bounce


# ═══════════════════════════════
# E2 — Panic Exhaustion (BB + Volume)
# ═══════════════════════════════
def signal_e2(d, p, _):
    if not ind.enough(d, 30):
        return False
    vol_mult  = p.get('vol_mult', 2.0)
    bb_sigma  = p.get('bb_sigma', 2.0)
    recovery  = p.get('recovery_pct', 0.5)

    bb_u, bb_m, bb_l = ind.calc_bollinger(d['close'], 20, bb_sigma)
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if bb_l is None or vr is None:
        return False

    prev_pierced = d['close'][-2] < bb_l
    curr_inside  = d['close'][-1] > bb_l
    vol_ok       = vr >= vol_mult
    recovery_ok  = (d['close'][-1] - d['close'][-2]) / d['close'][-2] * 100 >= recovery
    return prev_pierced and curr_inside and vol_ok and recovery_ok


# ═══════════════════════════════
# E3 — Volume Climax
# ═══════════════════════════════
def signal_e3(d, p, _):
    if not ind.enough(d, 30):
        return False
    vol_mult    = p.get('vol_mult', 4.0)
    range_atr   = p.get('range_atr', 2.5)
    close_upper = p.get('close_upper', 50)

    vr  = ind.calc_volume_ratio(d['volume'], 20)
    atr = ind.calc_atr(d['high'], d['low'], d['close'], 14)
    sma = ind.calc_sma(d['close'], 20)
    if vr is None or atr is None or sma is None:
        return False

    candle_range = d['high'][-1] - d['low'][-1]
    close_pos    = (d['close'][-1] - d['low'][-1]) / candle_range * 100 if candle_range > 0 else 0
    vol_ok       = vr >= vol_mult
    range_ok     = candle_range >= atr * range_atr
    below_sma    = d['close'][-1] < sma
    close_ok     = close_pos >= close_upper
    return vol_ok and range_ok and below_sma and close_ok


# ═══════════════════════════════
# E4 — Time-Cycle Window
# ═══════════════════════════════
def signal_e4(d, p, _):
    # SMA pullback entry - price below SMA
    if not ind.enough(d, 20):
        return False
    sma_period  = p.get('sma_period', 24)
    drop_pct    = p.get('drop_pct', 2.0)
    sma = ind.calc_sma(d['close'], sma_period)
    if sma is None:
        return False
    price = d['close'][-1]
    pct_below = (sma - price) / sma * 100
    return pct_below >= drop_pct


# ═══════════════════════════════
# E5 — Multi-Timeframe EMA
# ═══════════════════════════════
def signal_e5(d, p, _):
    if not ind.enough(d, 200):
        return False
    macro_ema   = p.get('macro_ema', 168)
    pullback_ema = p.get('pullback_ema', 24)
    rsi_threshold = p.get('rsi_threshold', 40)

    ema_macro    = ind.calc_ema(d['close'], macro_ema)
    ema_pullback = ind.calc_ema(d['close'], pullback_ema)
    rsi          = ind.calc_rsi(d['close'], 14)
    if ema_macro is None or ema_pullback is None or rsi is None:
        return False

    price = d['close'][-1]
    return (price > ema_macro and
            price < ema_pullback and
            rsi < rsi_threshold)


# ═══════════════════════════════
# E6 — Z-Score Statistical
# ═══════════════════════════════
def signal_e6(d, p, _):
    lookback  = p.get('lookback', 168)
    z_trigger = p.get('z_trigger', -2.5)
    if not ind.enough(d, lookback):
        return False
    z = ind.calc_zscore(d['close'], lookback)
    return z is not None and z <= z_trigger


# ═══════════════════════════════
# E7 — Volatility Squeeze
# ═══════════════════════════════
def signal_e7(d, p, _):
    if not ind.enough(d, 50):
        return False
    squeeze_hours = p.get('squeeze_hours', 12)
    vol_mult      = p.get('vol_mult', 1.5)

    bb_u, bb_m, bb_l = ind.calc_bollinger(d['close'], 20, 2.0)
    kc_u, kc_m, kc_l = ind.calc_keltner(d['high'], d['low'], d['close'])
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if bb_u is None or kc_u is None or vr is None:
        return False

    squeeze   = bb_u < kc_u and bb_l > kc_l
    breakout  = d['close'][-1] > bb_u
    vol_ok    = vr >= vol_mult
    return not squeeze and breakout and vol_ok


# ═══════════════════════════════
# E8 — Swing Structure Shift
# ═══════════════════════════════
def signal_e8(d, p, _):
    if not ind.enough(d, 50):
        return False
    swing_candles = p.get('swing_candles', 3)
    vwap_period   = p.get('vwap_period', 24)

    sw_low, sw_high = ind.calc_swing_structure(d['high'], d['low'], swing_candles)
    vwap = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], vwap_period)
    if sw_low is None or vwap is None:
        return False

    price = d['close'][-1]
    structure_shift = price > sw_high
    above_vwap      = price > vwap
    return structure_shift and above_vwap


# ═══════════════════════════════
# E9 — Sequential Candle Decay
# ═══════════════════════════════
def signal_e9(d, p, _):
    red_candles = p.get('red_candles', 6)
    vol_mult    = p.get('vol_mult', 1.5)
    if not ind.enough(d, red_candles + 2):
        return False

    consecutive_red = all(
        d['close'][-(i+2)] < d['open'][-(i+2)]
        for i in range(red_candles)
    )
    green_reversal = d['close'][-1] > d['open'][-1]
    vr = ind.calc_volume_ratio(d['volume'], 20)
    vol_ok = vr is not None and vr >= vol_mult
    return consecutive_red and green_reversal and vol_ok


# ═══════════════════════════════
# E10 — Pure Drop Threshold (Control)
# ═══════════════════════════════
def signal_e10(d, p, _):
    drop_pct = p.get('drop_pct', 5.0)
    lookback = p.get('lookback', 24)
    if not ind.enough(d, lookback):
        return False
    drop = ind.calc_price_drop(d['close'], d['high'], lookback)
    return drop is not None and drop >= drop_pct


# ═══════════════════════════════
# E11 — QFL Base Bounce
# ═══════════════════════════════
def signal_e11(d, p, _):
    if not ind.enough(d, 100):
        return False
    base_break_pct = p.get('base_break_pct', 5.0)

    qfl = ind.qfl_base_bounce(d['close'], d['high'], d['low'], d['volume'])
    if qfl is None:
        return False
    if not (qfl['broken'] and qfl['reclaimed'] and qfl['volume_ok']):
        return False

    break_depth = (qfl['base_price'] - min(d['low'][-10:])) / qfl['base_price'] * 100
    return break_depth >= base_break_pct


# ═══════════════════════════════
# E12 — Support/Resistance Reclaim
# ═══════════════════════════════
def signal_e12(d, p, _):
    if not ind.enough(d, 50):
        return False
    reclaim_pct  = p.get('reclaim_pct', 1.0)
    touch_count  = p.get('touch_count', 2)
    vol_mult     = p.get('vol_mult', 1.5)

    sup = ind.detect_support_level(d['close'], d['low'], 48, touch_count)
    vr  = ind.calc_volume_ratio(d['volume'], 20)
    if sup is None or vr is None:
        return False

    price    = d['close'][-1]
    broke    = any(d['low'][-10:-1] < sup)
    reclaimed = price > sup * (1 + reclaim_pct / 100)
    vol_ok   = vr >= vol_mult
    return broke and reclaimed and vol_ok


# ═══════════════════════════════
# E13 — EMA + MACD + RSI Confluence
# ═══════════════════════════════
def signal_e13(d, p, _):
    if not ind.enough(d, 200):
        return False
    fast_ema      = p.get('fast_ema', 12)
    slow_ema      = p.get('slow_ema', 26)
    rsi_threshold = p.get('rsi_threshold', 40)

    ema200 = ind.calc_ema(d['close'], 200)
    rsi    = ind.calc_rsi(d['close'], 14)
    result = ind.calc_macd(d['close'], fast_ema, slow_ema, 9)
    if ema200 is None or rsi is None or result[0] is None:
        return False
    macd, sig, hist, hist_prev = result

    above_ema200  = d['close'][-1] > ema200
    macd_bullish  = macd > sig
    hist_rising   = hist > hist_prev
    rsi_ok        = rsi < rsi_threshold
    return above_ema200 and macd_bullish and hist_rising and rsi_ok


# ═══════════════════════════════
# E14 — Stochastic RSI Pullback
# ═══════════════════════════════
def signal_e14(d, p, _):
    if not ind.enough(d, 100):
        return False
    stoch_threshold   = p.get('stoch_threshold', 20)
    trend_ema         = p.get('trend_ema', 50)
    recovery_closes   = p.get('recovery_closes', 1)

    ema_trend = ind.calc_ema(d['close'], trend_ema)
    k, dk     = ind.calc_stoch_rsi(d['close'])
    if ema_trend is None or k is None:
        return False

    above_trend = d['close'][-1] > ema_trend
    oversold    = k < stoch_threshold
    crossover   = k > dk
    return above_trend and oversold and crossover


# ═══════════════════════════════
# E15 — OBV Divergence
# ═══════════════════════════════
def signal_e15(d, p, _):
    lookback      = p.get('lookback', 48)
    rsi_threshold = p.get('rsi_threshold', 45)
    price_drop    = p.get('price_drop_pct', 5.0)
    if not ind.enough(d, lookback + 20):
        return False

    rsi = ind.calc_rsi(d['close'], 14)
    div = ind.detect_obv_divergence(d['close'], d['volume'], lookback)
    drop = ind.calc_price_drop(d['close'], d['high'], lookback)
    if rsi is None or drop is None:
        return False
    return div and rsi < rsi_threshold and drop >= price_drop


# ═══════════════════════════════
# E16 — RSI Divergence
# ═══════════════════════════════
def signal_e16(d, p, _):
    lookback      = p.get('lookback', 48)
    rsi_threshold = p.get('rsi_threshold', 40)
    if not ind.enough(d, lookback + 20):
        return False

    div = ind.detect_rsi_divergence(d['close'], 14, lookback)
    rsi = ind.calc_rsi(d['close'], 14)
    if rsi is None:
        return False
    green_close = d['close'][-1] > d['open'][-1]
    return div and rsi < rsi_threshold and green_close


# ═══════════════════════════════
# E17 — Liquidity Sweep Reversal
# ═══════════════════════════════
def signal_e17(d, p, _):
    if not ind.enough(d, 50):
        return False
    lookback    = p.get('lookback', 24)
    sweep_pct   = p.get('sweep_pct', 0.5)
    close_upper = p.get('close_upper', 50)

    recent_low  = min(d['low'][-lookback:-1])
    sweep       = d['low'][-1] < recent_low * (1 - sweep_pct / 100)
    candle_range = d['high'][-1] - d['low'][-1]
    close_pos   = (d['close'][-1] - d['low'][-1]) / candle_range * 100 if candle_range > 0 else 0
    recovery    = close_pos >= close_upper
    return sweep and recovery


# ═══════════════════════════════
# E18 — ADX Trend Pullback (High ADX)
# ═══════════════════════════════
def signal_e18(d, p, _):
    if not ind.enough(d, 50):
        return False
    adx_min       = p.get('adx_min', 25)
    rsi_threshold = p.get('rsi_threshold', 40)
    vol_lookback  = p.get('vol_lookback', 100)

    adx = ind.calc_adx(d['high'], d['low'], d['close'])
    rsi = ind.calc_rsi(d['close'], 14)
    vr  = ind.calc_volume_ratio(d['volume'], 20)
    if adx is None or rsi is None:
        return False
    return adx >= adx_min and rsi < rsi_threshold


# ═══════════════════════════════
# E18b — Low ADX Ranging Market
# ═══════════════════════════════
def signal_e18b(d, p, _):
    if not ind.enough(d, 50):
        return False
    adx_max       = p.get('adx_max', 25)
    rsi_threshold = p.get('rsi_threshold', 35)
    lookback      = p.get('lookback', 14)

    adx = ind.calc_adx(d['high'], d['low'], d['close'])
    rsi = ind.calc_rsi(d['close'], 14)
    if adx is None or rsi is None:
        return False
    return adx < adx_max and rsi < rsi_threshold


# ═══════════════════════════════
# E19 — Fibonacci Retracement
# ═══════════════════════════════
def signal_e19(d, p, _):
    if not ind.enough(d, 200):
        return False
    fib_level = p.get('fib_level', '61.8')
    lookback  = p.get('lookback', 48)
    tolerance = 0.005

    ema200 = ind.calc_ema(d['close'], 200)
    fibs   = ind.calc_fibonacci_levels(d['high'], d['low'], lookback)
    vwap   = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], 24)
    if ema200 is None or fibs is None:
        return False

    price     = d['close'][-1]
    fib_price = fibs.get(str(fib_level))
    if fib_price is None:
        return False

    at_level    = abs(price - fib_price) / fib_price <= tolerance
    above_ema   = price > ema200
    green_close = d['close'][-1] > d['open'][-1]
    return at_level and above_ema and green_close


# ═══════════════════════════════
# E20 — VPOC Volume Profile
# ═══════════════════════════════
def signal_e20(d, p, _):
    if not ind.enough(d, 100):
        return False
    profile_days  = p.get('profile_days', 60)
    buffer_pct    = p.get('buffer_pct', 0.5)
    rsi_threshold = p.get('rsi_threshold', 35)
    tolerance     = 0.005

    vpoc = ind.calc_vpoc(d['close'], d['volume'], profile_days)
    if vpoc is None:
        return False

    price    = d['close'][-1]
    at_vpoc  = abs(price - vpoc) / vpoc <= (tolerance + buffer_pct / 100)

    if rsi_threshold:
        rsi = ind.calc_rsi(d['close'], 14)
        if rsi is None or rsi >= rsi_threshold:
            return False
    return at_vpoc


# ═══════════════════════════════
# E21 — Fair Value Gap
# ═══════════════════════════════
def signal_e21(d, p, _):
    if not ind.enough(d, 200):
        return False
    fill_depth    = p.get('fill_depth', 50)
    vol_mult      = p.get('vol_mult', 0)

    ema200 = ind.calc_ema(d['close'], 200)
    fvg    = ind.detect_fair_value_gap(d['high'], d['low'], d['close'])
    if ema200 is None or fvg is None:
        return False

    fill_ok      = fvg['fill_pct'] * 100 >= fill_depth
    above_ema    = d['close'][-1] > ema200
    vol_ok       = True
    if vol_mult > 0:
        vr = ind.calc_volume_ratio(d['volume'], 20)
        vol_ok = vr is not None and vr >= vol_mult
    return fill_ok and above_ema and vol_ok


# ═══════════════════════════════
# E22 — Hammer/Engulfing at Support
# ═══════════════════════════════
def signal_e22(d, p, _):
    if not ind.enough(d, 50):
        return False
    pattern           = p.get('pattern', 'hammer')
    wick_ratio        = p.get('wick_ratio', 2.5)
    support_proximity = p.get('support_proximity', 1.0)

    sup = ind.detect_support_level(d['close'], d['low'])
    if sup is None:
        return False

    price       = d['close'][-1]
    near_support = abs(price - sup) / sup * 100 <= support_proximity

    if pattern == 'hammer':
        pattern_ok = ind.detect_hammer(d['open'], d['high'], d['low'], d['close'], wick_ratio)
    else:
        pattern_ok = ind.detect_engulfing(d['open'], d['close'])
    return near_support and pattern_ok


# ═══════════════════════════════
# E23 — Relative Strength vs BTC
# ═══════════════════════════════
def signal_e23(d, p, btc_data):
    if not ind.enough(d, 50):
        return False
    if btc_data is None:
        return False
    lookback      = p.get('lookback', 48)
    min_outperform = p.get('min_outperform', 4.0)
    rsi_threshold = p.get('rsi_threshold', 45)

    rs  = ind.calc_relative_strength_vs_btc(d['close'], btc_data['close'], lookback)
    rsi = ind.calc_rsi(d['close'], 14)
    if rs is None or rsi is None:
        return False
    return rs >= min_outperform and rsi < rsi_threshold


# ═══════════════════════════════
# E24 — Funding Rate Extreme
# ═══════════════════════════════
def signal_e24(d, p, _):
    """
    E24 - RSI Oversold + Price below SMA (spot version)
    Original funding rate version disabled for spot exchanges.
    """
    if not ind.enough(d, 30):
        return False
    rsi_threshold = p.get('rsi_threshold', 35)
    sma_period    = p.get('sma_period', 24)

    rsi = ind.calc_rsi(d['close'], 14)
    sma = ind.calc_sma(d['close'], sma_period)
    if rsi is None or sma is None:
        return False
    return rsi < rsi_threshold and d['close'][-1] < sma


# ═══════════════════════════════
# E25 — Supertrend + RSI
# ═══════════════════════════════
def signal_e25(d, p, _):
    if not ind.enough(d, 50):
        return False
    atr_period    = p.get('atr_period', 14)
    atr_mult      = p.get('atr_mult', 3.0)
    rsi_threshold = p.get('rsi_threshold', 35)

    st_dir, st_val = ind.calc_supertrend(d['high'], d['low'], d['close'],
                                          atr_period, atr_mult)
    rsi = ind.calc_rsi(d['close'], 14)
    if st_dir is None or rsi is None:
        return False
    return st_dir == 1 and rsi < rsi_threshold


# ═══════════════════════════════
# E26 — Ichimoku Cloud Simplified
# ═══════════════════════════════
def signal_e26(d, p, _):
    if not ind.enough(d, 100):
        return False
    conversion    = p.get('conversion', 9)
    base          = p.get('base', 26)
    rsi_threshold = p.get('rsi_threshold', 40)

    ichi = ind.calc_ichimoku(d['high'], d['low'], conversion, base)
    rsi  = ind.calc_rsi(d['close'], 14)
    if ichi is None or rsi is None:
        return False

    price         = d['close'][-1]
    cloud_top     = max(ichi['senkou_a'], ichi['senkou_b'])
    below_cloud   = price < cloud_top
    future_bullish = ichi['cloud_bullish']
    rsi_ok        = rsi < rsi_threshold
    return below_cloud and future_bullish and rsi_ok


# ═══════════════════════════════
# SIGNAL MAP
# ═══════════════════════════════
def signal_bm_simple(d, p, coin):
    """BM_SIMPLE - buy on any drop_pct drop"""
    if not ind.enough(d, 2):
        return False
    drop_pct = p.get('drop_pct', 7.0)
    if d['close'][-2] == 0:
        return False
    drop = (d['close'][-2] - d['close'][-1]) / d['close'][-2] * 100
    return drop >= drop_pct

def signal_bm_static(d, p, coin):
    """BM_STATIC - fixed spacing entry"""
    if not ind.enough(d, 2):
        return False
    spacing = p.get('spacing', 1.0)
    if d['close'][-2] == 0:
        return False
    drop = (d['close'][-2] - d['close'][-1]) / d['close'][-2] * 100
    return drop >= spacing

def signal_bm_random(d, p, coin):
    """BM_RANDOM - random entry for baseline comparison"""
    import random
    return random.random() < 0.01

def signal_bm_hold(d, p, coin):
    """BM_HOLD - buy and hold specific coin"""
    target = p.get('coin', 'BTC')
    return coin.upper() == target.upper()

SIGNAL_MAP = {
    'E1':   signal_e1,
    'E2':   signal_e2,
    'E3':   signal_e3,
    'E4':   signal_e4,
    'E5':   signal_e5,
    'E6':   signal_e6,
    'E7':   signal_e7,
    'E8':   signal_e8,
    'E9':   signal_e9,
    'E10':  signal_e10,
    'E11':  signal_e11,
    'E12':  signal_e12,
    'E13':  signal_e13,
    'E14':  signal_e14,
    'E15':  signal_e15,
    'E16':  signal_e16,
    'E17':  signal_e17,
    'E18':  signal_e18,
    'E18b': signal_e18b,
    'E19':  signal_e19,
    'E20':  signal_e20,
    'E21':  signal_e21,
    'E22':  signal_e22,
    'E23':  signal_e23,
    'E24':  signal_e24,
    'E25':  signal_e25,
    'E26':  signal_e26,
    'BM_SIMPLE': signal_bm_simple,
    'BM_STATIC': signal_bm_static,
    'BM_RANDOM': signal_bm_random,
    'BM_HOLD':   signal_bm_hold,
}
