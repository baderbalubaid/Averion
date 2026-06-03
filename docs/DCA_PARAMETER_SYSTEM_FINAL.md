# Averion DCA Parameter System — Final Brief
## All Decisions Locked · Ready to Code

---

## 1. Purpose

Platform automatically calculates all DCA parameters per coin.
User never manually sets spacing, TP, trailing, or size multiplier.
Goal: maximum profit through accurate per-coin parameters
that adapt automatically to market conditions every day.

---

## 2. Five Categories (LOCKED)

| Category  | Market Cap    | Examples        |
|-----------|--------------|----------------|
| Mega Cap  | > $100B      | BTC · ETH       |
| Large Cap | $10B-$100B   | BNB · SOL · XRP |
| Mid Cap   | $1B-$10B     | AVAX · LINK     |
| Small Cap | $100M-$1B    | RVN · HBAR      |
| Micro Cap | < $100M      | Excluded live   |

Category roles (THREE only):
1. Emergency safety limits (always silently watching)
2. Default starting point for new coins (< 90 days)
3. Confidence blend (30-90 days: 70% category + 30% own)

After 90 days: coin uses 100% own independent data.
Category limits = backstop only · rarely triggers.

---

## 3. Category Emergency Limits (LOCKED)

| Category | Spacing    | TP%      | Trail%   | Size Mult |
|----------|-----------|---------|---------|-----------|
| Mega     | 2%-8%     | 1%-5%   | 0.5%-2% | 1.1x-1.8x |
| Large    | 5%-12%    | 2%-7%   | 1%-3%   | 1.2x-2.2x |
| Mid      | 7%-18%    | 4%-10%  | 1.5%-4% | 1.3x-2.8x |
| Small    | 10%-25%   | 5%-15%  | 2%-6%   | 1.5x-3.5x |
| Micro    | 15%-40%   | 8%-20%  | 3%-8%   | 2x-5x     |

These ONLY override when coin own data produces extreme values.
Normal calibrated coins never hit these limits.

---

## 4. Cap Protection System (LOCKED · Original Design)

Upward: recorded_cap = min(real_cap, previous × 1.10)
Downward: recorded_cap = real_cap (immediate)

Max +10% per day upward → protects against fake pumps
Full drop immediately → protects against real crashes

Reclassification: new positions only · existing unchanged forever.

---

## 5. New Coin Confidence System (LOCKED)

| Days      | Approach                          |
|-----------|----------------------------------|
| 0-30      | 100% category average             |
| 30-90     | 70% category + 30% own data      |
| 90+       | 100% own independent data         |

Category average = simple mean of all calibrated coins in category.
Example Mega Cap: (BTC spacing + ETH spacing + BNB spacing) / 3

---

## 6. Data Sources (LOCKED)

Market cap (for category classification):
- CoinGecko: fetched daily at 03:30
- CMC: fetched daily at 04:00
- Combined at 04:30: (CoinGecko + CMC) / 2
- If disagree > 100%: use lower value (conservative)

OHLCV (for parameter calculation):
- Collected EVERY HOUR via CCXT
- Stored in ohlcv_hourly table
- Per coin · per exchange separately
- 90 days = 2,160 hourly candles per coin

Live price (for trade decisions):
- Fetched every 60 seconds via CCXT
- One bulk fetch_tickers() per exchange
- Bot loop reads and acts on it

---

## 7. Weighted Rolling Window (LOCKED)

Equal weights: 25/25/25/25
Last 7 days:    25%
Days 8-30:      25%
Days 31-60:     25%
Days 61-90:     25%

Why equal weights (not 50/30/20):
- No single period dominates calculation
- 50% on last 30 days = too reactive to anomalies
- One bad month distorts everything
- Equal weights = stable · reliable · consistent
- Still adapts faster than unweighted 90-day window

---

## 8. Spacing Calculation Per Coin (LOCKED)

