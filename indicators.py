"""
indicators.py — All technical indicators for E1-E26 research bots
Calculated from ohlcv_hourly table data
No external APIs needed (except E24 funding rate via CCXT)
"""

import numpy as np
from typing import Optional


# ═══════════════════════════════
# DATA HELPERS
# ═══════════════════════════════

def to_arrays(ohlcv_rows):
    """
    Convert DB rows to numpy arrays.
    DB row order: timestamp, open, high, low, close, volume, atr_14
    Returns dict of arrays, newest candle LAST (chronological order)
    """
    if not ohlcv_rows:
        return None
    rows = list(reversed(ohlcv_rows))  # DB returns newest first
    return {
        'ts':     [r[0] for r in rows],
        'open':   np.array([float(r[1]) for r in rows]),
        'high':   np.array([float(r[2]) for r in rows]),
        'low':    np.array([float(r[3]) for r in rows]),
        'close':  np.array([float(r[4]) for r in rows]),
        'volume': np.array([float(r[5]) for r in rows]),
    }

def enough(d, n):
    """Check we have at least n candles."""
    return d is not None and len(d['close']) >= n


# ═══════════════════════════════
# MOMENTUM INDICATORS
# ═══════════════════════════════

def calc_rsi(close, period=14):
    """RSI — Relative Strength Index."""
    if len(close) < period + 1:
        return None
    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.mean(gain[:period])
    avg_loss = np.mean(loss[:period])
    for i in range(period, len(gain)):
        avg_gain = (avg_gain * (period - 1) + gain[i]) / period
        avg_loss = (avg_loss * (period - 1) + loss[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def calc_stoch_rsi(close, period=14, k_period=3, d_period=3):
    """Stochastic RSI — %K and %D."""
    if len(close) < period * 2:
        return None, None
    rsi_values = []
    for i in range(period, len(close) + 1):
        r = calc_rsi(close[i-period-1:i], period)
        if r is not None:
            rsi_values.append(r)
    if len(rsi_values) < period:
        return None, None
    rsi_arr = np.array(rsi_values)
    min_rsi = np.min(rsi_arr[-period:])
    max_rsi = np.max(rsi_arr[-period:])
    if max_rsi == min_rsi:
        return 50.0, 50.0
    k = (rsi_arr[-1] - min_rsi) / (max_rsi - min_rsi) * 100
    k_series = [(rsi_arr[i] - np.min(rsi_arr[i-period+1:i+1])) /
                max(np.max(rsi_arr[i-period+1:i+1]) -
                    np.min(rsi_arr[i-period+1:i+1]), 0.0001) * 100
                for i in range(period-1, len(rsi_arr))]
    d = np.mean(k_series[-d_period:]) if len(k_series) >= d_period else k
    return round(k, 2), round(d, 2)


def calc_macd(close, fast=12, slow=26, signal=9):
    """MACD line, signal line, histogram."""
    if len(close) < slow + signal:
        return None, None, None
    def ema(arr, n):
        e = np.zeros(len(arr))
        e[n-1] = np.mean(arr[:n])
        k = 2 / (n + 1)
        for i in range(n, len(arr)):
            e[i] = arr[i] * k + e[i-1] * (1 - k)
        return e
    fast_ema = ema(close, fast)
    slow_ema = ema(close, slow)
    macd_line = fast_ema - slow_ema
    valid = macd_line[slow-1:]
    sig_ema = ema(valid, signal)
    macd_val = round(macd_line[-1], 6)
    sig_val = round(sig_ema[-1], 6)
    hist = round(macd_val - sig_val, 6)
    hist_prev = round(macd_line[-2] - sig_ema[-2], 6) if len(sig_ema) >= 2 else hist
    return macd_val, sig_val, hist, hist_prev


def calc_adx(high, low, close, period=14):
    """ADX — Average Directional Index."""
    if len(close) < period * 2:
        return None
    tr = np.maximum(high[1:] - low[1:],
         np.maximum(abs(high[1:] - close[:-1]),
                    abs(low[1:] - close[:-1])))
    dm_plus = np.where((high[1:] - high[:-1]) > (low[:-1] - low[1:]),
                        np.maximum(high[1:] - high[:-1], 0), 0)
    dm_minus = np.where((low[:-1] - low[1:]) > (high[1:] - high[:-1]),
                         np.maximum(low[:-1] - low[1:], 0), 0)
    atr = np.mean(tr[:period])
    pdm = np.mean(dm_plus[:period])
    ndm = np.mean(dm_minus[:period])
    for i in range(period, len(tr)):
        atr = atr * (period-1)/period + tr[i]/period
        pdm = pdm * (period-1)/period + dm_plus[i]/period
        ndm = ndm * (period-1)/period + dm_minus[i]/period
    pdi = 100 * pdm / atr if atr > 0 else 0
    ndi = 100 * ndm / atr if atr > 0 else 0
    dx = 100 * abs(pdi - ndi) / (pdi + ndi) if (pdi + ndi) > 0 else 0
    return round(dx, 2)


def calc_obv(close, volume):
    """OBV — On Balance Volume. Returns current OBV and trend."""
    if len(close) < 20:
        return None, None
    obv = np.zeros(len(close))
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            obv[i] = obv[i-1] + volume[i]
        elif close[i] < close[i-1]:
            obv[i] = obv[i-1] - volume[i]
        else:
            obv[i] = obv[i-1]
    obv_20 = np.mean(obv[-20:])
    obv_current = obv[-1]
    trend = 'up' if obv_current > obv_20 else 'down'
    return round(obv_current, 2), trend


# ═══════════════════════════════
# TREND INDICATORS
# ═══════════════════════════════

def calc_ema(close, period):
    """Exponential Moving Average."""
    if len(close) < period:
        return None
    k = 2 / (period + 1)
    ema = np.mean(close[:period])
    for price in close[period:]:
        ema = price * k + ema * (1 - k)
    return round(ema, 8)


def calc_sma(close, period):
    """Simple Moving Average."""
    if len(close) < period:
        return None
    return round(float(np.mean(close[-period:])), 8)


def calc_vwap(high, low, close, volume, period=24):
    """VWAP — Volume Weighted Average Price."""
    if len(close) < period:
        return None
    h = high[-period:]
    l = low[-period:]
    c = close[-period:]
    v = volume[-period:]
    typical = (h + l + c) / 3
    total_vol = np.sum(v)
    if total_vol == 0:
        return None
    return round(float(np.sum(typical * v) / total_vol), 8)


def calc_supertrend(high, low, close, period=14, multiplier=3.0):
    """Supertrend indicator. Returns direction: 1=bullish, -1=bearish."""
    if len(close) < period + 1:
        return None, None
    atr = calc_atr(high, low, close, period)
    if atr is None:
        return None, None
    hl2 = (high[-1] + low[-1]) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    # Simplified: just check if close is above lower band
    direction = 1 if close[-1] > lower else -1
    return direction, round(lower if direction == 1 else upper, 8)


def calc_ichimoku(high, low, conversion=9, base=26):
    """
    Ichimoku Kumo Cloud (simplified — Tenkan + Kijun + Senkou A/B).
    Returns: tenkan, kijun, senkou_a, senkou_b, cloud_bullish
    """
    needed = base + 26
    if len(high) < needed:
        return None
    def midpoint(h, l, n):
        return (np.max(h[-n:]) + np.min(l[-n:])) / 2
    tenkan = midpoint(high, low, conversion)
    kijun = midpoint(high, low, base)
    senkou_a = (tenkan + kijun) / 2
    senkou_b = midpoint(high[-base-26:-26], low[-base-26:-26], base) if len(high) >= base+26 else senkou_a
    cloud_bullish = senkou_a > senkou_b
    return {
        'tenkan': round(tenkan, 8),
        'kijun': round(kijun, 8),
        'senkou_a': round(senkou_a, 8),
        'senkou_b': round(senkou_b, 8),
        'cloud_bullish': cloud_bullish,
        'price_below_cloud': None  # set by caller with current price
    }


# ═══════════════════════════════
# VOLATILITY INDICATORS
# ═══════════════════════════════

def calc_atr(high, low, close, period=14):
    """ATR — Average True Range."""
    if len(close) < period + 1:
        return None
    tr = np.maximum(high[1:] - low[1:],
         np.maximum(abs(high[1:] - close[:-1]),
                    abs(low[1:] - close[:-1])))
    atr = np.mean(tr[:period])
    for i in range(period, len(tr)):
        atr = (atr * (period - 1) + tr[i]) / period
    return round(float(atr), 8)


def calc_bollinger(close, period=20, sigma=2.0):
    """Bollinger Bands — upper, middle, lower."""
    if len(close) < period:
        return None, None, None
    sma = np.mean(close[-period:])
    std = np.std(close[-period:])
    return (round(float(sma + sigma * std), 8),
            round(float(sma), 8),
            round(float(sma - sigma * std), 8))


def calc_keltner(high, low, close, period=20, multiplier=2.0):
    """Keltner Channels — upper, middle, lower."""
    if len(close) < period + 1:
        return None, None, None
    ema = calc_ema(close, period)
    atr = calc_atr(high, low, close, period)
    if ema is None or atr is None:
        return None, None, None
    return (round(ema + multiplier * atr, 8),
            round(ema, 8),
            round(ema - multiplier * atr, 8))


def calc_zscore(close, period=96):
    """Z-Score — price deviation from rolling mean."""
    if len(close) < period:
        return None
    window = close[-period:]
    mean = np.mean(window)
    std = np.std(window)
    if std == 0:
        return 0.0
    return round(float((close[-1] - mean) / std), 4)


# ═══════════════════════════════
# VOLUME INDICATORS
# ═══════════════════════════════

def calc_volume_ratio(volume, period=20):
    """Current volume vs N-period average."""
    if len(volume) < period + 1:
        return None
    avg = np.mean(volume[-period-1:-1])
    if avg == 0:
        return None
    return round(float(volume[-1] / avg), 4)


def calc_vpoc(close, volume, days=30):
    """
    VPOC — Volume Point of Control.
    Returns price level with highest volume.
    """
    candles = min(days * 24, len(close))
    if candles < 10:
        return None
    c = close[-candles:]
    v = volume[-candles:]
    price_min = np.min(c)
    price_max = np.max(c)
    if price_max == price_min:
        return None
    buckets = 50
    bucket_size = (price_max - price_min) / buckets
    vol_by_price = np.zeros(buckets)
    for i in range(len(c)):
        idx = min(int((c[i] - price_min) / bucket_size), buckets - 1)
        vol_by_price[idx] += v[i]
    vpoc_idx = np.argmax(vol_by_price)
    vpoc_price = price_min + (vpoc_idx + 0.5) * bucket_size
    return round(float(vpoc_price), 8)


# ═══════════════════════════════
# PRICE ACTION
# ═══════════════════════════════

def calc_price_drop(close, high, lookback=24):
    """Price drop % from recent high."""
    if len(close) < lookback:
        return None
    recent_high = np.max(high[-lookback:])
    if recent_high == 0:
        return None
    drop = (recent_high - close[-1]) / recent_high * 100
    return round(float(drop), 4)


def calc_fibonacci_levels(high, low, lookback=48):
    """Fibonacci retracement levels from swing high/low."""
    if len(high) < lookback:
        return None
    swing_high = np.max(high[-lookback:])
    swing_low = np.min(low[-lookback:])
    diff = swing_high - swing_low
    if diff == 0:
        return None
    return {
        '23.6': round(swing_high - 0.236 * diff, 8),
        '38.2': round(swing_high - 0.382 * diff, 8),
        '50.0': round(swing_high - 0.500 * diff, 8),
        '61.8': round(swing_high - 0.618 * diff, 8),
        '78.6': round(swing_high - 0.786 * diff, 8),
        'swing_high': round(swing_high, 8),
        'swing_low': round(swing_low, 8),
    }


def detect_hammer(open_p, high, low, close, wick_ratio=2.0):
    """Detect hammer candle pattern."""
    body = abs(close[-1] - open_p[-1])
    lower_wick = min(open_p[-1], close[-1]) - low[-1]
    upper_wick = high[-1] - max(open_p[-1], close[-1])
    if body == 0:
        return False
    return (lower_wick >= wick_ratio * body and
            upper_wick <= body * 0.5 and
            close[-1] > open_p[-1])


def detect_engulfing(open_p, close):
    """Detect bullish engulfing pattern."""
    if len(close) < 2:
        return False
    prev_bearish = close[-2] < open_p[-2]
    curr_bullish = close[-1] > open_p[-1]
    curr_engulfs = (open_p[-1] <= close[-2] and
                    close[-1] >= open_p[-2])
    return prev_bearish and curr_bullish and curr_engulfs


def detect_fair_value_gap(high, low, close, min_fill=0.25):
    """
    Fair Value Gap — 3 candle imbalance.
    Returns (gap_low, gap_high, fill_pct) or None.
    """
    if len(high) < 3:
        return None
    # Bullish FVG: candle[i-2] high < candle[i] low
    gap_low = high[-3]
    gap_high = low[-1]
    if gap_high <= gap_low:
        return None
    gap_size = gap_high - gap_low
    current_price = close[-1]
    fill_pct = max(0, (current_price - gap_low) / gap_size) if gap_size > 0 else 0
    return {'gap_low': gap_low, 'gap_high': gap_high,
            'fill_pct': round(fill_pct, 4), 'gap_size': gap_size}


def detect_support_level(close, low, lookback=48, touches=2):
    """Detect support level with N touches."""
    if len(low) < lookback:
        return None
    recent_lows = low[-lookback:]
    min_low = np.min(recent_lows)
    tolerance = min_low * 0.01
    touch_count = np.sum(recent_lows <= min_low + tolerance)
    if touch_count >= touches:
        return round(float(min_low), 8)
    return None


def calc_swing_structure(high, low, n_candles=3):
    """Detect swing low and subsequent structure shift."""
    if len(high) < n_candles * 2 + 1:
        return None, None
    recent_low = np.min(low[-n_candles:])
    prior_high = np.max(high[-n_candles*2:-n_candles])
    return round(float(recent_low), 8), round(float(prior_high), 8)


def calc_relative_strength_vs_btc(coin_close, btc_close, lookback=24):
    """
    Coin return vs BTC return over N hours.
    Positive = coin outperforming BTC.
    """
    if len(coin_close) < lookback + 1 or len(btc_close) < lookback + 1:
        return None
    coin_return = (coin_close[-1] - coin_close[-lookback]) / coin_close[-lookback] * 100
    btc_return = (btc_close[-1] - btc_close[-lookback]) / btc_close[-lookback] * 100
    return round(float(coin_return - btc_return), 4)


def detect_rsi_divergence(close, period=14, lookback=48):
    """
    Bullish RSI divergence: price makes lower low, RSI makes higher low.
    Returns True if divergence detected.
    """
    if len(close) < lookback + period:
        return False
    mid = lookback // 2
    price_low1 = np.min(close[-lookback:-mid])
    price_low2 = np.min(close[-mid:])
    rsi1 = calc_rsi(close[-lookback-period:-mid], period)
    rsi2 = calc_rsi(close[-period-mid:], period)
    if rsi1 is None or rsi2 is None:
        return False
    return price_low2 < price_low1 and rsi2 > rsi1


def detect_obv_divergence(close, volume, lookback=48):
    """
    Bullish OBV divergence: price making lower lows, OBV making higher lows.
    """
    if len(close) < lookback:
        return False
    mid = lookback // 2
    _, obv_trend_early = calc_obv(close[:-mid], volume[:-mid])
    _, obv_trend_late = calc_obv(close[-mid:], volume[-mid:])
    price_falling = close[-1] < close[-lookback]
    obv_rising = obv_trend_late == 'up' and obv_trend_early == 'down'
    return price_falling and obv_rising


def qfl_base_bounce(close, high, low, volume, base_age=72, vol_mult=1.5):
    """
    QFL Base Bounce — consolidation base broken then reclaimed.
    Returns (base_price, broken, reclaimed) or None.
    """
    if len(close) < base_age + 10:
        return None
    base_window = close[-base_age-10:-10]
    base_low = np.min(base_window)
    base_high = np.max(base_window)
    base_range = base_high - base_low
    if base_range / base_low > 0.05:
        return None
    base_price = base_low
    recent = close[-10:]
    broke = any(p < base_price for p in recent[:-1])
    reclaimed = close[-1] > base_price
    vol_ratio = calc_volume_ratio(volume, 20)
    vol_ok = vol_ratio is not None and vol_ratio >= vol_mult
    return {
        'base_price': round(base_price, 8),
        'broken': broke,
        'reclaimed': reclaimed,
        'volume_ok': vol_ok
    }
