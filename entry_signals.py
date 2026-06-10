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

    require_btc_safe = p.get('require_btc_safe', False)
    rs  = ind.calc_relative_strength_vs_btc(d['close'], btc_data['close'], lookback)
    rsi = ind.calc_rsi(d['close'], 14)
    if rs is None or rsi is None:
        return False
    # Optional BTC regime filter
    if require_btc_safe:
        btc_rsi = ind.calc_rsi(btc_data['close'], 14)
        if btc_rsi is None or btc_rsi < 45:
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

# ═══════════════════════════════
# E27 — MACD Histogram Reversal
# ═══════════════════════════════
def signal_e27(d, p, _):
    if not ind.enough(d, 50):
        return False
    fast = p.get('fast', 12)
    slow = p.get('slow', 26)
    signal_period = p.get('signal_period', 9)
    mode = p.get('mode', 'histogram')

    macd_data = ind.calc_macd(d['close'], fast, slow, signal_period)
    if macd_data is None:
        return False
    hist = macd_data.get('histogram', [])
    if len(hist) < 3:
        return False
    if mode == 'histogram':
        return hist[-2] < hist[-1] < 0 and hist[-3] < hist[-2]
    elif mode == 'cross_zero':
        return hist[-2] < 0 and hist[-1] > 0
    return False

# ═══════════════════════════════
# E28 — Keltner Channel Mean Reversion
# ═══════════════════════════════
def signal_e28(d, p, _):
    if not ind.enough(d, 60):
        return False
    ema_period = p.get('ema_period', 20)
    atr_mult   = p.get('atr_mult', 2.0)
    rsi_max    = p.get('rsi_max', 35)

    kc = ind.calc_keltner(d['high'], d['low'], d['close'], ema_period, atr_mult)
    rsi = ind.calc_rsi(d['close'], 14)
    if kc is None or rsi is None:
        return False
    return d['close'][-1] < kc['lower'] and rsi < rsi_max

# ═══════════════════════════════
# E29 — Donchian Breakout Pullback
# ═══════════════════════════════
def signal_e29(d, p, _):
    if not ind.enough(d, 120):
        return False
    breakout_high = p.get('breakout_high', 20)
    pullback_ema  = p.get('pullback_ema', 10)
    rsi_min       = p.get('rsi_min', 45)

    import numpy as np
    highest = max(d['high'][-breakout_high:])
    ema = ind.calc_ema(d['close'], pullback_ema)
    rsi = ind.calc_rsi(d['close'], 14)
    if ema is None or rsi is None:
        return False
    was_above = any(c > highest * 0.95 for c in d['close'][-breakout_high:-5])
    pullback = d['close'][-1] < ema
    return was_above and pullback and rsi > rsi_min

# ═══════════════════════════════
# E30 — Hurst Exponent Mean Reversion
# ═══════════════════════════════
def signal_e30(d, p, _):
    if not ind.enough(d, 120):
        return False
    hurst_max = p.get('hurst_max', 0.45)
    lookback  = p.get('lookback', 100)
    drop_pct  = p.get('drop_pct', 5.0)

    import numpy as np
    prices = np.array(d['close'][-lookback:])
    # Approximate Hurst exponent using R/S analysis
    lags = [2, 4, 8, 16, 32]
    rs_vals = []
    for lag in lags:
        if lag >= len(prices):
            continue
        ts = prices[-lag:]
        mean = np.mean(ts)
        deviation = np.cumsum(ts - mean)
        r = np.max(deviation) - np.min(deviation)
        s = np.std(ts)
        if s > 0:
            rs_vals.append(r/s)
    if len(rs_vals) < 3:
        return False
    hurst = np.polyfit(np.log(lags[:len(rs_vals)]), np.log(rs_vals), 1)[0]

    if hurst >= hurst_max:
        return False
    if d['close'][-2] == 0:
        return False
    drop = (d['close'][-lookback//4] - d['close'][-1]) / d['close'][-lookback//4] * 100
    return drop >= drop_pct

# ═══════════════════════════════
# E31 — Kalman Filter Deviation
# ═══════════════════════════════
def signal_e31(d, p, _):
    if not ind.enough(d, 50):
        return False
    noise_cov   = p.get('noise_cov', 0.01)
    deviation   = p.get('deviation_pct', 5.0)

    import numpy as np
    prices = np.array(d['close'][-50:])
    # Simple Kalman filter
    x = prices[0]
    P = 1.0
    Q = noise_cov
    R = 0.1
    estimates = []
    for z in prices:
        P = P + Q
        K = P / (P + R)
        x = x + K * (z - x)
        P = (1 - K) * P
        estimates.append(x)
    kalman_val = estimates[-1]
    if kalman_val == 0:
        return False
    dev = (kalman_val - prices[-1]) / kalman_val * 100
    return dev >= deviation

# ═══════════════════════════════
# E32 — Session Killzone Sweep
# ═══════════════════════════════
def signal_e32(d, p, _):
    if not ind.enough(d, 5):
        return False
    import datetime
    session   = p.get('session', 'london_ny')
    drop_pct  = p.get('drop_pct', 3.0)
    vol_mult  = p.get('vol_mult', 1.5)

    hour = datetime.datetime.utcnow().hour
    sessions = {
        'asia_london': list(range(7, 10)),
        'london_ny':   list(range(13, 16)),
        'ny_close':    list(range(20, 23)),
    }
    if hour not in sessions.get(session, []):
        return False
    if d['close'][-2] == 0:
        return False
    drop = (d['close'][-2] - d['close'][-1]) / d['close'][-2] * 100
    vr = ind.calc_volume_ratio(d['volume'], 20)
    return drop >= drop_pct and (vr is None or vr >= vol_mult)

# ═══════════════════════════════
# E33 — Williams %R Reversal
# ═══════════════════════════════
def signal_e33(d, p, _):
    if not ind.enough(d, 20):
        return False
    wr_threshold = p.get('wr_threshold', -90)
    confirmation = p.get('confirmation', 'green')

    import numpy as np
    period = 14
    highs = np.array(d['high'][-period:])
    lows  = np.array(d['low'][-period:])
    hh = np.max(highs)
    ll = np.min(lows)
    if hh == ll:
        return False
    wr = (hh - d['close'][-1]) / (hh - ll) * -100
    if wr > wr_threshold:
        return False
    if confirmation == 'green':
        return d['close'][-1] > d['open'][-1]
    elif confirmation == 'rsi':
        rsi = ind.calc_rsi(d['close'], 14)
        return rsi is not None and rsi > 35
    elif confirmation == 'vwap':
        vwap = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], 24)
        return vwap is not None and d['close'][-1] > vwap
    return True

