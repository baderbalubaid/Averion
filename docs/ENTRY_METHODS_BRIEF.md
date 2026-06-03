# Averion Entry Methods — Complete AI Review Brief
## Goal: Find Every Possible DCA Entry Method Worth Testing

---

## 1. Context — Read This First

Averion is a crypto DCA trading platform.
We run 144 paper research bots simultaneously testing entry methods.
All bots use IDENTICAL DCA parameters (spacing, TP, size multiplier).
The ONLY difference between bots = the entry signal.

Goal of this brief:
Find every entry method worth testing for DCA specifically.
Not general trading — specifically for DCA entry timing.

Why DCA entry timing matters:
Perfect entry = coin goes directly to TP with zero DCAs needed.
Bad entry = coin drops more → needs multiple DCAs → capital tied up.
Best entry method = fewest DCAs + fastest path to TP.

Research system: 6-month paper trading.
Winner = automatically becomes Smart DCA default.
All methods run forever (never deleted).
Full research brief: docs/AI_RESEARCH_SYSTEM_BRIEF_FINAL.md

---

## 2. What We Already Have — E1 to E14

### Single/Pure Indicators:
E10 — Pure Price Drop (no indicator · control group)
E6  — Z-Score Statistical (price vs rolling mean)
E9  — Sequential Candle Decay (6 red candles + reversal)

### Two Indicators Combined:
E1  — VWAP + RSI + ATR + Bounce probability
E2  — Bollinger Band + Volume (panic exhaustion)
E3  — Volume Climax + SMA + ATR
E4  — Time-Cycle Window + SMA (specific weekly times)
E7  — Bollinger Bands + Keltner Channels (squeeze)
E8  — Swing Structure Shift + VWAP
E11 — QFL Base Bounce + Volume filter
E12 — Support/Resistance Reclaim + Volume + Touch count
E14 — Stochastic RSI + EMA Trend Filter

### Three+ Indicators Combined:
E5  — Multi-Timeframe EMA (macro + micro) + RSI
E13 — EMA + MACD + RSI Confluence

### Full Parameter Grids (E1-E14):

#### E1 — VWAP + RSI (12 bots)
| Bot | RSI | VWAP% | ATR | Bounce |
|-----|-----|-------|-----|--------|
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

Entry: RSI oversold + price X% below VWAP + ATR spike + bounce prob

#### E2 — Panic Exhaustion (9 bots)
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

Entry: Previous candle pierced BB → current closes back inside + volume spike

#### E3 — Volume Climax (12 bots)
| Bot | Volume | Range/ATR | Close Position |
|-----|--------|-----------|---------------|
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

Entry: Volume spike + price below SMA + large candle range closing high

#### E4 — Time-Cycle Window (9 bots)
| Bot | SMA Lookback | Window |
|-----|-------------|--------|
| E4-1 | 1h SMA | Sun 22:00 · Mon 00:00 · Wed 12:00 |
| E4-2 | 1h SMA | Same windows |
| E4-3 | 1h SMA | Same windows |
| E4-4 | 2h SMA | Same windows |
| E4-5 | 2h SMA | Same windows |
| E4-6 | 2h SMA | Same windows |
| E4-7 | 4h SMA | Same windows |
| E4-8 | 4h SMA | Same windows |
| E4-9 | 4h SMA | Same windows |

Entry: Price below SMA during specific weekly time windows

#### E5 — Multi-Timeframe EMA (12 bots)
| Bot | Macro EMA | Pullback EMA | RSI |
|-----|-----------|-------------|-----|
| E5-1 | 144h | 12h | 35 |
| E5-2 | 144h | 24h | 40 |
| E5-3 | 144h | 36h | 45 |
| E5-4 | 168h | 12h | 35 |
| E5-5 | 168h | 24h | 40 |
| E5-6 | 168h | 36h | 45 |
| E5-7 | 200h | 12h | 35 |
| E5-8 | 200h | 24h | 40 |
| E5-9 | 200h | 36h | 45 |
| E5-10 | 168h | 24h | 35 |
| E5-11 | 168h | 24h | 45 |
| E5-12 | 200h | 36h | 40 |

Entry: Price above macro EMA (uptrend) + below pullback EMA (dip) + RSI oversold

#### E6 — Z-Score Statistical (9 bots)
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

Entry: Price X standard deviations below rolling mean

