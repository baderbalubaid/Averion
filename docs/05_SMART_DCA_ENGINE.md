# Smart DCA Engine

> The brain of Averion.
> Auto-classification · 10 entry methods · research system · equations.

---

## Philosophy
- Survivability first · Controlled recovery second · Profit third
- Platform gets smarter every year automatically
- Data decides winners — not opinions

---

## Five Market Cap Categories

| Category | Market Cap | Examples | Default Spacing | Default TP |
|----------|-----------|---------|----------------|-----------|
| Mega Cap | >$100B | BTC · ETH | 4-5% | 2-3% |
| Large Cap | $10B-$100B | BNB · SOL · XRP | 6-7% | 3-5% |
| Mid Cap | $1B-$10B | AVAX · LINK · INJ | 8-10% | 5-7% |
| Small Cap | $100M-$1B | RVN · HBAR · CELO | 10-15% | 6-10% |
| Micro Cap | <$100M | Unknown/new coins | 15-25% | 8-15% |

Customers see category name ONLY.
All boundaries and parameters = admin only — never shown to customers.

---

## Admin-Only Parameter Limits

| Category | Spacing Min/Max | Size Mult | TP% | Trail% |
|----------|----------------|-----------|-----|--------|
| Mega Cap | 2% — 8% | 1.1x — 1.8x | 1% — 5% | 0.5% — 2% |
| Large Cap | 5% — 12% | 1.2x — 2.2x | 2% — 7% | 1% — 3% |
| Mid Cap | 7% — 18% | 1.3x — 2.8x | 4% — 10% | 1.5% — 4% |
| Small Cap | 10% — 25% | 1.5x — 3.5x | 5% — 15% | 2% — 6% |
| Micro Cap | 15% — 40% | 2x — 5x | 8% — 20% | 3% — 8% |

---

## Smart DCA Calculations

### What It Calculates Automatically
- Reads 90 days of hourly OHLCV data per coin per exchange
- Calculates optimal spacing using ATR_14 + median bounce threshold
- Calculates size multiplier from category base + per-level escalation
- Calculates TP from weighted average entry + median recovery
- Volume-weighted category parameters
- Updates all parameters daily at 3am

### Spacing Formula (LOCKED)
- spacing = max(ATR_14 x 1.5, median_bounce_threshold x 0.85)
- Clamped between category min and max

### Example — BTC (Mega Cap)
- ATR daily = 1.8% → ATR x 1.5 = 2.7%
- Median drop before bounce = 3.1% → x 0.85 = 2.6%
- max(2.7%, 2.6%) = 2.7% → within Mega Cap range ✅

### Example — RVN (Small Cap)
- ATR daily = 4.2% → ATR x 1.5 = 6.3%
- Median drop before bounce = 8.4% → x 0.85 = 7.1%
- max(6.3%, 7.1%) = 7.1% → below Small Cap floor 10% → clamped to 10% ✅

### TP Formula
- TP_target = weighted_avg_entry_price x (1 + median_recovery% x 0.70)
- Always from YOUR actual average cost — not original entry

### Size Multiplier
- Coin base: Mega=1.10x · Large=1.20x · Mid=1.35x · Small=1.50x · Micro=1.65x
- Per level: L1=1.0x · L2=1.2x · L3=1.4x · L4=1.6x · L5+=2.0x hard cap
- Example Small Cap L3: $1.00 x 1.50 x 1.4 = $2.10 per DCA buy

### Always Use MEDIAN Not MEAN
- Sample: 2% · 3% · 4% · 5% · 40%
- Mean = 10.8% (distorted by flash crash)
- Median = 4% (actual typical behavior) ✅

---

## Volume-Weighted Category Parameters

Formula:
Category_Spacing = Sum(coin_spacing x coin_24h_volume) / Sum(all volumes in category)

### Example — Mega Cap
| Coin | Spacing | 24h Volume | Weight | Contribution |
|------|---------|-----------|--------|-------------|
| BTC | 2.7% | $28B | 87.0% | 2.349% |
| ETH | 3.1% | $4B | 12.5% | 0.388% |
| BNB | 3.4% | $200M | 0.5% | 0.017% |
| Result | — | $32.2B | 100% | 2.754% |

Updates daily at 3am as volumes shift.

---

## Auto-Classification Engine

### Data Sources (LOCKED)
- Exchange data via CCXT: coin list + volume + OHLCV
- CoinGecko: market cap ONLY for classification
- Never mixed in same calculation

