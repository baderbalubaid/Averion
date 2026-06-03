# Averion Coin Classification System — Final Brief
## All Decisions Locked · Ready to Code

---

## 1. Purpose

Automatically set correct DCA parameters per coin.
No user ever sets spacing or TP manually.
System calculates everything daily.

Main goal:
Best entry signal = goes directly to TP with zero or few DCAs.
Classification sets correct TP target and spacing safety limits.
Best research method = fewest DCAs + fastest TP = genuinely good signal.

---

## 2. Five Categories (LOCKED)

| Category | Market Cap | Examples |
|----------|-----------|---------|
| Mega Cap | >$100B | BTC, ETH |
| Large Cap | $10B-$100B | BNB, SOL, XRP |
| Mid Cap | $1B-$10B | AVAX, LINK |
| Small Cap | $100M-$1B | RVN, HBAR |
| Micro Cap | <$100M | Excluded from live |

Categories = SAFETY LIMITS ONLY.
Not used to calculate exact spacing or TP.
Each coin gets independent params from its own data.

Admin-only parameter limits:
| Category | Spacing Min/Max | Size Mult | TP Min/Max |
|----------|----------------|-----------|-----------|
| Mega Cap | 2%-8% | 1.1x-1.8x | 1%-5% |
| Large Cap | 5%-12% | 1.2x-2.2x | 2%-7% |
| Mid Cap | 7%-18% | 1.3x-2.8x | 4%-10% |
| Small Cap | 10%-25% | 1.5x-3.5x | 5%-15% |
| Micro Cap | 15%-40% | 2x-5x | 8%-20% |

---

## 3. Independent Coin Spacing (LOCKED)

REMOVED: Volume-weighted category spacing
Why removed: BTC (87% weight) dominated Mega Cap
BNB users got BTC spacing despite BNB being more volatile

REPLACED WITH: Each coin gets its OWN spacing

Formula per coin:
spacing = max(ATR_14 x 1.5, median_bounce x 0.85)
Clamped between coin category min and max

ATR_14 = Average True Range over 14 periods (hourly OHLCV)
median_bounce = median of all drops before price recovery
               calculated from 90 days of hourly data

Example:
BTC: ATR=1.8% → 2.7% → within Mega range → spacing = 2.7%
ETH: ATR=2.1% → 3.2% → within Mega range → spacing = 3.2%
BNB: ATR=2.8% → 4.2% → within Large range → spacing = 4.2%
Each coin independent. Category = safety limits only.

Server load:
Calculate once daily at 03:30 for all coins.
One SQL UPDATE per coin per day.
Lightweight. Not a loop issue.
Same server handles 288 research bots easily.

---

## 4. Regime-Aware TP (LOCKED)

TP adapts to market regime automatically.
Reads from market_regimes table daily.

Formula:
regime_multipliers = {bull: 0.80, bear: 0.60, sideways: 0.70}
tp_mult = multipliers[today_regime]
TP = weighted_avg_entry x (1 + median_recovery x tp_mult)

Why different multipliers:
Bull: coins recover stronger, ride momentum longer = 0.80
Bear: bounces weak and short, take profit fast = 0.60
Sideways: normal conditions = 0.70

Example BTC (Mega Cap, median recovery 4%):
Bull: TP = avg_cost x (1 + 0.04 x 0.80) = avg_cost x 1.032
Bear: TP = avg_cost x (1 + 0.04 x 0.60) = avg_cost x 1.024
Sideways: TP = avg_cost x (1 + 0.04 x 0.70) = avg_cost x 1.028

All clamped between category TP min and max.
Updates automatically when regime changes.
3 lines of code to implement.

---

## 5. Independent Size Multiplier Per Coin

Category base:
Mega=1.10x, Large=1.20x, Mid=1.35x, Small=1.50x, Micro=1.65x

Per DCA level:
L1=1.0x, L2=1.2x, L3=1.4x, L4=1.6x, L5+=2.0x hard cap

Example Small Cap L3:
$1.00 x 1.50 x 1.4 = $2.10 per DCA buy

---

## 6. Cap Protection System (LOCKED · Original Design)

No other platform has this.

Formula:
Upward: recorded_cap = min(real_cap, previous x 1.10)
Downward: recorded_cap = real_cap (full drop immediately)

Why:
Fake pump: $100M → $500M overnight → recorded as $110M only
Coin stays Small Cap → conservative parameters maintained
Real growth: takes 25+ consecutive days to cross boundary
Fake pumps cannot sustain 25 days → naturally filtered

10% threshold stays as-is. Well-calibrated.

---

## 7. Data Sources (LOCKED)

CoinGecko: market cap ONLY for classification
CMC: market cap ONLY for classification
Average: recorded_cap = (CoinGecko + CMC) / 2
If one fails: use available source
If both fail: use last recorded cap
If disagree > 100%: use LOWER value (conservative)

CCXT: OHLCV + volume for parameter calculation
Never mix classification and parameter data sources.

---

## 8. New Coin Confidence System (LOCKED)

| History | Approach | Badge |
|---------|---------|-------|
| < 30 days | Category defaults only | New |
| 30-90 days | 70% defaults + 30% coin stats | Learning |
| > 90 days | Fully adaptive coin own data | Calibrated |

Spacing for new coins:
Uses category default until 90 days of own data available.

---

## 9. Daily Classification Process (LOCKED)

03:00 - Fetch market cap CoinGecko + CMC
03:30 - Calculate per-coin spacing and TP independently
04:00 - Apply cap protection formula
04:15 - Compare against category boundaries
04:20 - If boundary crossed: reclassify
04:25 - Apply regime-aware TP multiplier
04:30 - Update coin_history table
04:35 - Telegram alert if any coin reclassified
04:40 - Regime detection (5 signals)
05:00 - Research metrics if Sunday

Reclassification: affects NEW positions only
Existing positions keep original params forever (LOCKED)

---

## 10. Research Bots and Classification (LOCKED)

Research bots USE classified params.

Why:
Best entry signal = goes directly to TP with zero DCAs
Classification sets the correct TP target
Research correctly measures: signal quality in real conditions

What we are measuring:
Which entry signal produces fewest DCAs before TP?
Which entry signal produces fastest TP close?
Which signal works best per market regime?

A method that enters so well the coin goes straight to TP
= fewer DCAs = better capital efficiency = higher RARS score
This is exactly what we want to find.

Research bots get same classification as live bots:
- Own spacing from own ATR data
- Regime-aware TP
- Category safety limits
- Cap protection applied

---

## 11. All Locked Decisions

| Decision | Rule |
|----------|------|
| Categories | 5 (Mega/Large/Mid/Small/Micro) |
| Category purpose | Safety limits only (min/max) |
| Spacing | Independent per coin (ATR formula) |
| Volume weighting | REMOVED |
| TP formula | Regime-aware (0.80/0.60/0.70) |
| Cap protection | +10% max upward per day |
| Data sources | CoinGecko + CMC averaged |
| Sector classification | Not now (Phase 6) |
| Reclassification | New positions only |
| Research bots | Use classified params |
| New coin | 30/90 day confidence tiers |
| Nano Cap | <$10M blocked from trading |