#### E7 — Volatility Squeeze (9 bots)
| Bot | Squeeze Duration | Volume |
|-----|-----------------|--------|
| E7-1 | 8h | 1.0x |
| E7-2 | 12h | 1.0x |
| E7-3 | 24h | 1.0x |
| E7-4 | 8h | 1.5x |
| E7-5 | 12h | 1.5x |
| E7-6 | 24h | 1.5x |
| E7-7 | 8h | 2.0x |
| E7-8 | 12h | 2.0x |
| E7-9 | 24h | 2.0x |

Entry: Bollinger Bands inside Keltner Channels (squeeze) then breakout + volume

#### E8 — Swing Structure Shift (9 bots)
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

Entry: Lower low confirmed + price closes above last swing high + above VWAP

#### E9 — Sequential Candle Decay (9 bots)
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

Entry: N consecutive red candles + green reversal candle with volume

#### E10 — Pure Drop Threshold (12 bots · control group)
| Bot | Drop % | Lookback |
|-----|--------|---------|
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

Entry: Price drops X% from recent high (no indicators)

#### E11 — QFL Base Bounce (9 bots)
| Bot | Base Break % |
|-----|------------|
| E11-1 | 2% |
| E11-2 | 3% |
| E11-3 | 4% |
| E11-4 | 5% |
| E11-5 | 6% |
| E11-6 | 8% |
| E11-7 | 10% |
| E11-8 | 12% |
| E11-9 | 15% |

Fixed: Base Age=72h · Volume=1.5x · Reclaim required
Entry: Price breaks consolidation base by X% + reclaims it + volume

#### E12 — Support/Resistance Reclaim (9 bots)
| Bot | Reclaim % | Touch Count | Volume |
|-----|-----------|------------|--------|
| E12-1 | 0.5% | 2 | 1.2x |
| E12-2 | 1.0% | 2 | 1.4x |
| E12-3 | 1.5% | 3 | 1.6x |
| E12-4 | 2.0% | 3 | 1.8x |
| E12-5 | 2.5% | 4 | 2.0x |
| E12-6 | 3.0% | 4 | 2.2x |
| E12-7 | 3.5% | 5 | 2.4x |
| E12-8 | 4.0% | 5 | 2.6x |
| E12-9 | 5.0% | 6 | 3.0x |

Entry: Price breaks support → closes back above by X% + volume + N prior touches

#### E13 — EMA + MACD + RSI Confluence (10 bots)
| Bot | Fast EMA | Slow EMA | RSI Max |
|-----|----------|----------|--------|
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
Entry: EMA cross + MACD bullish + RSI oversold threshold

#### E14 — Stochastic RSI Pullback + Trend (9 bots)
| Bot | Stoch RSI | Trend EMA | Recovery Closes |
|-----|-----------|-----------|----------------|
| E14-1 | 10 | 50 | 1 |
| E14-2 | 12 | 55 | 1 |
| E14-3 | 14 | 60 | 1 |
| E14-4 | 16 | 65 | 2 |
| E14-5 | 18 | 70 | 2 |
| E14-6 | 20 | 75 | 2 |
| E14-7 | 22 | 80 | 2 |
| E14-8 | 24 | 90 | 3 |
| E14-9 | 26 | 100 | 3 |

Fixed: Period=14 · %K crosses above %D trigger
Entry: Price above trend EMA + Stoch RSI oversold + %K/%D crossover

---

## 3. Indicators We Have Used So Far

| Indicator | Used In |
|-----------|--------|
| RSI | E1 · E5 · E13 |
| VWAP | E1 · E8 |
| ATR | E1 · E3 |
| Bollinger Bands | E2 · E7 |
| Volume | E2 · E3 · E7 · E11 · E12 |
| SMA | E3 · E4 |
| EMA | E5 · E13 · E14 |
| Z-Score | E6 |
| Keltner Channels | E7 |
| Swing Structure | E8 |
| Candle Patterns | E9 |
| Price Drop | E10 |
| QFL Base | E11 |
| Support/Resistance | E12 |
| MACD | E13 |
| Stochastic RSI | E14 |

---

## 4. Indicators NOT Yet Used