### Daily 3am Process
1. Fetch market cap from CoinGecko at 03:30 · from CMC at 04:00 (separate cron steps)
2. Average both sources: (CoinGecko + CMC) / 2 · see averaging formula in locked decisions
3. Apply cap protection formula
3. Compare against category boundaries
4. If boundary crossed → reclassify immediately
5. Apply new parameters to NEW positions only (existing positions keep original parameters — see 13_LOCKED_DECISIONS.md)
6. Log in coin_history table
7. Telegram alert if any coin reclassified

### CoinGecko Failure Fallback
- Use last recorded market cap from coin_history
- Skip reclassification that day
- Telegram alert: CoinGecko failed — using last recorded caps
- Retry next 3am automatically

### Averaging Formula (LOCKED)
- Both sources: recorded_cap = (CoinGecko + CMC) / 2
- One source only: use available source
- Both failed: use last recorded cap
- Disagreement > 100%: use LOWER value (conservative)

### New Coin Tiered Confidence
| History | Approach | Badge |
|---------|---------|-------|
| < 30 days | Category defaults + penalty | 🔴 New |
| 30-90 days | 70% defaults + 30% coin stats | 🟡 Learning |
| > 90 days | Fully adaptive — coin's own data | 🟢 Calibrated |

---

## Cap Protection System (LOCKED)

Original idea by Bader. No other platform does this.

### Formula
- Upward: recorded_cap = min(real_cap, previous x 1.10) — max +10% per day
- Downward: recorded_cap = real_cap — full drop immediately

### Why It Works
- Fake pump: $100M → $500M overnight → recorded as $110M only
- Coin stays Small Cap → conservative parameters maintained
- Real growth: takes 25+ consecutive days to cross category boundary
- Fake pumps cannot sustain 25 days → naturally filtered

---

## 10 Entry Methods

All run simultaneously in paper mode.
Same coins · same DCA params · only entry signal differs.
3-12 months data decides winner.
Worst deleted · best becomes Smart DCA default.

### 5 Benchmark Bots (always running)
- BTC Buy & Hold — pure market exposure
- ETH Buy & Hold — pure market exposure
- Simple DCA — ASAP entry no signal
- Random Entry DCA — control group
- Static Spacing DCA — tests if widening adds value

### E1 — VWAP + RSI Deviation (Current Baseline)
- RSI < 35 (oversold)
- VWAP distance > 3% below
- ATR > 1.5x 30-day average (volatility spike)
- Bounce probability > 60%
- ALL FOUR required simultaneously

### E2 — Panic Exhaustion
- Previous candle pierced below lower Bollinger Band
- Current candle closes back inside band
- Volume > 2x 24h average
- Current candle closes green

### E3 — Volume Climax
- Volume > 4x SMA(Volume, 72)
- Close < SMA(Close, 24)
- Candle range > 2.5x ATR · close in upper 50%

### E4 — Time-Cycle Window
- Sunday UTC 22:00-23:00 only
- Close < SMA(Close, 48)

### E5 — Multi-Timeframe Alignment
- Close > EMA(Close, 168) — bullish macro
- Close < EMA(Close, 24) — micro pullback
- RSI(14) < 45
- Close > Close[1] — first green candle

### E6 — Z-Score Statistical
- Z = (Close - Rolling_Mean_168h) / Rolling_StdDev_168h
- Entry when Z < -2.5

### E7 — Volatility Squeeze
- Bollinger Bands inside Keltner Channels >= 12 hours
- Current close > Upper Bollinger Band
- Volume > SMA(Volume, 24)

### E8 — Swing Structure Shift
- Lower low within past 48 hours confirmed
- Last swing high identified (high > 3 candles before AND after)
- Close > last swing high
- Close > Trailing VWAP(24)

### E9 — Sequential Candle Decay
- 6 consecutive red candles (lower closes)
- 7th candle: green AND volume > avg of prior 6

### E10 — Pure Drop Threshold (Control Group)
- Price drops X% from recent 24h high → enter
- No indicators — pure price drop only
- Most important benchmark — measures if signals add value

---

## Research System

### What Gets Stored Per Trade
- Entry method + version
- Full market context (BTC trend · regime · volatility)
- All signal values at entry
- DCA progression
- Exit details + profit

### Parameter Versioning
- Every parameter change creates new version
- Old versions kept for comparison
- Never mix results between versions
- 30-day cooldown enforced after any change