# ═══════════════════════════════
# E34 — Choppiness Index Exhaustion
# ═══════════════════════════════
def signal_e34(d, p, _):
    if not ind.enough(d, 30):
        return False
    import numpy as np
    lookback  = p.get('lookback', 14)
    chop_min  = p.get('chop_min', 61.8)
    drop_pct  = p.get('drop_pct', 3.0)

    highs = np.array(d['high'][-lookback:])
    lows  = np.array(d['low'][-lookback:])
    closes = np.array(d['close'][-lookback:])
    tr = np.maximum(highs[1:] - lows[1:],
         np.maximum(np.abs(highs[1:] - closes[:-1]),
                    np.abs(lows[1:] - closes[:-1])))
    atr_sum = np.sum(tr)
    hh = np.max(highs)
    ll = np.min(lows)
    if (hh - ll) == 0 or atr_sum == 0:
        return False
    chop = 100 * np.log10(atr_sum / (hh - ll)) / np.log10(lookback)
    if chop < chop_min:
        return False
    if d['close'][-2] == 0:
        return False
    drop = (d['close'][-lookback] - d['close'][-1]) / d['close'][-lookback] * 100
    return drop >= drop_pct

# ═══════════════════════════════
# E35 — Fisher Transform Reversal
# ═══════════════════════════════
def signal_e35(d, p, _):
    if not ind.enough(d, 30):
        return False
    import numpy as np
    period  = p.get('period', 14)
    trigger = p.get('trigger', -2.0)

    highs  = np.array(d['high'][-period:])
    lows   = np.array(d['low'][-period:])
    closes = np.array(d['close'][-period:])
    hh = np.max(highs)
    ll = np.min(lows)
    if hh == ll:
        return False
    val = 2 * ((closes[-1] - ll) / (hh - ll)) - 1
    val = min(max(val, -0.999), 0.999)
    fisher = 0.5 * np.log((1 + val) / (1 - val))
    val2 = 2 * ((closes[-2] - ll) / (hh - ll)) - 1
    val2 = min(max(val2, -0.999), 0.999)
    fisher2 = 0.5 * np.log((1 + val2) / (1 - val2))
    return fisher < trigger and fisher > fisher2  # hooking up

# ═══════════════════════════════
# E36 — ALMA Deviation Entry
# ═══════════════════════════════
def signal_e36(d, p, _):
    if not ind.enough(d, 60):
        return False
    import numpy as np
    window    = p.get('window', 21)
    offset    = p.get('offset', 0.85)
    sigma     = p.get('sigma', 6.0)
    drop_pct  = p.get('drop_pct', 3.0)

    closes = np.array(d['close'][-window:])
    m = offset * (window - 1)
    s = window / sigma
    weights = np.exp(-((np.arange(window) - m) ** 2) / (2 * s * s))
    weights /= weights.sum()
    alma = np.dot(weights, closes)
    if alma == 0:
        return False
    dev = (alma - d['close'][-1]) / alma * 100
    return dev >= drop_pct

# ═══════════════════════════════
# E37 — BTC Regime Filter
# ═══════════════════════════════
def signal_e37(d, p, btc_data):
    if not ind.enough(d, 20):
        return False
    if btc_data is None or not ind.enough(btc_data, 200):
        return True  # no BTC data - allow entry
    filter_type = p.get('filter', 'ema200')
    drop_pct    = p.get('drop_pct', 5.0)

    btc_close = btc_data['close']
    if filter_type == 'ema200':
        ema = ind.calc_ema(btc_close, 200)
        if ema is None or btc_close[-1] < ema:
            return False
    elif filter_type == 'ema100':
        ema = ind.calc_ema(btc_close, 100)
        if ema is None or btc_close[-1] < ema:
            return False
    elif filter_type == 'rsi45':
        rsi = ind.calc_rsi(btc_close, 14)
        if rsi is None or rsi < 45:
            return False
    elif filter_type == 'drop3':
        if btc_close[-2] > 0:
            btc_drop = (btc_close[-25] - btc_close[-1]) / btc_close[-25] * 100
            if btc_drop > 3:
                return False

    if d['close'][-2] == 0:
        return False
    drop = (d['close'][-10] - d['close'][-1]) / d['close'][-10] * 100
    return drop >= drop_pct