Step 1: Calculate ATR (daily candles from ohlcv_hourly grouped by day)
ATR_14_daily = average true range over 14 daily candles

Step 2: Calculate dynamic volatility scalar
vol_scalar = min(3.0, max(1.2, coin_vol_30d / category_avg_vol))

Why dynamic scalar (not fixed 1.5):
- BTC low vol: scalar = 1.2 → tighter spacing → more entries
- RVN high vol: scalar = 2.0+ → wider spacing → protect capital
- Fixed 1.5 = wrong for most coins

Step 3: Calculate median bounce (weighted 25/25/25/25)
median_bounce = weighted median of all drops before recovery
               from 90-day hourly data

Step 4: Raw spacing
spacing_raw = max(ATR_14_daily × vol_scalar, median_bounce)

Step 5: Calculate coin own percentile range
spacing_floor = weighted 10th percentile of drops
spacing_ceiling = weighted 90th percentile of drops

Step 6: Clamp to own range
spacing = clamp(spacing_raw, spacing_floor, spacing_ceiling)

Step 7: Apply 20% daily change limit
spacing = clamp(spacing, yesterday × 0.80, yesterday × 1.20)

Step 8: Emergency category check (rarely triggers)
spacing = clamp(spacing, category_min, category_max)

---

## 9. TP Calculation Per Coin (LOCKED)

Step 1: Calculate median recovery (weighted 25/25/25/25)
median_recovery = weighted median of all recoveries after drops
                 from 90-day hourly data

Step 2: Calculate coin own percentile range
tp_floor = weighted 10th percentile of recoveries
tp_ceiling = weighted 90th percentile of recoveries

Step 3: Apply regime multiplier (small tilt only)
Regime multipliers:
Strong Bull: 1.10  (capture more of the move)
Bull:        1.05
Sideways:    1.00  (no adjustment)
Bear:        0.90  (slight reduction)
Strong Bear: 0.85  (more reduction)

Why soft multipliers (not original 0.60-0.85):
- Weighted window already adapts to bear conditions
- Regime = small nudge only · not major override
- Old 0.60 bear = TP too tight · left profit on table
- Weighted window does the heavy lifting

tp_raw = median_recovery × regime_multiplier

Step 4: Clamp to own range
tp = clamp(tp_raw, tp_floor, tp_ceiling)

Step 5: Apply 20% daily change limit
tp = clamp(tp, yesterday × 0.80, yesterday × 1.20)

Step 6: Emergency category check (rarely triggers)
tp = clamp(tp, category_min_tp, category_max_tp)

TP applied from: weighted average entry price (not original entry)
Formula: close_price = avg_cost × (1 + tp_pct)

---

## 10. Trailing Calculation Per Coin (LOCKED)

Trailing = how much further price moves after TP before reversing

Step 1: Find all post-TP extensions in 90-day data
For each trade that hit TP:
extra_move = (peak_price_after_TP - TP_price) / TP_price

Step 2: Calculate 20th percentile of extensions (weighted)
trailing_raw = weighted 20th percentile of extra_moves

Why 20th percentile (conservative):
- 80% of cases: price moves MORE than trailing distance
- Closes position cleanly before reversal
- Does not chase every small extension

Step 3: Apply 15% daily change limit
trailing = clamp(trailing, yesterday × 0.85, yesterday × 1.15)

Step 4: Emergency category check
trailing = clamp(trailing, category_min_trail, category_max_trail)

Minimum trailing floor: 0.1% absolute minimum
Prevents immediate sell on TP touch if extensions near zero.

---

## 11. Size Multiplier Per Coin (LOCKED)

Category base:
Mega=1.10x · Large=1.20x · Mid=1.35x · Small=1.50x · Micro=1.65x

Volatility adjustment per coin:
vol_ratio = coin_volatility / category_avg_volatility
adjusted = category_base × (vol_ratio ^ 0.7)
size_mult = clamp(adjusted, category_min_mult, category_max_mult)

