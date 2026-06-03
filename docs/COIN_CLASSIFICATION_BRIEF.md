# Averion Coin Classification System — AI Review Brief
## For AI Validation and Recommendations

---

## 1. Context

Averion is an automated crypto DCA trading platform.
Users create bots on specific coins.
The platform automatically sets DCA parameters per coin.
No user manually sets spacing or TP — system calculates everything.

This brief covers ONE specific question:
Is coin classification the right way to determine DCA parameters?
And if yes, is our current approach correct?

---

## 2. Current Classification System

### 5 Categories by Market Cap:

| Category | Market Cap | Examples | Default Spacing | Default TP |
|----------|-----------|---------|----------------|-----------|
| Mega Cap | >$100B | BTC, ETH | 4-5% | 2-3% |
| Large Cap | $10B-$100B | BNB, SOL, XRP | 6-7% | 3-5% |
| Mid Cap | $1B-$10B | AVAX, LINK | 8-10% | 5-7% |
| Small Cap | $100M-$1B | RVN, HBAR | 10-15% | 6-10% |
| Micro Cap | <$100M | Unknown coins | 15-25% | 8-15% |

### Admin-Only Parameter Limits:

| Category | Spacing Min/Max | Size Multiplier | TP% | Trail% |
|----------|----------------|-----------------|-----|--------|
| Mega Cap | 2%-8% | 1.1x-1.8x | 1%-5% | 0.5%-2% |
| Large Cap | 5%-12% | 1.2x-2.2x | 2%-7% | 1%-3% |
| Mid Cap | 7%-18% | 1.3x-2.8x | 4%-10% | 1.5%-4% |
| Small Cap | 10%-25% | 1.5x-3.5x | 5%-15% | 2%-6% |
| Micro Cap | 15%-40% | 2x-5x | 8%-20% | 3%-8% |

---

## 3. How Parameters Are Calculated Per Coin

### Spacing Formula (current):
spacing = max(ATR_14 x 1.5, median_bounce_threshold x 0.85)
Clamped between category min and max.

ATR_14 = Average True Range over 14 periods (hourly OHLCV)
median_bounce_threshold = median of all drops before price recovery
                          calculated from 90 days of hourly data

### Size Multiplier:
Coin base: Mega=1.10x, Large=1.20x, Mid=1.35x, Small=1.50x, Micro=1.65x
Per DCA level: L1=1.0x, L2=1.2x, L3=1.4x, L4=1.6x, L5+=2.0x cap

### TP Formula:
TP_target = weighted_avg_entry_price x (1 + median_recovery% x 0.70)
Always calculated from actual average cost, not original entry.

### Volume-Weighted Category Parameters (Bader original idea):
Category_Spacing = Sum(coin_spacing x coin_24h_volume) / Sum(all volumes in category)

Example: Mega Cap
BTC: spacing 2.7%, volume $28B, weight 87% → contributes 2.349%
ETH: spacing 3.1%, volume $4B, weight 12.5% → contributes 0.388%
Result: Category spacing = 2.754%

Updates daily as volumes shift.

---

## 4. Cap Protection System (Original Design)

Original idea — no other platform does this.

Formula:
Upward: recorded_cap = min(real_cap, previous x 1.10) — max +10% per day
Downward: recorded_cap = real_cap — full drop immediately

Why:
Fake pump: $100M → $500M overnight → recorded as $110M only
Coin stays Small Cap → conservative parameters maintained
Real growth: takes 25+ consecutive days to cross boundary
Fake pumps cannot sustain 25 days → naturally filtered

---

## 5. Data Sources

CoinGecko: market cap ONLY (for classification)
CMC (CoinMarketCap): market cap ONLY (for classification)
Both averaged: recorded_cap = (CoinGecko + CMC) / 2
If disagree > 100%: use LOWER value (conservative)
CCXT exchanges: OHLCV + volume (for parameter calculation)
Never mixed in same calculation.

---

## 6. New Coin Confidence System

| History | Approach | Badge |
|---------|---------|-------|
| < 30 days | Category defaults + penalty | New |
| 30-90 days | 70% defaults + 30% coin stats | Learning |
| > 90 days | Fully adaptive — coin own data | Calibrated |

---

## 7. Research Bots Question (IMPORTANT)

144 paper research bots test 14 entry methods simultaneously.
Goal: find best entry SIGNAL per market regime.

Question: Should research bots use coin classification for spacing/TP?

Option A: Fixed params for all research bots
Pros: Clean comparison — only entry signal differs
Cons: Winner might not work in real world with real params

Option B: Use classification params for research bots too
Pros: Realistic — mirrors live trading exactly
Cons: Winner might win because of params not signal

Option C: Run two sets — one fixed, one classified
Pros: Full picture
Cons: 288 bots becomes 576

Current decision: NOT decided yet.
This is one of the questions for AIs.

---

## 8. The Core Question for AIs

Is market cap category the RIGHT basis for DCA parameters?

Arguments FOR category-based:
- Simple to understand and explain to users
- Market cap correlates with volatility
- Easy to classify any coin
- Stable (category changes slowly)

Arguments AGAINST:
- Two coins same market cap, very different volatility
- BNB and XRP both Large Cap but behave differently
- Category is a proxy, not the real measure
- ATR already captures actual volatility directly

Alternative approaches to consider:
A) Pure ATR-based (no categories)
   spacing = ATR_14 x multiplier
   No categories at all

B) Volatility tier only (not market cap)
   Low vol: 30d std_dev < 3%
   Medium vol: 3-7%
   High vol: > 7%

C) Hybrid: Category for min/max limits + ATR for exact value
   (current approach - is this best?)

D) Correlation-based
   How correlated is this coin with BTC?
   High correlation = tighter spacing
   Low correlation = wider spacing

---

## 9. Volume-Weighted Spacing Question

Current: category spacing = volume-weighted average of coin spacings
Bader original idea.

Is this the right approach?
Or should each coin have completely independent spacing?

Volume weighting means:
BTC dominates Mega Cap spacing calculation (87% weight)
ETH barely matters (12.5%)
BNB irrelevant (0.5%)

Question: Should a user trading BNB get BTC-dominated spacing?
Or should BNB have its own spacing independently?

---

## 10. Questions for AI Review

1. Is market cap category the right basis for DCA parameters?
   Or is there a fundamentally better approach?

2. Is our spacing formula correct?
   spacing = max(ATR_14 x 1.5, median_bounce x 0.85)
   Clamped to category range.

3. Is volume-weighted category spacing a good idea?
   Or should each coin have independent spacing?

4. Is the cap protection system (10% daily max upward) correct?
   Good idea? Right threshold? Better alternatives?

5. Should research bots use classified params or fixed params?
   What produces more useful research data?

6. Is 5 categories the right number?
   Too many? Too few? Different boundaries?

7. Is TP formula correct?
   TP = weighted_avg_entry x (1 + median_recovery x 0.70)
   Should the 0.70 factor be different?

8. New coin confidence system — is 30/90 day threshold correct?
   Too long? Too short?

9. Should sector/category matter?
   Gaming coins vs Layer 1 vs DeFi
   Different parameters per sector?

10. Is the whole classification system worth the complexity?
    Or is simple ATR-based spacing enough?
    What do professional DCA platforms do?
