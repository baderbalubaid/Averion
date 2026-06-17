# Averion Coin Parameter Calculation - AI Review Brief
## For ChatGPT / Gemini / Claude review - June 2026

---

## 1. Context

Averion is an automated crypto DCA (Dollar Cost Averaging) trading platform.
Every coin gets its own DCA spacing%, Take Profit%, Trailing%, and Size Multiplier,
calculated automatically once per day. No user ever sets these manually.

We now have real running data to inform this decision:
- 366 research DCA bots (entry methods E1-E66) with 150+ closed trades
- 240 research scalper bots (E58 control + E58v2 velocity challenger)
- BTC regime tracking (bull/bear/sideways) captured on every trade
- Currently market is in BEAR regime (BTC below SMA50)

This brief asks: what is the best formula to calculate per-coin DCA parameters,
and should it be regime-aware?

---

## 2. What Is ACTUALLY Running In Code Right Now

File: calculate_coin_params.py, runs daily.

Data window: 30 days hourly OHLCV (not 90, despite docs saying 90)

ATR_14 = average true range over last 14 hourly candles
atr_pct = ATR_14 divided by current price, times 100

median_drop = median of all percent drops between consecutive lower closes
spacing_raw = MIN(atr_pct times 1.5, median_drop times 0.85)
spacing = clamp(spacing_raw, category_min, category_max)

median_recovery = median of all percent gains on a bounce
tp_raw = median_recovery times 0.8 (flat multiplier, no regime awareness)
tp = clamp(tp_raw, category_tp_min, category_tp_max)

trail_raw = atr_pct times 0.8
trail = clamp(trail_raw, category_trail_min, category_trail_max)

size_mult = clamp(1 + atr_pct/10, category_size_min, category_size_max)

5 categories (mega/large/mid/small/micro) only define MIN/MAX clamps, e.g:
Mega: spacing 2-8%, TP 1-5%, trail 0.5-2%, size 1.1x-1.8x
Micro: spacing 15-40%, TP 8-20%, trail 3-8%, size 2x-5x

No regime adjustment. No weighted time windows. No percentile clamping.
No outlier filtering. No new-coin confidence blending. Falls back to
category-midpoint defaults if a coin has less than 24 hours of data.

---

## 3. Three Different "Locked" Spec Versions Exist (Never Implemented)

These were written at different points in planning. None of them match
the code described above. The team is unsure which one (if any) reflects
the right direction now that real trading data exists.

### Version A - original draft
spacing = MAX(ATR times 1.5, median_drop times 0.85) - note MAX, not MIN
TP = weighted_avg_entry times (1 + median_recovery times 0.70)
Category spacing = volume-weighted average across coins in category
(BTC would dominate Mega Cap spacing at roughly 87% weight)

### Version B - "final" v2
Volume-weighting REMOVED, each coin fully independent
TP regime multiplier: bull=0.80, bear=0.60, sideways=0.70
Same ATR / median-drop spacing formula as version A (MAX, not MIN)

### Version C - most detailed "final" v3
90-day window, weighted equally across 4 sub-periods:
last 7 days 25%, days 8-30 25%, days 31-60 25%, days 61-90 25%
Dynamic ATR multiplier scaled by coin volatility vs category average,
ranging from 1.2x to 3.0x (not a fixed 1.5x)
Spacing clamped to the COIN'S OWN 10th-90th percentile range of drops,
not just the category min/max
TP regime multiplier: strong bull=1.10, bull=1.05, sideways=1.00,
bear=0.90, strong bear=0.85 (soft tilt, not the 0.60-0.85 swing in version B)
Trailing = 20th percentile of price extension after TP is hit
Size multiplier uses power scaling (volatility ratio to the power of 0.7)
rather than linear scaling
Daily change limits: spacing/TP capped at 20% change per day,
trailing capped at 15%, size multiplier capped at 10%
New coins (0-30 days): 100% category average
30-90 days: 70% category average blended with 30% coin's own data
90+ days: 100% coin's own independent data
3x IQR outlier filter applied before any percentile calculation
Absolute floors: TP never below 1.5%, trailing never below 0.1%

---

## 4. Questions For AI Review

1. Given we now have 150+ real closed trades with regime data attached,
should TP/spacing be regime-aware (adjust automatically for bull/bear/
sideways), or is a flat multiplier (current code) safer until more data
accumulates?

2. Is the currently-running MIN(ATR*1.5, median_drop*0.85) formula
sound, or does the documented MAX version (versions A and B) make more
sense? What is the practical difference in outcome between MIN and MAX
here, and which is more conservative for capital protection?

3. Is the 30-day data window (current code) sufficient, or does the
90-day window with weighted sub-periods (version C) provide meaningfully
better calibration? What's the risk of overfitting to a recent volatile
period with only 30 days?

4. Is category-only clamping (current code) sufficient, or is the
coin's-own-percentile-range clamping (version C) worth the added
complexity?

5. Should we prioritize building a v2 right now, or is it reasonable
to keep running the current simpler formula until 30+ closed trades
exist per research method (the threshold the team already set for
other scoring decisions), and revisit then with real outcome data
rather than theory?

6. Of the three documented versions, which (if any) should be the
target implementation, or should the team design a new v4 informed
by what the live research data shows once enough trades accumulate?

---

## 5. What We Are NOT Asking

We are not asking whether market-cap categories are the right basis
for classification at all (that was reviewed previously and locked).
This brief is narrowly about the spacing/TP/trailing/size formula
applied within those categories.