# ═══════════════════════════════
# E38 — Relative Volume Breakout
# ═══════════════════════════════
def signal_e38(d, p, _):
    if not ind.enough(d, 50):
        return False
    vol_mult  = p.get('vol_mult', 3.0)
    drop_pct  = p.get('drop_pct', 5.0)
    rsi_max   = p.get('rsi_max', 40)

    vr = ind.calc_volume_ratio(d['volume'], 20)
    rsi = ind.calc_rsi(d['close'], 14)
    if vr is None or rsi is None:
        return False
    if d['close'][-2] == 0:
        return False
    drop = (d['close'][-5] - d['close'][-1]) / d['close'][-5] * 100
    return vr >= vol_mult and drop >= drop_pct and rsi < rsi_max

# ═══════════════════════════════
# E39 — MFI Oversold Bounce
# ═══════════════════════════════
def signal_e39(d, p, _):
    if not ind.enough(d, 30):
        return False
    import numpy as np
    mfi_max  = p.get('mfi_max', 20)
    rsi_max  = p.get('rsi_max', 35)
    vol_mult = p.get('vol_mult', 1.0)
    period = 14

    tp = (np.array(d['high'][-period-1:]) + np.array(d['low'][-period-1:]) + np.array(d['close'][-period-1:])) / 3
    raw_mf = tp * np.array(d['volume'][-period-1:])
    pos_mf = sum(raw_mf[i] for i in range(1, period+1) if tp[i] > tp[i-1])
    neg_mf = sum(raw_mf[i] for i in range(1, period+1) if tp[i] < tp[i-1])
    if neg_mf == 0:
        return False
    mfi = 100 - (100 / (1 + pos_mf/neg_mf))
    rsi = ind.calc_rsi(d['close'], 14)
    vr  = ind.calc_volume_ratio(d['volume'], 20)
    if rsi is None:
        return False
    return mfi < mfi_max and rsi < rsi_max and (vr is None or vr >= vol_mult)

# ═══════════════════════════════
# E40 — Wick Capitulation
# ═══════════════════════════════
def signal_e40(d, p, _):
    if not ind.enough(d, 10):
        return False
    wick_ratio = p.get('wick_ratio', 3.0)
    vol_mult   = p.get('vol_mult', 2.0)
    drop_pct   = p.get('drop_pct', 5.0)

    o, h, l, c = d['open'][-1], d['high'][-1], d['low'][-1], d['close'][-1]
    body = abs(c - o)
    lower_wick = min(o, c) - l
    if body == 0:
        return False
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if d['close'][-5] == 0:
        return False
    drop = (d['close'][-5] - c) / d['close'][-5] * 100
    return (lower_wick / body >= wick_ratio and
            (vr is None or vr >= vol_mult) and
            drop >= drop_pct)

# ═══════════════════════════════
# E41 — TTM Squeeze Fakeout
# ═══════════════════════════════
def signal_e41(d, p, _):
    if not ind.enough(d, 30):
        return False
    import numpy as np
    bb_period = p.get('bb_period', 20)
    kc_mult   = p.get('kc_mult', 1.5)
    fakeout   = p.get('fakeout_pct', 3.0)

    bb = ind.calc_bollinger(d['close'], bb_period, 2.0)
    kc = ind.calc_keltner(d['high'], d['low'], d['close'], bb_period, kc_mult)
    if bb is None or kc is None:
        return False
    # Squeeze: BB inside KC
    squeeze = bb['upper'] < kc['upper'] and bb['lower'] > kc['lower']
    if not squeeze:
        return False
    if d['close'][-4] == 0:
        return False
    drop = (d['close'][-4] - d['close'][-1]) / d['close'][-4] * 100
    return drop >= fakeout

# ═══════════════════════════════
# E42 — Chaikin Money Flow Divergence
# ═══════════════════════════════
def signal_e42(d, p, _):
    if not ind.enough(d, 60):
        return False
    import numpy as np
    period    = p.get('period', 21)
    cmf_min   = p.get('cmf_min', 0.0)
    drop_pct  = p.get('drop_pct', 5.0)

    highs  = np.array(d['high'][-period:])
    lows   = np.array(d['low'][-period:])
    closes = np.array(d['close'][-period:])
    vols   = np.array(d['volume'][-period:])
    hl     = highs - lows
    hl[hl == 0] = 1e-9
    mfm = ((closes - lows) - (highs - closes)) / hl
    mfv = mfm * vols
    cmf = np.sum(mfv) / np.sum(vols) if np.sum(vols) > 0 else 0
    if d['close'][-period] == 0:
        return False
    drop = (d['close'][-period] - d['close'][-1]) / d['close'][-period] * 100
    return cmf > cmf_min and drop >= drop_pct

# ═══════════════════════════════
# E43 — QQE Momentum
# ═══════════════════════════════
def signal_e43(d, p, _):
    if not ind.enough(d, 50):
        return False
    import numpy as np
    qqe_factor = p.get('qqe_factor', 4.236)
    rsi_period = 14

    rsi = ind.calc_rsi(d['close'], rsi_period)
    if rsi is None:
        return False
    # Smooth RSI
    closes = np.array(d['close'][-30:])
    rsi_vals = []
    for i in range(14, len(closes)):
        r = ind.calc_rsi(closes[:i+1].tolist(), rsi_period)
        if r is not None:
            rsi_vals.append(r)
    if len(rsi_vals) < 5:
        return False
    rsi_smooth = sum(rsi_vals[-5:]) / 5
    atr_rsi = max(rsi_vals[-5:]) - min(rsi_vals[-5:])
    qqe_line = rsi_smooth - qqe_factor * atr_rsi
    return rsi < 30 and qqe_line < 30 and rsi > rsi_vals[-2] if len(rsi_vals) >= 2 else False