| Indicator | Description |
|-----------|------------|
| Ichimoku Cloud | Complete system: Tenkan/Kijun/Senkou/Chikou |
| Fibonacci Retracement | 23.6% · 38.2% · 50% · 61.8% · 78.6% levels |
| OBV (On Balance Volume) | Cumulative volume pressure |
| CCI (Commodity Channel Index) | Price deviation from statistical mean |
| Williams %R | Momentum oscillator -100 to 0 |
| Parabolic SAR | Trend following stop and reverse |
| Supertrend | ATR-based trend direction |
| Heikin Ashi | Smoothed candle pattern system |
| ADX (Average Directional Index) | Trend strength (not direction) |
| Aroon Indicator | Trend detection and strength |
| TRIX | Triple smoothed EMA momentum |
| Awesome Oscillator | Market momentum (SMA based) |
| Hull Moving Average | Reduced lag moving average |
| Pivot Points | Classic support/resistance levels |
| Market Profile / VPOC | Volume at price levels |
| Divergence (RSI/MACD) | Price vs indicator disagreement |
| Order Block | Institutional price levels |
| Fair Value Gap | Price imbalance zones |
| Liquidity Sweep | Stop hunt detection |

---

## 5. Combination Categories Not Yet Tested

### Momentum + Volume:
RSI + OBV → oversold + volume accumulation
MACD + Volume surge → momentum + participation
Stoch + OBV divergence → momentum vs volume conflict

### Trend + Momentum:
ADX + RSI → strong trend + oversold
Supertrend + Stoch RSI → trend direction + timing
Ichimoku + RSI → complete trend system + oversold

### Statistical + Momentum:
Z-Score + RSI → statistically extreme + momentum extreme
Bollinger %B + RSI → position in band + momentum

### Price Action + Volume:
Order Block + Volume → institutional level + confirmation
Fair Value Gap + OBV → imbalance zone + volume
Fibonacci + Volume → key level + participation

### Multi-Indicator Confluence (3+):
EMA200 + RSI + MACD + Volume (4 confirmations)
Ichimoku + RSI + Volume (complete system)
Fibonacci + VWAP + RSI + OBV (level + fair value + momentum + volume)

---

## 6. Important Considerations for AI

### DCA-specific constraints:
- We enter LONG only (no shorting in main system)
- We want entries that catch PULLBACKS in uptrends
- OR entries that catch BOTTOMS in downtrends
- Entry signal fires → position opens → bot waits for TP
- BEST signal = coin goes directly up to TP → zero DCAs
- WORST signal = coin keeps falling → needs 5+ DCAs

### Server constraints:
- All calculations from hourly OHLCV data (already collected)
- No external APIs beyond what we have
- Calculation runs every 60 seconds per active bot
- Must be computationally simple enough for 288 bots

### Research constraints:
- Each method needs 9-12 parameter variations
- Clear most important parameter to vary
- Fixed secondary parameters
- Clean hypothesis being tested

### What works best for DCA specifically:
- Mean reversion signals (oversold → recovery)
- Support level identification
- Volume exhaustion signals
- Momentum reversal confirmations
- NOT: trend following (we want to buy dips not breakouts)

---

## 7. Current Bot Count

| Method | Bots | Category |
|--------|------|---------|
| E1 | 12 | VWAP + RSI + ATR |
| E2 | 9 | BB + Volume |
| E3 | 12 | Volume Climax |
| E4 | 9 | Time Cycle |
| E5 | 12 | Multi-EMA + RSI |
| E6 | 9 | Z-Score |
| E7 | 9 | BB Squeeze |
| E8 | 9 | Swing Structure |
| E9 | 9 | Candle Pattern |
| E10 | 12 | Pure Drop (control) |
| E11 | 9 | QFL Base |
| E12 | 9 | S/R Reclaim |
| E13 | 10 | EMA+MACD+RSI |
| E14 | 9 | Stoch RSI |
| Benchmarks | 5 | Hold + Simple DCA |
| TOTAL | 144 | |

Current limit: 144 bots for server balance.
Can expand to 200+ if server handles it (CX33 upgrade).

---

## 8. Questions for AI Review

1. Looking at our 14 methods — what important entry
   philosophy or indicator category did we completely miss?

2. Which indicators from our "not yet used" list
   would you prioritize for DCA entry specifically?
   Why those over others?

3. What are the best 2-indicator combinations for
   catching DCA entry points (pullbacks + bottoms)?

4. What are the best 3-indicator combinations?
   Is there diminishing returns after 3 indicators?

5. Should we test pure price action methods?
   (No indicators — just candle patterns, market structure)
   Examples: hammer candles · engulfing · morning star

6. Divergence testing:
   RSI divergence (price lower low · RSI higher low)
   MACD divergence
   OBV divergence
   Are these worth testing for DCA?

7. Ichimoku — is it worth testing as a complete system?
   Or too complex / too many parameters?

