# Averion DCA Parameter Calculation System
## AI Review Brief — Spacing · TP · Trailing · Size Multiplier

---

## 1. Platform Context

Averion is an automated crypto DCA trading platform.
Users connect their exchange API and create bots on specific coins.
Platform automatically calculates all DCA parameters.
User never manually sets spacing, TP, or trailing.
Goal: find ONE optimal calculation method that works fairly
for every coin and every market scenario automatically.

---

## 2. The Core Problem We Are Solving

Every coin behaves differently:
- BTC (Mega Cap): moves 1-3% typically · very liquid
- ETH (Large Cap): moves 2-4% typically · liquid
- RVN (Small Cap): moves 8-15% typically · less liquid
- Unknown micro coin: moves 20-40% · thin order book

If we use same spacing for all:
- Too tight for volatile coins → multiple DCAs fire in minutes
- Too wide for stable coins → misses good entry opportunities
- Capital depleted on wrong coins · stuck positions on others

We need: each coin gets parameters matching its REAL behavior
Automatically · daily · no human intervention

---

## 3. Five Market Cap Categories (LOCKED)

| Category  | Market Cap      | Examples        |
|-----------|----------------|----------------|
| Mega Cap  | > $100B        | BTC · ETH       |
| Large Cap | $10B - $100B   | BNB · SOL · XRP |
| Mid Cap   | $1B - $10B     | AVAX · LINK     |
| Small Cap | $100M - $1B    | RVN · HBAR      |
| Micro Cap | < $100M        | Unknown coins   |

Categories purpose:
- Emergency safety limits only (never too extreme)
- Classification for new coins before own data available
- NOT used to calculate exact spacing/TP for calibrated coins

---

## 4. Data Sources

Market cap classification:
- CoinGecko fetched at 03:30 daily
- CoinMarketCap fetched at 04:00 daily
- Combined at 04:30: recorded_cap = (CoinGecko + CMC) / 2
- If one fails: use available source
- If both fail: use last recorded cap
- If disagree > 100%: use lower value (conservative)

OHLCV data for parameter calculation:
- Collected EVERY HOUR continuously via CCXT
- Stored in ohlcv_hourly table
- Per coin · per exchange separately
- 90 days = 2,160 hourly candles per coin per exchange
- Source: user's specific exchange (not CoinGecko)
- Reason: prices differ per exchange

Live price for trading decisions:
- Fetched every 60 seconds via CCXT
- One bulk fetch_tickers() call per exchange
- Not per coin · not per bot · one call covers all
- Used by bot loop only · not for classification

---

## 5. Cap Protection System (LOCKED · Original Design)

No other platform has this.

Problem: fake pump or manipulation can spike market cap
overnight → coin wrongly classified as higher category →
wrong parameters applied → user's capital at risk.

Solution — Asymmetric cap protection:
Upward: recorded_cap = min(real_cap, previous × 1.10)
→ Maximum +10% recorded per day upward
→ Fake pump: $100M → $500M → recorded as $110M
→ Coin stays Small Cap · conservative params maintained
→ Real growth takes 25+ consecutive days to cross boundary
→ Fake pumps cannot sustain 25 days → naturally filtered

Downward: recorded_cap = real_cap immediately
→ Full drop recorded same day
→ Coin immediately reclassified to lower category
→ Wider spacing applied to new positions
→ Protects capital from real crashes immediately

Example:
Day 0: BTC at $1T (Mega Cap)
Day 1: crash to $80B → recorded $80B → Large Cap immediately
Day 2: recovers to $200B → recorded $88B (+10%) → still Large
Day 3: real $300B → recorded $96.8B → still Large
Day 4: real $400B → recorded $106.5B → back to Mega Cap

Reclassification:
→ Affects NEW positions only
→ Existing positions keep original parameters FOREVER
→ User never surprised by parameter change on open position

---

## 6. New Coin Confidence System

| History    | Approach                        | Badge       |
|------------|--------------------------------|-------------|
| 0-30 days  | Category defaults only          | 🔴 New      |
| 30-90 days | 70% category + 30% own data    | 🟡 Learning |
| 90+ days   | 100% own data · fully adaptive  | 🟢 Calibrated |

New coin (< 30 days):
→ Gets category average spacing/TP
→ Category average = simple mean of all calibrated coins
→ BTC spacing 2.7% + ETH spacing 3.2% + BNB 4.1% / 3 = 3.33%
→ New Mega coin gets 3.33% until own data available
→ Cap protection applies from day 1

---