# ═══════════════════════════════
# E44 — Multi-Signal Score Bot
# ═══════════════════════════════
def signal_e44(d, p, btc_data):
    if not ind.enough(d, 50):
        return False
    min_score   = p.get('min_score', 3)
    drop_pct    = p.get('drop_pct', 3.0)

    score = 0
    # RSI oversold
    rsi = ind.calc_rsi(d['close'], 14)
    if rsi is not None and rsi < 35: score += 1
    # Price below VWAP
    vwap = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], 24)
    if vwap is not None and d['close'][-1] < vwap * 0.97: score += 1
    # Volume spike
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if vr is not None and vr > 2.0: score += 1
    # Price drop
    if d['close'][-10] > 0:
        drop = (d['close'][-10] - d['close'][-1]) / d['close'][-10] * 100
        if drop >= drop_pct: score += 1
    # BTC safe
    if btc_data is not None and ind.enough(btc_data, 50):
        btc_rsi = ind.calc_rsi(btc_data['close'], 14)
        if btc_rsi is not None and btc_rsi > 40: score += 1
    # BB lower band
    bb = ind.calc_bollinger(d['close'], 20, 2.0)
    if bb is not None and d['close'][-1] < bb['lower']: score += 1

    return score >= min_score

# ═══════════════════════════════
# E45 — Ensemble Best Methods
# ═══════════════════════════════
def signal_e45(d, p, btc_data):
    """Combines E1 + E10 + E22 signals"""
    if not ind.enough(d, 50):
        return False
    mode = p.get('mode', 'any2')

    results = []
    # E1-style: RSI + VWAP
    rsi = ind.calc_rsi(d['close'], 14)
    vwap = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], 24)
    if rsi is not None and vwap is not None:
        results.append(rsi < 30 and d['close'][-1] < vwap * 0.97)
    # E10-style: price drop
    if d['close'][-12] > 0:
        drop = (d['close'][-12] - d['close'][-1]) / d['close'][-12] * 100
        results.append(drop >= 5.0)
    # Volume spike
    vr = ind.calc_volume_ratio(d['volume'], 20)
    results.append(vr is not None and vr > 2.5)

    hits = sum(1 for r in results if r)
    if mode == 'any2':
        return hits >= 2
    elif mode == 'all':
        return all(results)
    return hits >= 1

# ═══════════════════════════════
# E46 — CVD Approximation (Volume Delta)
# ═══════════════════════════════
def signal_e46(d, p, _):
    """Approximates CVD divergence using price direction + volume"""
    if not ind.enough(d, 50):
        return False
    import numpy as np
    lookback  = p.get('lookback', 24)
    drop_pct  = p.get('drop_pct', 5.0)
    div_pct   = p.get('div_pct', 2.0)

    closes = np.array(d['close'][-lookback:])
    opens  = np.array(d['open'][-lookback:])
    vols   = np.array(d['volume'][-lookback:])
    # Approximate CVD: buy vol when green, sell vol when red
    delta = np.where(closes > opens, vols, -vols)
    cvd = np.cumsum(delta)
    # Price makes lower low but CVD makes higher low
    price_drop = (closes[0] - closes[-1]) / closes[0] * 100 if closes[0] > 0 else 0
    cvd_change = (cvd[-1] - cvd[0]) / (abs(cvd[0]) + 1) * 100
    return price_drop >= drop_pct and cvd_change > div_pct

# ═══════════════════════════════
# E47 — ATR Expansion Breakout
# ═══════════════════════════════
def signal_e47(d, p, _):
    if not ind.enough(d, 30):
        return False
    atr_mult  = p.get('atr_mult', 2.0)
    vol_mult  = p.get('vol_mult', 2.0)

    atr = ind.calc_atr(d['high'], d['low'], d['close'], 14)
    avg_atr = ind.calc_atr(d['high'], d['low'], d['close'], 50)
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if atr is None or avg_atr is None or avg_atr == 0:
        return False
    atr_expansion = atr / avg_atr
    rsi = ind.calc_rsi(d['close'], 14)
    return (atr_expansion >= atr_mult and
            (vr is None or vr >= vol_mult) and
            rsi is not None and rsi < 40)


# ═══════════════════════════════
# E48 — Volume Before Price
# Price flat but volume exploding = smart money entering
# ═══════════════════════════════
def signal_e48(d, p, _):
    if not ind.enough(d, 50):
        return False
    import numpy as np
    vol_mult  = p.get('vol_mult', 3.0)
    max_price_move = p.get('max_price_move', 3.0)  # price NOT already pumped

    vr = ind.calc_volume_ratio(d['volume'], 20)
    if vr is None or vr < vol_mult:
        return False
    if d['close'][-5] == 0:
        return False
    price_move = abs(d['close'][-1] - d['close'][-5]) / d['close'][-5] * 100
    # Volume spiking but price NOT yet moved much
    return price_move < max_price_move