### Monthly Review Workflow
1. Generate signed research URL (1 click in admin)
2. Share URL with Claude → get analysis
3. Share same URL with ChatGPT → second opinion
4. Compare recommendations
5. Approve changes in admin panel
6. 30-day cooldown starts automatically

### Three-Speed Evaluation
- Daily: automatic health check → Telegram alert if flagged
- Monthly: 5 minutes → share URL → approve changes
- Quarterly: 10 minutes → delete worst · promote winners

## Research Bot Grid (LOCKED — ChatGPT Validated)

Total: 144 paper bots (139 method bots + 5 benchmarks)
Period: 6 months · no mid-period adjustments
Scaling: start 10 trades/bot → 20 → 30 gradually

### Bot Count Per Method
- E1 VWAP+RSI: 12 bots (RSI · VWAP · ATR · Bounce variations)
- E2 Panic Exhaustion: 9 bots (Volume · BB · Recovery variations)
- E3 Volume Climax: 12 bots (Volume multiple · Range · Close position)
- E4 Time-Cycle: 9 bots (Window duration · SMA length)
- E5 Multi-Timeframe: 12 bots (Macro EMA · Pullback EMA · RSI)
- E6 Z-Score: 9 bots (Z trigger · Lookback period)
- E7 Volatility Squeeze: 9 bots (Squeeze duration · Volume filter)
- E8 Swing Structure: 9 bots (Detection width · VWAP length)
- E9 Sequential Candle: 9 bots (Red candle count · Reversal volume)
- E10 Pure Drop: 12 bots (Drop threshold · Lookback high)

### 5 Benchmark Bots (always running)
- BTC Buy and Hold
- ETH Buy and Hold
- Simple DCA (ASAP entry)
- Random Entry DCA
- Static Spacing DCA

### Full Parameter Grid
Stored in: docs/05_SMART_DCA_ENGINE.md
Validated by ChatGPT May 2026
Each bot tests unique parameter hypothesis
Mathematical progression — no random values

## Detailed Parameter Grid Per Method

### E1 — VWAP + RSI (12 bots)
| Bot | RSI | VWAP | ATR | Bounce |
|-----|-----|------|-----|--------|
| E1-1 | 25 | 4% | 1.5x | 65% |
| E1-2 | 30 | 4% | 1.5x | 65% |
| E1-3 | 35 | 4% | 1.5x | 65% |
| E1-4 | 25 | 3% | 1.5x | 65% |
| E1-5 | 30 | 3% | 1.5x | 65% |
| E1-6 | 35 | 3% | 1.5x | 65% |
| E1-7 | 25 | 2% | 1.5x | 65% |
| E1-8 | 30 | 2% | 1.5x | 65% |
| E1-9 | 35 | 2% | 1.5x | 65% |
| E1-10 | 30 | 3% | 1.3x | 65% |
| E1-11 | 30 | 3% | 1.5x | 55% |
| E1-12 | 35 | 2% | 1.3x | 55% |

### E2 — Panic Exhaustion (9 bots)
| Bot | Volume | BB Sigma | Recovery |
|-----|--------|----------|---------|
| E2-1 | 1.5x | 2.0 | 0.5% |
| E2-2 | 2.0x | 2.0 | 0.5% |
| E2-3 | 3.0x | 2.0 | 0.5% |
| E2-4 | 1.5x | 2.5 | 0.5% |
| E2-5 | 2.0x | 2.5 | 0.5% |
| E2-6 | 3.0x | 2.5 | 0.5% |
| E2-7 | 2.0x | 2.0 | 1.0% |
| E2-8 | 2.0x | 2.5 | 1.0% |
| E2-9 | 3.0x | 2.5 | 1.0% |

### E3 — Volume Climax (12 bots)
| Bot | Volume | Range vs ATR | Close Position |
|-----|--------|-------------|---------------|
| E3-1 | 3x | 2.0x | Upper 40% |
| E3-2 | 4x | 2.0x | Upper 40% |
| E3-3 | 5x | 2.0x | Upper 40% |
| E3-4 | 3x | 2.5x | Upper 50% |
| E3-5 | 4x | 2.5x | Upper 50% |
| E3-6 | 5x | 2.5x | Upper 50% |
| E3-7 | 3x | 3.0x | Upper 60% |
| E3-8 | 4x | 3.0x | Upper 60% |
| E3-9 | 5x | 3.0x | Upper 60% |
| E3-10 | 4x | 2.0x | Upper 60% |
| E3-11 | 4x | 3.0x | Upper 40% |
| E3-12 | 5x | 3.0x | Upper 50% |