## 7. Current Parameter Calculation (What We Have)

For calibrated coins (90+ days own data):

SPACING:
spacing = max(ATR_14_daily × 1.5, median_bounce × 0.85)
Clamped to category emergency limits

ATR_14_daily = Average True Range over 14 daily candles
median_bounce = median of all drops before recovery (90-day hourly data)
Take larger of two = more conservative = protects capital

TP (currently):
TP = weighted_avg_entry × (1 + median_recovery × regime_multiplier)
regime_multiplier: Bull=0.80 · Sideways=0.70 · Bear=0.60
Clamped to category limits

SIZE MULTIPLIER (currently):
Category base: Mega=1.10x · Large=1.20x · Mid=1.35x · Small=1.50x · Micro=1.65x
Per DCA level: L1=1.0x · L2=1.2x · L3=1.4x · L4=1.6x · L5+=2.0x hard cap

TRAILING (currently):
Category-based:
Mega: 0.5%-2% · Large: 1%-3% · Mid: 1.5%-4% · Small: 2%-6% · Micro: 3%-8%

---

## 8. Current Problems We Identified

Problem 1 — Static category limits block real market behavior:
Mega Cap max TP = 5%
BTC independently calculates 8% recovery from own data
System clamps to 5% → leaving 3% profit on table
If market gains improve to 8% average → limit never adapts

Problem 2 — 90-day fixed window lags market changes:
Bull run for 90 days → TP set high
Bull run ends on day 91 → 90 days of bull data still in window
TP remains high → positions open expecting 8% → market only gives 3%
→ TP never hits → positions stuck open → capital locked
Takes another 90 days for window to fully reflect new reality

Problem 3 — Static trailing does not reflect coin behavior:
BTC trailing = 0.5% (Mega Cap range)
But BTC might typically extend 1.2% past TP before reversing
0.5% trail = closes too early → leaves money on table
Another coin might only extend 0.3% → 0.5% trail = misses close

Problem 4 — Size multiplier not linked to coin volatility:
All Mega Cap coins get same 1.10x base multiplier
But ETH is 30-50% more volatile than BTC despite same category
Same multiplier = wrong capital deployment per DCA

---

## 9. Proposed Better Approach — Per Coin Independent

Instead of category limits for exact values:
Each coin calculates everything from its own 90-day rolling data

ROLLING WINDOW (not fixed block):
Not a fixed 90-day snapshot
Always last 90 days from today
Old data drops out daily as new data comes in
Market change reflects gradually and continuously

WEIGHTED ROLLING WINDOW:
Recent data matters more than old data
Weight scheme:
Last 30 days:  50% weight
Days 31-60:    30% weight
Days 61-90:    20% weight

Why weighted:
If bull run ends → recent 30 days (50% weight) pulls TP down fast
Not waiting 90 days for old bull data to fully expire
Adapts within weeks not months

SPACING per coin:
floor = coin's own 10th percentile drop (90-day weighted)
ceiling = coin's own 90th percentile drop (90-day weighted)
calculated = max(ATR_14 × 1.5, median_bounce × 0.85)
final = clamp(calculated, floor, ceiling)

TP per coin:
floor = coin's own 10th percentile recovery (weighted)
ceiling = coin's own 90th percentile recovery (weighted)
calculated = median_recovery × regime_multiplier
final = clamp(calculated, floor, ceiling)

TRAILING per coin:
Measure: after price hits TP level, how much further does it
         typically move before reversing?
trailing = 20th percentile of extra moves after TP point
           (conservative · catches most but not all)
final = clamp(trailing, category_absolute_min, category_absolute_max)

SIZE MULTIPLIER per coin:
Base from coin's own volatility relative to category average:
if coin_volatility > category_avg_volatility:
    multiplier = category_base × (1 + volatility_ratio × 0.5)
else:
    multiplier = category_base × (1 - volatility_ratio × 0.5)
Clamped to category limits

CATEGORY LIMITS become EMERGENCY ONLY:
Not for normal calculation
Only triggers if coin data produces extreme values
Example: data anomaly makes spacing = 0.1% → emergency min kicks in
Very rarely triggered · just a safety backstop

---

## 10. Daily Change Protection

Even with weighted window, prevent sudden parameter jumps:

Max daily change on any parameter: 20%
Yesterday spacing = 2.7%
Max today = 2.7% × 1.20 = 3.24%
Min today = 2.7% × 0.80 = 2.16%

Prevents:
- Flash crash distorting ATR → spacing suddenly 8x wider
- Single day manipulation affecting parameters
- Gradual adaptation always · never sudden jumps