# ═══════════════════════════════
# E49 — Relative Strength Explosion
# Coin moving much stronger than BTC
# ═══════════════════════════════
def signal_e49(d, p, btc_data):
    if not ind.enough(d, 10):
        return False
    if btc_data is None or not ind.enough(btc_data, 10):
        return False
    min_strength = p.get('min_strength', 5.0)
    lookback = p.get('lookback', 4)

    if d['close'][-lookback] == 0 or btc_data['close'][-lookback] == 0:
        return False
    coin_return = (d['close'][-1] - d['close'][-lookback]) / d['close'][-lookback] * 100
    btc_return  = (btc_data['close'][-1] - btc_data['close'][-lookback]) / btc_data['close'][-lookback] * 100
    strength = coin_return - btc_return
    return strength >= min_strength and coin_return > 0

# ═══════════════════════════════
# E50 — Compression Breakout
# BB squeeze → breakout with volume
# ═══════════════════════════════
def signal_e50(d, p, _):
    if not ind.enough(d, 50):
        return False
    import numpy as np
    compression_days = p.get('compression_days', 5)
    vol_mult = p.get('vol_mult', 3.0)

    # BB width compression
    bb = ind.calc_bollinger(d['close'], 20, 2.0)
    if bb is None:
        return False
    bb_width = (bb['upper'] - bb['lower']) / d['close'][-1] * 100

    # Historical BB widths
    widths = []
    closes = d['close']
    for i in range(compression_days * 24, len(closes) - 1):
        bb_h = ind.calc_bollinger(closes[:i], 20, 2.0)
        if bb_h:
            widths.append((bb_h['upper'] - bb_h['lower']) / closes[i] * 100)
        if len(widths) >= 10:
            break

    if not widths:
        return False
    avg_width = sum(widths) / len(widths)

    # Currently compressed AND price breaking up
    compressed = bb_width < avg_width * 0.7
    vr = ind.calc_volume_ratio(d['volume'], 20)
    breakout = d['close'][-1] > bb['upper']
    return compressed and breakout and (vr is None or vr >= vol_mult)

# ═══════════════════════════════
# E51 — Top Gainers Pullback
# Buy after first pump + controlled pullback
# ═══════════════════════════════
def signal_e51(d, p, _):
    if not ind.enough(d, 30):
        return False
    pump_pct    = p.get('pump_pct', 20.0)
    pullback_pct = p.get('pullback_pct', 8.0)
    max_pullback = p.get('max_pullback', 20.0)

    # Find recent peak
    import numpy as np
    closes = np.array(d['close'][-24:])
    peak_idx = np.argmax(closes)
    peak = closes[peak_idx]
    current = closes[-1]
    low_before_peak = min(closes[:peak_idx+1]) if peak_idx > 0 else closes[0]

    if low_before_peak == 0 or peak == 0:
        return False

    pump = (peak - low_before_peak) / low_before_peak * 100
    pullback = (peak - current) / peak * 100

    return (pump >= pump_pct and
            pullback >= pullback_pct and
            pullback <= max_pullback and
            peak_idx < len(closes) - 1)  # peak not at current candle

# ═══════════════════════════════
# E52 — Wyckoff Flatline Breakout
# Dead zone → violent breakout
# ═══════════════════════════════
def signal_e52(d, p, _):
    if not ind.enough(d, 80):
        return False
    import numpy as np
    flatline_hours = p.get('flatline_hours', 48)
    max_range_pct  = p.get('max_range_pct', 3.0)
    vol_mult       = p.get('vol_mult', 5.0)

    flat_prices = d['close'][-flatline_hours:-1]
    if not flat_prices or min(flat_prices) == 0:
        return False

    price_range = (max(flat_prices) - min(flat_prices)) / min(flat_prices) * 100
    if price_range > max_range_pct:
        return False

    # Now breaking out
    resistance = max(flat_prices)
    breakout = d['close'][-1] > resistance
    vr = ind.calc_volume_ratio(d['volume'], 20)
    return breakout and (vr is None or vr >= vol_mult)

# ═══════════════════════════════
# E53 — Volatility Expansion Chain
# ATR expanding before price moves
# ═══════════════════════════════
def signal_e53(d, p, _):
    if not ind.enough(d, 60):
        return False
    atr_increase = p.get('atr_increase', 0.5)  # 50% increase
    vol_mult     = p.get('vol_mult', 2.0)

    atr_now = ind.calc_atr(d['high'], d['low'], d['close'], 14)
    atr_prev = ind.calc_atr(d['high'][:-6], d['low'][:-6], d['close'][:-6], 14)
    if atr_now is None or atr_prev is None or atr_prev == 0:
        return False

    atr_expansion = (atr_now - atr_prev) / atr_prev
    vr = ind.calc_volume_ratio(d['volume'], 20)
    rsi = ind.calc_rsi(d['close'], 14)

    return (atr_expansion >= atr_increase and
            (vr is None or vr >= vol_mult) and
            rsi is not None and rsi > 45)  # not oversold, momentum building

# ═══════════════════════════════
# E54 — Failed Breakdown Reversal
# Support breaks → everyone panic sells → price reclaims
# ═══════════════════════════════
def signal_e54(d, p, _):
    if not ind.enough(d, 30):
        return False
    breakdown_pct = p.get('breakdown_pct', 3.0)
    reclaim_pct   = p.get('reclaim_pct', 0.5)

    # Find recent support (low of last 20 candles excluding last 3)
    import numpy as np
    support = min(d['low'][-20:-3])
    if support == 0:
        return False

    # Price broke below support
    broke_below = any(c < support for c in d['close'][-5:-1])
    if not broke_below:
        return False

    # How far below
    min_price = min(d['close'][-5:-1])
    breakdown = (support - min_price) / support * 100
    if breakdown < breakdown_pct:
        return False

    # Now reclaimed support
    reclaimed = d['close'][-1] > support
    vr = ind.calc_volume_ratio(d['volume'], 20)
    return reclaimed and (vr is None or vr >= 1.5)