Why power scaling (^ 0.7) not linear:
- Linear: high vol coin gets 2.76x (too aggressive)
- Power: same coin gets 2.18x (safer · bounded)
- Smooth curve · never extreme

Per DCA level escalation:
L1: × 1.0 · L2: × 1.2 · L3: × 1.4 · L4: × 1.6 · L5+: × 2.0 cap

Apply 10% daily change limit on size multiplier:
(smaller limit = capital exposure changes slowly)

---

## 12. DCA Turned OFF Then ON (LOCKED)

User turns DCA OFF → turns back ON later:
- Bot joins shared queue normally
- Queue calculates score: Loss% / USDT needed
- If price dropped a lot while OFF → high loss% → high priority
- Queue fires when it is this position's turn
- DCA executes at current price
- Next DCA spacing = today's calculated value (updated daily)
- No reset logic needed
- No special handling needed
- Queue handles priority
- Daily classification handles spacing
- Both systems work together automatically

---

## 13. Daily Classification Process (LOCKED)

03:30 → CoinGecko fetch (market caps)
04:00 → CMC fetch (market caps)
04:30 → Classification:
        - Average both sources
        - Apply cap protection
        - Classify category
        - Calculate per-coin spacing/TP/trail/size
        - Apply 25/25/25/25 weighted window
        - Apply regime multiplier to TP
        - Apply daily change limits
        - Store in coin_history table
        - Telegram alert if any coin reclassified

Bot loop every 60 seconds:
- Reads spacing/TP/trail/size from coin_history
- Fetches live price (one bulk call per exchange)
- Checks all positions against parameters
- Executes trades if conditions met
- Never recalculates parameters (reads only)

---

## 14. Edge Cases (LOCKED)

Coin never bounces (downtrend):
If median_recovery <= 0:
→ Use category default TP
→ Mark coin as weak_recovery
→ Admin alert

Coin instantly recovers (tiny bounces):
→ Spacing floor prevents too tight spacing
→ Minimum TP = 1.5% absolute (covers fees + profit)

Extreme outlier events (LUNA-style crash):
→ 3× IQR outlier filter before any percentile calculation
→ Removes extreme events from statistical calculations
→ Flag coin: outlier_event_detected = TRUE

No USDT pair (coin trades against BTC only):
→ Convert ATR to USDT equivalent before calculation

---

## 15. Admin Dashboard (LOCKED)

Category table (shows current values per regime):
| Category | Spacing Min | Spacing Max | TP Min | TP Max |
...

Coin search bar:
Type any coin → shows:
- Category + market cap + confidence badge
- Own calculated: spacing · TP · trail · size mult
- Own data ranges: 10th-90th percentile
- Weight breakdown: last7 · 8-30 · 31-60 · 61-90
- Category limits (emergency backstop)
- Active bots on this coin
- Last updated timestamp

---

## 16. All Locked Decisions

| Decision | Rule |
|----------|------|
| Categories | 5 (safety limits + defaults only) |
| Window weights | 25/25/25/25 equal |
| Window length | 90 days rolling |
| ATR multiplier | Dynamic (1.2-3.0 per volatility) |
| Spacing | Per-coin independent |
| TP | Per-coin + regime soft multiplier |
| Regime multipliers | 1.10/1.05/1.0/0.90/0.85 |
| Trailing | 20th percentile post-TP extension |
| Size multiplier | Volatility-adjusted power scaling |
| Daily limit spacing/TP | 20% |
| Daily limit trailing | 15% |
| Daily limit size mult | 10% |
| Percentile range | 10th-90th per coin |
| Statistic | Weighted median + weighted percentile |
| New coin | Category average until 90 days |
| Blend period | 30-90 days: 70/30 |
| Cap protection | +10% up · immediate down |
| DCA off then on | Queue handles · spacing from daily calc |
| Outlier filter | 3× IQR before percentile calc |
| Min TP | 1.5% absolute floor |
| Min trailing | 0.1% absolute floor |