### E4 — Time-Cycle Window (9 bots)
| Bot | Window | SMA Length |
|-----|--------|-----------|
| E4-1 | 1h | 24 |
| E4-2 | 1h | 48 |
| E4-3 | 1h | 72 |
| E4-4 | 2h | 24 |
| E4-5 | 2h | 48 |
| E4-6 | 2h | 72 |
| E4-7 | 4h | 24 |
| E4-8 | 4h | 48 |
| E4-9 | 4h | 72 |

### E5 — Multi-Timeframe (12 bots)
| Bot | Macro EMA | Pullback EMA | RSI |
|-----|-----------|-------------|-----|
| E5-1 | 144 | 12 | 35 |
| E5-2 | 144 | 24 | 40 |
| E5-3 | 144 | 36 | 45 |
| E5-4 | 168 | 12 | 35 |
| E5-5 | 168 | 24 | 40 |
| E5-6 | 168 | 36 | 45 |
| E5-7 | 200 | 12 | 35 |
| E5-8 | 200 | 24 | 40 |
| E5-9 | 200 | 36 | 45 |
| E5-10 | 168 | 24 | 35 |
| E5-11 | 168 | 24 | 45 |
| E5-12 | 200 | 36 | 40 |

### E6 — Z-Score Statistical (9 bots)
| Bot | Z Trigger | Lookback |
|-----|-----------|---------|
| E6-1 | -2.0 | 96h |
| E6-2 | -2.5 | 96h |
| E6-3 | -3.0 | 96h |
| E6-4 | -2.0 | 168h |
| E6-5 | -2.5 | 168h |
| E6-6 | -3.0 | 168h |
| E6-7 | -2.0 | 336h |
| E6-8 | -2.5 | 336h |
| E6-9 | -3.0 | 336h |

### E7 — Volatility Squeeze (9 bots)
| Bot | Squeeze Duration | Volume Filter |
|-----|-----------------|--------------|
| E7-1 | 8h | 1.0x |
| E7-2 | 12h | 1.0x |
| E7-3 | 24h | 1.0x |
| E7-4 | 8h | 1.5x |
| E7-5 | 12h | 1.5x |
| E7-6 | 24h | 1.5x |
| E7-7 | 8h | 2.0x |
| E7-8 | 12h | 2.0x |
| E7-9 | 24h | 2.0x |

### E8 — Swing Structure Shift (9 bots)
| Bot | Swing Detection | VWAP Length |
|-----|----------------|------------|
| E8-1 | 2 candles | 12h |
| E8-2 | 2 candles | 24h |
| E8-3 | 2 candles | 48h |
| E8-4 | 3 candles | 12h |
| E8-5 | 3 candles | 24h |
| E8-6 | 3 candles | 48h |
| E8-7 | 5 candles | 12h |
| E8-8 | 5 candles | 24h |
| E8-9 | 5 candles | 48h |

### E9 — Sequential Candle Decay (9 bots)
| Bot | Red Candles | Reversal Volume |
|-----|------------|----------------|
| E9-1 | 5 | 1.0x |
| E9-2 | 6 | 1.0x |
| E9-3 | 7 | 1.0x |
| E9-4 | 5 | 1.5x |
| E9-5 | 6 | 1.5x |
| E9-6 | 7 | 1.5x |
| E9-7 | 5 | 2.0x |
| E9-8 | 6 | 2.0x |
| E9-9 | 7 | 2.0x |

### E10 — Pure Drop Threshold (12 bots)
| Bot | Drop % | Lookback High |
|-----|--------|--------------|
| E10-1 | 3% | 12h |
| E10-2 | 5% | 12h |
| E10-3 | 7% | 12h |
| E10-4 | 10% | 12h |
| E10-5 | 15% | 12h |
| E10-6 | 3% | 24h |
| E10-7 | 5% | 24h |
| E10-8 | 7% | 24h |
| E10-9 | 10% | 24h |
| E10-10 | 15% | 24h |
| E10-11 | 5% | 48h |
| E10-12 | 10% | 48h |

## New Entry Methods — E11 to E14 (Added After AI Review)

### E11 — QFL Base Bounce (9 bots)
Concept: Price breaks below historical base → enter on rejection
Most important parameter: Base Break %