# ═══════════════════════════════
# E55 — Relative Volume Leaderboard
# Coin has highest vol/avg ratio = pump candidate
# ═══════════════════════════════
def signal_e55(d, p, _):
    if not ind.enough(d, 30):
        return False
    import numpy as np
    min_vol_mult = p.get('min_vol_mult', 5.0)
    rsi_min      = p.get('rsi_min', 40)
    rsi_max      = p.get('rsi_max', 70)

    vr = ind.calc_volume_ratio(d['volume'], 20)
    rsi = ind.calc_rsi(d['close'], 14)
    if vr is None or rsi is None:
        return False
    # High volume but RSI not yet overbought = early pump
    return vr >= min_vol_mult and rsi_min <= rsi <= rsi_max

# ═══════════════════════════════
# E56 — Smart Money Footprint
# Price flat but OBV + volume rising = accumulation
# ═══════════════════════════════
def signal_e56(d, p, _):
    if not ind.enough(d, 30):
        return False
    import numpy as np
    max_price_move = p.get('max_price_move', 2.0)
    vol_mult       = p.get('vol_mult', 2.0)
    lookback       = p.get('lookback', 10)

    closes = np.array(d['close'][-lookback:])
    volumes = np.array(d['volume'][-lookback:])

    if closes[0] == 0:
        return False

    # Price relatively flat
    price_move = abs(closes[-1] - closes[0]) / closes[0] * 100
    if price_move > max_price_move:
        return False

    # Volume trending up (later candles have more volume)
    early_vol = np.mean(volumes[:lookback//2])
    late_vol  = np.mean(volumes[lookback//2:])
    vol_growing = late_vol > early_vol * vol_mult

    # OBV rising
    obv = 0
    obv_vals = []
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv += volumes[i]
        elif closes[i] < closes[i-1]:
            obv -= volumes[i]
        obv_vals.append(obv)
    obv_rising = len(obv_vals) >= 4 and obv_vals[-1] > obv_vals[-4]

    return vol_growing and obv_rising

# ═══════════════════════════════
# E57 — Consensus Pump Engine
# Multiple signals agree = high confidence pump
# ═══════════════════════════════
def signal_e57(d, p, btc_data):
    if not ind.enough(d, 50):
        return False
    min_votes = p.get('min_votes', 4)

    votes = 0
    # Vote 1: Volume surge
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if vr and vr > 3.0: votes += 1
    # Vote 2: Relative strength vs BTC
    if btc_data and ind.enough(btc_data, 5):
        if d['close'][-5] > 0 and btc_data['close'][-5] > 0:
            coin_r = (d['close'][-1]-d['close'][-5])/d['close'][-5]*100
            btc_r  = (btc_data['close'][-1]-btc_data['close'][-5])/btc_data['close'][-5]*100
            if coin_r - btc_r > 3: votes += 1
    # Vote 3: RSI momentum (not oversold, building)
    rsi = ind.calc_rsi(d['close'], 14)
    if rsi and 45 < rsi < 75: votes += 1
    # Vote 4: ATR expanding
    atr = ind.calc_atr(d['high'], d['low'], d['close'], 14)
    atr_slow = ind.calc_atr(d['high'], d['low'], d['close'], 28)
    if atr and atr_slow and atr_slow > 0 and atr/atr_slow > 1.2: votes += 1
    # Vote 5: Price above VWAP
    vwap = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], 24)
    if vwap and d['close'][-1] > vwap: votes += 1
    # Vote 6: BB squeeze breaking out
    bb = ind.calc_bollinger(d['close'], 20, 2.0)
    if bb and d['close'][-1] > bb['upper']: votes += 1
    # Vote 7: OBV positive
    closes = d['close'][-10:]
    vols = d['volume'][-10:]
    obv = sum(vols[i] if closes[i]>closes[i-1] else -vols[i] for i in range(1,len(closes)))
    if obv > 0: votes += 1

    return votes >= min_votes


# ═══════════════════════════════
# E59 — Volume Acceleration (2nd Derivative)
# Volume growth itself is accelerating = pre-pump signal
# ═══════════════════════════════
def signal_e59(d, p, _):
    if not ind.enough(d, 10):
        return False
    import numpy as np
    accel_mult    = p.get('accel_mult', 2.0)
    min_vol_usd   = p.get('min_vol_usd', 50000)
    interval      = p.get('interval', 3)  # candles per interval

    vols = np.array(d['volume'][-interval*3:])
    closes = np.array(d['close'][-interval*3:])
    if len(vols) < interval * 3:
        return False

    # Split into 3 intervals
    v1 = np.sum(vols[:interval])
    v2 = np.sum(vols[interval:interval*2])
    v3 = np.sum(vols[interval*2:])

    if v1 == 0 or v2 == 0:
        return False

    # Volume must be accelerating: v3 > v2 > v1 with multiplier
    accel = v3 / v2 if v2 > 0 else 0
    prev_accel = v2 / v1 if v1 > 0 else 0

    # Min volume check (approximate USD)
    avg_price = float(np.mean(closes))
    vol_usd = v3 * avg_price

    return (accel >= accel_mult and
            v3 > v2 and v2 > v1 and
            vol_usd >= min_vol_usd)

# ═══════════════════════════════
# E60 — Consecutive Higher Lows
# Buyers stepping higher = accumulation before pump
# ═══════════════════════════════
def signal_e60(d, p, _):
    if not ind.enough(d, 20):
        return False
    import numpy as np
    min_higher_lows = p.get('min_higher_lows', 3)
    min_step_pct    = p.get('min_step_pct', 0.3)

    lows = d['low'][-10:]
    higher_lows = 0
    for i in range(1, len(lows)):
        if lows[i] > lows[i-1] * (1 + min_step_pct/100):
            higher_lows += 1
        else:
            higher_lows = 0  # reset on break
        if higher_lows >= min_higher_lows:
            return True
    return False

# ═══════════════════════════════
# E61 — Sudden Ranking Change
# Coin's relative strength rank improving rapidly
# ═══════════════════════════════
def signal_e61(d, p, btc_data):
    if not ind.enough(d, 20):
        return False
    if btc_data is None or not ind.enough(btc_data, 20):
        return False
    import numpy as np
    min_strength_gain = p.get('min_strength_gain', 5.0)
    lookback          = p.get('lookback', 6)

    # Calculate relative strength improvement over lookback
    if d['close'][-lookback] == 0 or btc_data['close'][-lookback] == 0:
        return False

    coin_return_now  = (d['close'][-1] - d['close'][-lookback]) / d['close'][-lookback] * 100
    coin_return_prev = (d['close'][-lookback] - d['close'][-lookback*2]) / d['close'][-lookback*2] * 100 if len(d['close']) >= lookback*2 else 0
    btc_return_now   = (btc_data['close'][-1] - btc_data['close'][-lookback]) / btc_data['close'][-lookback] * 100

    rs_now  = coin_return_now - btc_return_now
    rs_gain = rs_now - coin_return_prev

    return rs_gain >= min_strength_gain and coin_return_now > 0

# ═══════════════════════════════
# E62 — Multi-Timeframe Strength
# Strong on short TF but not yet on long TF = early signal
# ═══════════════════════════════
def signal_e62(d, p, btc_data):
    if not ind.enough(d, 50):
        return False
    import numpy as np
    short_lookback = p.get('short_lookback', 3)
    mid_lookback   = p.get('mid_lookback', 12)
    long_lookback  = p.get('long_lookback', 24)
    min_short_pct  = p.get('min_short_pct', 2.0)
    max_long_pct   = p.get('max_long_pct', 5.0)

    if d['close'][-short_lookback] == 0:
        return False
    if d['close'][-mid_lookback] == 0:
        return False
    if d['close'][-long_lookback] == 0:
        return False

    short_move = (d['close'][-1] - d['close'][-short_lookback]) / d['close'][-short_lookback] * 100
    mid_move   = (d['close'][-1] - d['close'][-mid_lookback])   / d['close'][-mid_lookback]   * 100
    long_move  = (d['close'][-1] - d['close'][-long_lookback])  / d['close'][-long_lookback]  * 100

    # Strong on short TF, building on mid, not yet overbought on long
    return (short_move >= min_short_pct and
            mid_move > 0 and
            abs(long_move) <= max_long_pct)

# ═══════════════════════════════
# E63 — Leader-Laggard Rotation
# Leader coin pumped → buy laggards in same category
# ═══════════════════════════════
def signal_e63(d, p, btc_data):
    if not ind.enough(d, 10):
        return False
    if btc_data is None or not ind.enough(btc_data, 10):
        return False
    leader_pump   = p.get('leader_pump', 3.0)   # BTC pumped X%
    coin_max_move = p.get('coin_max_move', 1.0)  # coin not yet moved
    lookback      = p.get('lookback', 3)

    if btc_data['close'][-lookback] == 0 or d['close'][-lookback] == 0:
        return False

    btc_move  = (btc_data['close'][-1] - btc_data['close'][-lookback]) / btc_data['close'][-lookback] * 100
    coin_move = (d['close'][-1] - d['close'][-lookback]) / d['close'][-lookback] * 100

    # BTC pumped but coin hasn't moved yet = laggard opportunity
    return btc_move >= leader_pump and abs(coin_move) <= coin_max_move

# ═══════════════════════════════
# E64 — False Pump Detector (Inverse/Filter)
# Price pumped but volume weak = fake pump, SKIP
# Used as filter in E66/E67, also standalone to study false pumps
# ═══════════════════════════════
def signal_e64(d, p, _):
    if not ind.enough(d, 20):
        return False
    pump_pct    = p.get('pump_pct', 5.0)
    max_vol_mult = p.get('max_vol_mult', 1.5)  # volume NOT spiking

    if d['close'][-4] == 0:
        return False
    price_move = (d['close'][-1] - d['close'][-4]) / d['close'][-4] * 100
    vr = ind.calc_volume_ratio(d['volume'], 20)

    # Price pumped but volume weak = FALSE pump = interesting research
    return price_move >= pump_pct and (vr is None or vr <= max_vol_mult)

# ═══════════════════════════════
# E65 — Pump Probability Engine
# Weighted score from multiple signals
# ═══════════════════════════════
def signal_e65(d, p, btc_data):
    if not ind.enough(d, 50):
        return False
    min_score = p.get('min_score', 70)

    score = 0

    # Volume acceleration (20pts)
    import numpy as np
    vols = d['volume'][-6:]
    if len(vols) >= 6:
        v1 = np.sum(vols[:2])
        v2 = np.sum(vols[2:4])
        v3 = np.sum(vols[4:])
        if v1 > 0 and v2 > 0 and v3 > v2 > v1:
            score += 20

    # Relative strength vs BTC (20pts)
    if btc_data and ind.enough(btc_data, 6):
        if d['close'][-4] > 0 and btc_data['close'][-4] > 0:
            coin_r = (d['close'][-1]-d['close'][-4])/d['close'][-4]*100
            btc_r  = (btc_data['close'][-1]-btc_data['close'][-4])/btc_data['close'][-4]*100
            if coin_r - btc_r > 2: score += 20

    # Volume spike (20pts)
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if vr and vr > 3.0: score += 20

    # RSI momentum building (15pts)
    rsi = ind.calc_rsi(d['close'], 14)
    if rsi and 50 < rsi < 75: score += 15

    # ATR expanding (15pts)
    atr = ind.calc_atr(d['high'], d['low'], d['close'], 14)
    atr_slow = ind.calc_atr(d['high'], d['low'], d['close'], 28)
    if atr and atr_slow and atr_slow > 0 and atr/atr_slow > 1.3: score += 15

    # BTC regime safe (10pts)
    if btc_data and ind.enough(btc_data, 14):
        btc_rsi = ind.calc_rsi(btc_data['close'], 14)
        if btc_rsi and btc_rsi > 45: score += 10

    return score >= min_score

# ═══════════════════════════════
# E66 — Bot Consensus Explosion
# Count how many different signal types are bullish simultaneously
# ═══════════════════════════════
def signal_e66(d, p, btc_data):
    if not ind.enough(d, 50):
        return False
    min_consensus = p.get('min_consensus', 5)

    bullish = 0

    # RSI oversold/neutral
    rsi = ind.calc_rsi(d['close'], 14)
    if rsi and rsi < 40: bullish += 1

    # Volume spike
    vr = ind.calc_volume_ratio(d['volume'], 20)
    if vr and vr > 2.0: bullish += 1

    # Price above VWAP
    vwap = ind.calc_vwap(d['high'], d['low'], d['close'], d['volume'], 24)
    if vwap and d['close'][-1] > vwap: bullish += 1

    # BB lower band touch
    bb = ind.calc_bollinger(d['close'], 20, 2.0)
    if bb and d['close'][-1] < bb['lower'] * 1.02: bullish += 1

    # ATR expanding
    atr = ind.calc_atr(d['high'], d['low'], d['close'], 14)
    atr_slow = ind.calc_atr(d['high'], d['low'], d['close'], 28)
    if atr and atr_slow and atr_slow > 0 and atr/atr_slow > 1.2: bullish += 1

    # BTC safe
    if btc_data and ind.enough(btc_data, 14):
        btc_rsi = ind.calc_rsi(btc_data['close'], 14)
        if btc_rsi and btc_rsi > 45: bullish += 1

    # Consecutive higher lows (last 4 candles)
    lows = d['low'][-4:]
    if all(lows[i] > lows[i-1] for i in range(1, len(lows))): bullish += 1

    # Price momentum (short term positive)
    if d['close'][-3] > 0:
        momentum = (d['close'][-1] - d['close'][-3]) / d['close'][-3] * 100
        if momentum > 0.5: bullish += 1

    # OBV positive
    closes = d['close'][-10:]
    vols = d['volume'][-10:]
    obv = sum(vols[i] if closes[i]>closes[i-1] else -vols[i] for i in range(1,len(closes)))
    if obv > 0: bullish += 1

    # Relative strength vs BTC
    if btc_data and ind.enough(btc_data, 6):
        if d['close'][-4] > 0 and btc_data['close'][-4] > 0:
            coin_r = (d['close'][-1]-d['close'][-4])/d['close'][-4]*100
            btc_r  = (btc_data['close'][-1]-btc_data['close'][-4])/btc_data['close'][-4]*100
            if coin_r > btc_r: bullish += 1

    return bullish >= min_consensus


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
    'E27': signal_e27,
    'E28': signal_e28,
    'E29': signal_e29,
    'E30': signal_e30,
    'E31': signal_e31,
    'E32': signal_e32,
    'E33': signal_e33,
    'E34': signal_e34,
    'E35': signal_e35,
    'E36': signal_e36,
    'E37': signal_e37,
    'E38': signal_e38,
    'E39': signal_e39,
    'E40': signal_e40,
    'E41': signal_e41,
    'E42': signal_e42,
    'E43': signal_e43,
    'E44': signal_e44,
    'E45': signal_e45,
    'E46': signal_e46,
    'E47': signal_e47,
    'E48': signal_e48,
    'E49': signal_e49,
    'E50': signal_e50,
    'E51': signal_e51,
    'E52': signal_e52,
    'E53': signal_e53,
    'E54': signal_e54,
    'E55': signal_e55,
    'E56': signal_e56,
    'E57': signal_e57,
    'E59': signal_e59,
    'E60': signal_e60,
    'E61': signal_e61,
    'E62': signal_e62,
    'E63': signal_e63,
    'E64': signal_e64,
    'E65': signal_e65,
    'E66': signal_e66,
}