8. Fibonacci levels:
   Are they self-fulfilling enough to work in crypto?
   How would you test them for DCA entry?

9. What parameter ranges should we test for each
   new method you suggest?
   Please give: method name · logic · parameters · range

10. Looking at our existing E1-E14:
    Are there any methods that are essentially testing
    the same thing with different labels?
    Any redundancies we should remove?

11. What is the maximum useful number of methods?
    Is 14 enough? Should we go to 20? 25?
    At what point does adding more methods lose value?

12. If you had to pick 5 methods most likely to work
    for DCA entry in crypto specifically —
    which 5 and why?
    (Not for us to use — just to validate our thinking)

13. Are there any completely different approaches
    we have not considered at all?
    On-chain data? Sentiment? Order book analysis?
    What about combining on-chain with technical?

14. Should any of our existing methods be improved?
    E.g. E10 (pure drop) — should it add a filter?
    E9 (candle decay) — is 6 red candles too specific?

15. What would make this research system the most
    comprehensive DCA entry method study ever done
    in crypto? What are we still missing?

---

## FINAL SUMMARY — All 26 Methods Locked

### Complete Method List:

| Method | Name | Bots | Philosophy |
|--------|------|------|-----------|
| E1 | VWAP + RSI + ATR | 12 | Mean reversion + value |
| E2 | Panic Exhaustion | 9 | BB + volume exhaustion |
| E3 | Volume Climax | 12 | Volume + price action |
| E4 | Time-Cycle Window | 9 | Time-based entry |
| E5 | Multi-Timeframe EMA | 12 | Trend pullback |
| E6 | Z-Score Statistical | 9 | Pure mean reversion |
| E7 | Volatility Squeeze | 9 | Breakout from compression |
| E8 | Swing Structure Shift | 9 | Market structure |
| E9 | Sequential Candle Decay | 9 | Candle pattern |
| E10 | Pure Drop Threshold | 12 | Control group |
| E11 | QFL Base Bounce | 9 | Crypto-native base break |
| E12 | S/R Reclaim | 9 | Support reclaim |
| E13 | EMA + MACD + RSI | 10 | Triple confluence |
| E14 | Stoch RSI Pullback | 9 | Oversold + trend |
| E15 | OBV Divergence | 9 | Volume accumulation |
| E16 | RSI Divergence | 9 | Momentum divergence |
| E17 | Liquidity Sweep | 9 | Stop hunt reversal |
| E18 | ADX Trend Pullback | 9 | Trend strength filter |
| E19 | Fibonacci Retracement | 9 | Key level entry |
| E20 | VPOC Volume Profile | 9 | Volume node support |
| E21 | Fair Value Gap | 9 | Price imbalance fill |
| E22 | Hammer/Engulfing | 9 | Pure price action |
| E23 | Relative Strength vs BTC | 9 | Crypto-specific |
| E24 | Funding Rate Extreme | 9 | Short squeeze signal |
| E25 | Supertrend + RSI | 9 | ATR trend + oversold |
| E26 | Ichimoku Simplified | 9 | Cloud-based reversion |
| Benchmarks | 5 methods | 5 | BTC Hold · ETH · Simple · Random · Static |

Total method bots: 247
Total with benchmarks: 252

### Signal Families Covered:
✅ Mean reversion (E1 · E6 · E10)
✅ Volume exhaustion (E2 · E3)
✅ Trend pullback (E4 · E5 · E13 · E14 · E18 · E25)
✅ Volatility (E7 · E11)
✅ Market structure (E8 · E12 · E17 · E22)
✅ Statistical (E6 · E9)
✅ Divergence (E15 · E16)
✅ Volume profile (E20)
✅ Price imbalance (E21)
✅ Fibonacci (E19)
✅ Relative performance (E23)
✅ Crypto-specific (E11 · E24)
✅ Cloud system (E26)
✅ Control group (E10 · benchmarks)

### DCA-Specific Scoring Metrics:
Primary RARS: Capital Efficiency 35% + Drawdown 30% + Win Rate 20% + Profit Factor 15%
Additional tracking per method:
- avg_dca_count (fewer = better entry quality)
- avg_days_to_tp (faster = better)
- max_capital_deployed (lower = more efficient)
- regime_performance (bull/bear/sideways separate)

### Server Plan:
252 Long bots → CX33 (€17.99/month)
252 Short bots (Phase 2) → same server
Total at full capacity: 504 research bots

### All decisions locked. Ready to code on Hetzner Day 3.