| Bot | Base Break % | Notes |
|-----|-------------|-------|
| E11-1 | 2% | Aggressive · many entries |
| E11-2 | 3% | Standard micro crack |
| E11-3 | 4% | Moderate break |
| E11-4 | 5% | Strong break required |
| E11-5 | 6% | High conviction |
| E11-6 | 8% | Deep liquidation |
| E11-7 | 10% | Major capitulation |
| E11-8 | 12% | Extreme event |
| E11-9 | 15% | Ultra conservative |

Fixed: Base Age=72h · Volume Filter=1.5x · Reclaim required

Entry logic:
- Identify base from 72h OHLCV consolidation
- Price breaks below base by Break%
- Volume spike >= 1.5x average
- Close back above base → entry

---

### E12 — Support/Resistance Reclaim (9 bots)
Concept: Price breaks support → reclaims it → entry
Most important parameter: Reclaim Distance %

| Bot | Reclaim % | Touch Count | Volume |
|-----|-----------|-------------|--------|
| E12-1 | 0.5% | 2 | 1.2x |
| E12-2 | 1.0% | 2 | 1.4x |
| E12-3 | 1.5% | 3 | 1.6x |
| E12-4 | 2.0% | 3 | 1.8x |
| E12-5 | 2.5% | 4 | 2.0x |
| E12-6 | 3.0% | 4 | 2.2x |
| E12-7 | 3.5% | 5 | 2.4x |
| E12-8 | 4.0% | 5 | 2.6x |
| E12-9 | 5.0% | 6 | 3.0x |

Fixed: Lookback=30 days · Confirmation=1 candle close above

Entry logic:
- Find support from swing lows over 30 days
- Price breaks below support
- Closes back above support by Reclaim%
- Volume >= required · Touch Count prior tests confirmed

---

### E13 — EMA + MACD + RSI Confluence (10 bots)
Concept: Three confirmations before entry
Most important parameter: EMA pair (trend speed)

| Bot | Fast EMA | Slow EMA | RSI Max |
|-----|----------|----------|---------|
| E13-1 | 9 | 21 | 35 |
| E13-2 | 10 | 24 | 37 |
| E13-3 | 12 | 26 | 39 |
| E13-4 | 14 | 30 | 41 |
| E13-5 | 16 | 34 | 43 |
| E13-6 | 18 | 40 | 45 |
| E13-7 | 20 | 50 | 47 |
| E13-8 | 22 | 55 | 49 |
| E13-9 | 24 | 60 | 51 |
| E13-10 | 26 | 70 | 53 |

Fixed: MACD 12/26/9 · Price above EMA200 · Histogram rising 2 candles

Entry logic:
- Price above EMA200 (macro bull)
- Fast EMA crosses above Slow EMA
- MACD line above signal · histogram rising
- RSI <= RSI Max threshold
- All conditions met → entry

---

### E14 — Stoch RSI Pullback + Trend Filter (9 bots)
Concept: Oversold Stoch RSI during uptrend
Most important parameter: Oversold threshold + Trend EMA

| Bot | Stoch RSI Oversold | Trend EMA | Recovery |
|-----|-------------------|-----------|----------|
| E14-1 | 10 | 50 | 1 close |
| E14-2 | 12 | 55 | 1 close |
| E14-3 | 14 | 60 | 1 close |
| E14-4 | 16 | 65 | 2 closes |
| E14-5 | 18 | 70 | 2 closes |
| E14-6 | 20 | 75 | 2 closes |
| E14-7 | 22 | 80 | 2 closes |
| E14-8 | 24 | 90 | 3 closes |
| E14-9 | 26 | 100 | 3 closes |

Fixed: Stoch RSI 14 period · %K crosses above %D as trigger

Entry logic:
- Price above Trend EMA (uptrend confirmed)
- Stoch RSI %K drops below oversold threshold
- %K crosses above %D from oversold zone
- Recovery closes confirmed → entry

---

### Updated Research Bot Count

| Method | Bots |
|--------|------|
| E1 VWAP+RSI | 12 |
| E2 Panic Exhaustion | 9 |
| E3 Volume Climax | 12 |
| E4 Time-Cycle Window | 9 |
| E5 Multi-Timeframe | 12 |
| E6 Z-Score Statistical | 9 |
| E7 Volatility Squeeze | 9 |
| E8 Swing Structure | 9 |
| E9 Sequential Candle | 9 |
| E10 Pure Drop (control) | 12 |
| E11 QFL Base Bounce | 9 |
| E12 S/R Reclaim | 9 |
| E13 EMA+MACD+RSI | 10 |
| E14 Stoch RSI Pullback | 9 |
| Benchmarks | 5 |
| **TOTAL** | **144** |