---

## 11. Regime Interaction

Market regime detected daily at 04:30 (5 signals):
Strong Bull · Bull · Sideways · Bear · Strong Bear

Affects TP multiplier:
Strong Bull: 0.85 (ride momentum longer)
Bull:        0.80
Sideways:    0.70
Bear:        0.60
Strong Bear: 0.55 (take profit very fast)

Affects dynamic category limits (if enabled):
Bull:        limits × 0.75 (tighter spacing · more entries)
Sideways:    limits × 1.00 (standard)
Bear:        limits × 1.50 (wider spacing · protect capital)

Two-layer protection:
Layer 1: Weighted window adapts TP from historical data
Layer 2: Regime multiplier adjusts immediately to current conditions

---

## 12. Admin Dashboard — Category Table

Admin sees category table with current values:

Current Regime: SIDEWAYS

| Category | Spacing Min | Spacing Max | TP Min | TP Max | Trail |
|----------|------------|------------|--------|--------|-------|
| Mega     | 2.0%       | 8.0%       | 1%     | 5%     | 0.5-2%|
| Large    | 5.0%       | 12.0%      | 2%     | 7%     | 1-3%  |
| Mid      | 7.0%       | 18.0%      | 4%     | 10%    | 1.5-4%|
| Small    | 10.0%      | 25.0%      | 5%     | 15%    | 2-6%  |
| Micro    | 15.0%      | 40.0%      | 8%     | 20%    | 3-8%  |

[Edit Base Values] ← admin changes base
[Dynamic Limits: ON] ← regime adjusts limits automatically

---

## 13. Admin Coin Search

Admin types any coin name → sees full independent details:

Search: BTC

BTC/USDT — Binance
─────────────────────────────────
Category:        Mega Cap 🟢
Market Cap:      $1.24T
Confidence:      🟢 Calibrated (147 days own data)
Data points:     3,528 hourly candles

Calculated (independent from own data):
Spacing:         2.7%
TP:              2.94% (sideways regime × 0.70)
Trail:           0.5%
Size Multiplier: 1.10x

Own data ranges (10th-90th percentile):
Spacing range:   1.2% - 6.8%
TP range:        1.8% - 9.2%
Trail range:     0.3% - 1.4%

Weight breakdown:
Last 30 days (50%): median recovery 3.8%
Days 31-60  (30%): median recovery 4.6%
Days 61-90  (20%): median recovery 5.1%
Weighted median:   4.2%

Category emergency limits:
Spacing: 2% min · 8% max
TP: 1% min · 5% max

Active bots: 12
Last updated: Today 04:30
─────────────────────────────────

---

## 14. Research Bots and Classification

144 paper research bots test 14 entry methods.
Research bots USE classified params (same as live bots).

Why:
Best entry signal = enters so well that coin goes
directly to TP with zero or very few DCAs.
Classification sets correct TP target.
Fewest DCAs + fastest TP close = best signal quality.
Research correctly measures signal quality in real conditions.

---

## 15. Questions for AI Review

1. Is the weighted rolling window (50/30/20) the right approach?
   Better weights? Better window length?
   Or is there a fundamentally better method?

2. Is per-coin percentile range (10th-90th) correct for limits?
   Or should limits come from somewhere else?

3. Is the spacing formula correct?
   max(ATR_14_daily × 1.5, median_bounce × 0.85)
   Is 1.5 multiplier optimal? Should it vary per category?

4. Is weighted median the right statistic?
   Or should we use weighted percentile?
   Or something else entirely?

5. Does the regime multiplier on TP conflict with
   the weighted window? Are we double-adjusting?

6. Is the trailing calculation correct?
   20th percentile of extra moves after TP point
   Too conservative? Too aggressive?

7. Size multiplier per coin based on volatility ratio —
   is this the right approach?
   Or keep category-fixed multipliers?

8. Is 20% daily change limit correct?
   Too restrictive? Too loose?

9. What happens when a coin has unusual behavior:
   - Coin that never bounces (just keeps falling)
   - Coin that instantly recovers every time
   - Coin with extreme outlier events
   How should edge cases be handled?

10. Is there a better single unified formula that covers
    spacing · TP · trailing · multiplier together?
    Rather than calculating each independently?

11. Does the cap protection (+10% upward · immediate downward)
    conflict with any parameter calculations?

12. Overall: is this system achievable and accurate?
    What is the optimal calculation method that works
    fairly for every coin and every market scenario?
    Is there a better proven approach from quantitative finance?
