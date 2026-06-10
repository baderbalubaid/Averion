# Averion Research Bots — All Methods & Parameter Variants

> Auto-generated · All bots: Dynamic TP/DCA/trail per coin category

## Summary

| Method | Description | Variants |
|--------|-------------|----------|
| **BM_HOLD** | Benchmark: Buy and Hold | 2 |
| **BM_RANDOM** | Benchmark: Random Entry | 1 |
| **BM_SIMPLE** | Benchmark: Simple Drop Buy | 1 |
| **BM_STATIC** | Benchmark: Fixed Spacing | 1 |
| **E1** | RSI Oversold + VWAP Drop + ATR Spike + Bounce | 12 |
| **E2** | Bollinger Band Squeeze Breakout | 9 |
| **E3** | Volume Spike + Narrow Range Candle | 12 |
| **E4** | SMA Pullback Entry | 9 |
| **E5** | Multi-Timeframe EMA Pullback | 12 |
| **E6** | Z-Score Mean Reversion | 9 |
| **E7** | Volatility Squeeze Breakout | 9 |
| **E8** | VWAP + Swing Structure | 9 |
| **E9** | Consecutive Red Candles + Volume | 9 |
| **E10** | Pure Price Drop | 12 |
| **E11** | QFL Base Bounce | 9 |
| **E12** | Support/Resistance Reclaim | 9 |
| **E13** | EMA Cross + RSI | 10 |
| **E14** | StochRSI Oversold + Trend | 9 |
| **E15** | OBV Divergence + RSI | 9 |
| **E16** | RSI Divergence | 9 |
| **E17** | Liquidity Sweep | 9 |
| **E18** | High ADX Trend Pullback | 9 |
| **E18b** | Low ADX Range Bounce | 9 |
| **E19** | Fibonacci Retracement | 9 |
| **E20** | VPOC Volume Profile | 9 |
| **E21** | Fair Value Gap | 9 |
| **E22** | Candlestick Patterns | 9 |
| **E23** | Relative Strength vs BTC | 9 |
| **E24** | RSI + SMA Pullback | 9 |
| **E25** | Supertrend + RSI | 9 |
| **E26** | Ichimoku Cloud | 9 |
| **E27** | MACD Histogram Reversal | 5 |
| **E28** | Keltner Channel Mean Reversion | 5 |
| **E29** | Donchian Breakout Pullback | 5 |
| **E30** | Hurst Exponent Mean Reversion | 5 |
| **E31** | Kalman Filter Deviation | 5 |
| **E32** | Session Killzone Sweep | 5 |
| **E33** | Williams %R Reversal | 5 |
| **E34** | Choppiness Index Exhaustion | 5 |
| **E35** | Fisher Transform Reversal | 5 |
| **E36** | ALMA Deviation Entry | 5 |
| **E37** | BTC Regime Filter | 5 |
| **E38** | Relative Volume Breakout | 5 |
| **E39** | MFI Oversold Bounce | 5 |
| **E40** | Wick Capitulation | 5 |
| **E41** | TTM Squeeze Fakeout | 5 |
| **E42** | Chaikin Money Flow Divergence | 5 |
| **E43** | QQE Momentum | 5 |
| **E44** | Multi-Signal Score Bot | 5 |
| **E45** | Ensemble Best Methods | 5 |
| **E46** | CVD Approximation | 5 |
| **E47** | ATR Expansion Breakout | 5 |
| **E48** | Volume Before Price (Pump) | 5 |
| **E49** | Relative Strength Explosion (Pump) | 5 |
| **E50** | Compression Breakout (Pump) | 5 |
| **E51** | Top Gainers Pullback (Pump) | 5 |
| **E52** | Wyckoff Flatline Breakout (Pump) | 5 |
| **E53** | Volatility Expansion Chain (Pump) | 5 |
| **E54** | Failed Breakdown Reversal (Pump) | 5 |
| **E55** | Relative Volume Leaderboard (Pump) | 5 |
| **E56** | Smart Money Footprint (Pump) | 5 |
| **E57** | Consensus Pump Engine (Pump) | 5 |

**Total: 416 bots · 62 methods**

---

## BM_HOLD — Benchmark: Buy and Hold

| Bot | Coin |
|-----|---|
| BM-BTC-Hold | BTC |
| BM-ETH-Hold | ETH |

## BM_RANDOM — Benchmark: Random Entry

| Bot |
|-----|
| BM-RandomEntry |

## BM_SIMPLE — Benchmark: Simple Drop Buy

| Bot | Drop Pct |
|-----|---|
| BM-SimpleDCA | 7.0 |

## BM_STATIC — Benchmark: Fixed Spacing

| Bot | Spacing |
|-----|---|
| BM-StaticSpacing | 1.0 |

## E1 — RSI Oversold + VWAP Drop + ATR Spike + Bounce

| Bot | Atr Mult | Vwap Pct | Bounce Pct | Rsi Threshold |
|-----|---|---|---|---|
| E1-1 | 1.5 | 4.0 | 65 | 25 |
| E1-10 | 1.3 | 3.0 | 65 | 30 |
| E1-11 | 1.5 | 3.0 | 55 | 30 |
| E1-12 | 1.3 | 2.0 | 55 | 35 |
| E1-2 | 1.5 | 4.0 | 65 | 30 |
| E1-3 | 1.5 | 4.0 | 65 | 35 |
| E1-4 | 1.5 | 3.0 | 65 | 25 |
| E1-5 | 1.5 | 3.0 | 65 | 30 |
| E1-6 | 1.5 | 3.0 | 65 | 35 |
| E1-7 | 1.5 | 2.0 | 65 | 25 |
| E1-8 | 1.5 | 2.0 | 65 | 30 |
| E1-9 | 1.5 | 2.0 | 65 | 35 |

## E2 — Bollinger Band Squeeze Breakout

| Bot | Bb Sigma | Vol Mult | Recovery Pct |
|-----|---|---|---|
| E2-1 | 2.0 | 1.5 | 0.5 |
| E2-2 | 2.0 | 2.0 | 0.5 |
| E2-3 | 2.0 | 3.0 | 0.5 |
| E2-4 | 2.5 | 1.5 | 0.5 |
| E2-5 | 2.5 | 2.0 | 0.5 |
| E2-6 | 2.5 | 3.0 | 0.5 |
| E2-7 | 2.0 | 2.0 | 1.0 |
| E2-8 | 2.5 | 2.0 | 1.0 |
| E2-9 | 2.5 | 3.0 | 1.0 |

## E3 — Volume Spike + Narrow Range Candle

| Bot | Vol Mult | Range Atr | Close Upper |
|-----|---|---|---|
| E3-1 | 3.0 | 2.0 | 40 |
| E3-10 | 4.0 | 2.0 | 60 |
| E3-11 | 4.0 | 3.0 | 40 |
| E3-12 | 5.0 | 3.0 | 50 |
| E3-2 | 4.0 | 2.0 | 40 |
| E3-3 | 5.0 | 2.0 | 40 |
| E3-4 | 3.0 | 2.5 | 50 |
| E3-5 | 4.0 | 2.5 | 50 |
| E3-6 | 5.0 | 2.5 | 50 |
| E3-7 | 3.0 | 3.0 | 60 |
| E3-8 | 4.0 | 3.0 | 60 |
| E3-9 | 5.0 | 3.0 | 60 |

## E4 — SMA Pullback Entry

| Bot | Sma Period |
|-----|---|
| E4-1 | 1 |
| E4-2 | 1 |
| E4-3 | 1 |
| E4-4 | 2 |
| E4-5 | 2 |
| E4-6 | 2 |
| E4-7 | 4 |
| E4-8 | 4 |
| E4-9 | 4 |

## E5 — Multi-Timeframe EMA Pullback

| Bot | Macro Ema | Pullback Ema | Rsi Threshold |
|-----|---|---|---|
| E5-1 | 144 | 12 | 35 |
| E5-10 | 168 | 24 | 35 |
| E5-11 | 168 | 24 | 45 |
| E5-12 | 200 | 36 | 40 |
| E5-2 | 144 | 24 | 40 |
| E5-3 | 144 | 36 | 45 |
| E5-4 | 168 | 12 | 35 |
| E5-5 | 168 | 24 | 40 |
| E5-6 | 168 | 36 | 45 |
| E5-7 | 200 | 12 | 35 |
| E5-8 | 200 | 24 | 40 |
| E5-9 | 200 | 36 | 45 |

## E6 — Z-Score Mean Reversion

| Bot | Lookback | Z Trigger |
|-----|---|---|
| E6-1 | 96 | -2.0 |
| E6-2 | 96 | -2.5 |
| E6-3 | 96 | -3.0 |
| E6-4 | 168 | -2.0 |
| E6-5 | 168 | -2.5 |
| E6-6 | 168 | -3.0 |
| E6-7 | 336 | -2.0 |
| E6-8 | 336 | -2.5 |
| E6-9 | 336 | -3.0 |

## E7 — Volatility Squeeze Breakout

| Bot | Vol Mult | Squeeze Hours |
|-----|---|---|
| E7-1 | 1.0 | 8 |
| E7-2 | 1.0 | 12 |
| E7-3 | 1.0 | 24 |
| E7-4 | 1.5 | 8 |
| E7-5 | 1.5 | 12 |
| E7-6 | 1.5 | 24 |
| E7-7 | 2.0 | 8 |
| E7-8 | 2.0 | 12 |
| E7-9 | 2.0 | 24 |

## E8 — VWAP + Swing Structure

| Bot | Vwap Period | Swing Candles |
|-----|---|---|
| E8-1 | 12 | 2 |
| E8-2 | 24 | 2 |
| E8-3 | 48 | 2 |
| E8-4 | 12 | 3 |
| E8-5 | 24 | 3 |
| E8-6 | 48 | 3 |
| E8-7 | 12 | 5 |
| E8-8 | 24 | 5 |
| E8-9 | 48 | 5 |

## E9 — Consecutive Red Candles + Volume

| Bot | Vol Mult | Red Candles |
|-----|---|---|
| E9-1 | 1.0 | 5 |
| E9-2 | 1.0 | 6 |
| E9-3 | 1.0 | 7 |
| E9-4 | 1.5 | 5 |
| E9-5 | 1.5 | 6 |
| E9-6 | 1.5 | 7 |
| E9-7 | 2.0 | 5 |
| E9-8 | 2.0 | 6 |
| E9-9 | 2.0 | 7 |

## E10 — Pure Price Drop

| Bot | Drop Pct | Lookback |
|-----|---|---|
| E10-1 | 3.0 | 12 |
| E10-10 | 15.0 | 24 |
| E10-11 | 5.0 | 48 |
| E10-12 | 10.0 | 48 |
| E10-2 | 5.0 | 12 |
| E10-3 | 7.0 | 12 |
| E10-4 | 10.0 | 12 |
| E10-5 | 15.0 | 12 |
| E10-6 | 3.0 | 24 |
| E10-7 | 5.0 | 24 |
| E10-8 | 7.0 | 24 |
| E10-9 | 10.0 | 24 |

## E11 — QFL Base Bounce

| Bot | Base Break Pct |
|-----|---|
| E11-1 | 2.0 |
| E11-2 | 3.0 |
| E11-3 | 4.0 |
| E11-4 | 5.0 |
| E11-5 | 6.0 |
| E11-6 | 8.0 |
| E11-7 | 10.0 |
| E11-8 | 12.0 |
| E11-9 | 15.0 |

## E12 — Support/Resistance Reclaim

| Bot | Vol Mult | Reclaim Pct | Touch Count |
|-----|---|---|---|
| E12-1 | 1.2 | 0.5 | 2 |
| E12-2 | 1.4 | 1.0 | 2 |
| E12-3 | 1.6 | 1.5 | 3 |
| E12-4 | 1.8 | 2.0 | 3 |
| E12-5 | 2.0 | 2.5 | 4 |
| E12-6 | 2.2 | 3.0 | 4 |
| E12-7 | 2.4 | 3.5 | 5 |
| E12-8 | 2.6 | 4.0 | 5 |
| E12-9 | 3.0 | 5.0 | 6 |

## E13 — EMA Cross + RSI

| Bot | Fast Ema | Slow Ema | Rsi Threshold |
|-----|---|---|---|
| E13-1 | 9 | 21 | 35 |
| E13-10 | 26 | 70 | 53 |
| E13-2 | 10 | 24 | 37 |
| E13-3 | 12 | 26 | 39 |
| E13-4 | 14 | 30 | 41 |
| E13-5 | 16 | 34 | 43 |
| E13-6 | 18 | 40 | 45 |
| E13-7 | 20 | 50 | 47 |
| E13-8 | 22 | 55 | 49 |
| E13-9 | 24 | 60 | 51 |

## E14 — StochRSI Oversold + Trend

| Bot | Trend Ema | Recovery Closes | Stoch Threshold |
|-----|---|---|---|
| E14-1 | 50 | 1 | 10 |
| E14-2 | 55 | 1 | 12 |
| E14-3 | 60 | 1 | 14 |
| E14-4 | 65 | 2 | 16 |
| E14-5 | 70 | 2 | 18 |
| E14-6 | 75 | 2 | 20 |
| E14-7 | 80 | 2 | 22 |
| E14-8 | 90 | 3 | 24 |
| E14-9 | 100 | 3 | 26 |

## E15 — OBV Divergence + RSI

| Bot | Lookback | Rsi Threshold | Price Drop Pct |
|-----|---|---|---|
| E15-1 | 24 | 40 | 3.0 |
| E15-2 | 24 | 45 | 5.0 |
| E15-3 | 24 | 50 | 7.0 |
| E15-4 | 48 | 40 | 3.0 |
| E15-5 | 48 | 45 | 5.0 |
| E15-6 | 48 | 50 | 7.0 |
| E15-7 | 72 | 40 | 5.0 |
| E15-8 | 72 | 45 | 7.0 |
| E15-9 | 72 | 50 | 10.0 |

## E16 — RSI Divergence

| Bot | Lookback | Rsi Threshold |
|-----|---|---|
| E16-1 | 24 | 35 |
| E16-2 | 24 | 40 |
| E16-3 | 24 | 45 |
| E16-4 | 48 | 35 |
| E16-5 | 48 | 40 |
| E16-6 | 48 | 45 |
| E16-7 | 72 | 35 |
| E16-8 | 72 | 40 |
| E16-9 | 72 | 45 |

## E17 — Liquidity Sweep

| Bot | Lookback | Sweep Pct | Close Upper |
|-----|---|---|---|
| E17-1 | 12 | 0.25 | 40 |
| E17-2 | 12 | 0.5 | 50 |
| E17-3 | 12 | 1.0 | 60 |
| E17-4 | 24 | 0.25 | 40 |
| E17-5 | 24 | 0.5 | 50 |
| E17-6 | 24 | 1.0 | 60 |
| E17-7 | 48 | 0.25 | 40 |
| E17-8 | 48 | 0.5 | 50 |
| E17-9 | 48 | 1.0 | 60 |

## E18 — High ADX Trend Pullback

| Bot | Adx Min | Vol Lookback | Rsi Threshold |
|-----|---|---|---|
| E18-1 | 20 | 100 | 35 |
| E18-2 | 20 | 100 | 40 |
| E18-3 | 20 | 100 | 45 |
| E18-4 | 25 | 150 | 35 |
| E18-5 | 25 | 150 | 40 |
| E18-6 | 25 | 150 | 45 |
| E18-7 | 30 | 200 | 35 |
| E18-8 | 30 | 200 | 40 |
| E18-9 | 30 | 200 | 45 |

## E18b — Low ADX Range Bounce

| Bot | Adx Max | Lookback | Rsi Threshold |
|-----|---|---|---|
| E18b-1 | 20 | 14 | 30 |
| E18b-2 | 20 | 14 | 35 |
| E18b-3 | 20 | 14 | 40 |
| E18b-4 | 25 | 14 | 30 |
| E18b-5 | 25 | 14 | 35 |
| E18b-6 | 25 | 14 | 40 |
| E18b-7 | 20 | 24 | 30 |
| E18b-8 | 25 | 24 | 35 |
| E18b-9 | 25 | 24 | 40 |

## E19 — Fibonacci Retracement

| Bot | Lookback | Fib Level |
|-----|---|---|
| E19-1 | 48 | 38.2 |
| E19-2 | 48 | 50.0 |
| E19-3 | 48 | 61.8 |
| E19-4 | 48 | 78.6 |
| E19-5 | 96 | 38.2 |
| E19-6 | 96 | 50.0 |
| E19-7 | 96 | 61.8 |
| E19-8 | 96 | 78.6 |
| E19-9 | 168 | 61.8 |

## E20 — VPOC Volume Profile

| Bot | Buffer Pct | Profile Days | Rsi Threshold |
|-----|---|---|---|
| E20-1 | 0.0 | 30 | 0 |
| E20-2 | 0.0 | 60 | 0 |
| E20-3 | 0.0 | 90 | 0 |
| E20-4 | 0.5 | 30 | 35 |
| E20-5 | 0.5 | 60 | 35 |
| E20-6 | 0.5 | 90 | 35 |
| E20-7 | 1.0 | 60 | 0 |
| E20-8 | 1.0 | 90 | 30 |
| E20-9 | 0.5 | 90 | 40 |

## E21 — Fair Value Gap

| Bot | Vol Mult | Fill Depth |
|-----|---|---|
| E21-1 | 0 | 25 |
| E21-2 | 0 | 50 |
| E21-3 | 1.2 | 100 |
| E21-4 | 0 | 25 |
| E21-5 | 0 | 50 |
| E21-6 | 1.5 | 100 |
| E21-7 | 2.0 | 50 |
| E21-8 | 0 | 50 |
| E21-9 | 1.2 | 100 |

## E22 — Candlestick Patterns

| Bot | Pattern | Wick Ratio | Support Proximity |
|-----|---|---|---|
| E22-1 | hammer | 2.0 | 0.5 |
| E22-2 | hammer | 2.5 | 0.5 |
| E22-3 | hammer | 3.0 | 0.5 |
| E22-4 | hammer | 2.0 | 1.0 |
| E22-5 | hammer | 2.5 | 1.0 |
| E22-6 | hammer | 3.0 | 1.0 |
| E22-7 | engulfing | 0 | 0.5 |
| E22-8 | engulfing | 0 | 1.0 |
| E22-9 | engulfing | 0 | 2.0 |

## E23 — Relative Strength vs BTC

| Bot | Lookback | Rsi Threshold | Min Outperform |
|-----|---|---|---|
| E23-1 | 24 | 40 | 2.0 |
| E23-2 | 24 | 40 | 4.0 |
| E23-3 | 24 | 40 | 6.0 |
| E23-4 | 48 | 45 | 2.0 |
| E23-5 | 48 | 45 | 4.0 |
| E23-6 | 48 | 45 | 6.0 |
| E23-7 | 72 | 50 | 2.0 |
| E23-8 | 72 | 50 | 4.0 |
| E23-9 | 72 | 50 | 6.0 |

## E24 — RSI + SMA Pullback

| Bot | Rsi Threshold | Funding Threshold |
|-----|---|---|
| E24-1 | 35 | -0.05 |
| E24-2 | 35 | -0.1 |
| E24-3 | 35 | -0.15 |
| E24-4 | 40 | -0.05 |
| E24-5 | 40 | -0.1 |
| E24-6 | 40 | -0.15 |
| E24-7 | 35 | -0.05 |
| E24-8 | 35 | -0.1 |
| E24-9 | 40 | -0.15 |

## E25 — Supertrend + RSI

| Bot | Atr Mult | Atr Period | Rsi Threshold |
|-----|---|---|---|
| E25-1 | 2.0 | 10 | 30 |
| E25-2 | 2.5 | 10 | 35 |
| E25-3 | 3.0 | 10 | 40 |
| E25-4 | 2.0 | 14 | 30 |
| E25-5 | 2.5 | 14 | 35 |
| E25-6 | 3.0 | 14 | 40 |
| E25-7 | 2.0 | 20 | 30 |
| E25-8 | 2.5 | 20 | 35 |
| E25-9 | 3.0 | 20 | 40 |

## E26 — Ichimoku Cloud

| Bot | Base | Conversion | Rsi Threshold |
|-----|---|---|---|
| E26-1 | 26 | 9 | 35 |
| E26-2 | 26 | 9 | 40 |
| E26-3 | 26 | 9 | 45 |
| E26-4 | 30 | 12 | 35 |
| E26-5 | 30 | 12 | 40 |
| E26-6 | 30 | 12 | 45 |
| E26-7 | 26 | 9 | 35 |
| E26-8 | 26 | 12 | 35 |
| E26-9 | 30 | 9 | 40 |

## E27 — MACD Histogram Reversal

| Bot | Fast | Mode | Slow | Signal Period |
|-----|---|---|---|---|
| E27-1 | 8 | histogram | 21 | 5 |
| E27-2 | 12 | histogram | 26 | 9 |
| E27-3 | 16 | histogram | 34 | 9 |
| E27-4 | 12 | cross_zero | 26 | 9 |
| E27-5 | 8 | cross_zero | 21 | 5 |

## E28 — Keltner Channel Mean Reversion

| Bot | Rsi Max | Atr Mult | Ema Period |
|-----|---|---|---|
| E28-1 | 35 | 1.5 | 20 |
| E28-2 | 35 | 2.0 | 20 |
| E28-3 | 35 | 2.5 | 20 |
| E28-4 | 40 | 2.0 | 50 |
| E28-5 | 40 | 2.5 | 50 |

## E29 — Donchian Breakout Pullback

| Bot | Rsi Min | Pullback Ema | Breakout High |
|-----|---|---|---|
| E29-1 | 45 | 10 | 20 |
| E29-2 | 45 | 20 | 20 |
| E29-3 | 50 | 20 | 55 |
| E29-4 | 50 | 50 | 55 |
| E29-5 | 55 | 50 | 100 |

## E30 — Hurst Exponent Mean Reversion

| Bot | Drop Pct | Lookback | Hurst Max |
|-----|---|---|---|
| E30-1 | 5.0 | 100 | 0.45 |
| E30-2 | 7.0 | 100 | 0.45 |
| E30-3 | 10.0 | 100 | 0.4 |
| E30-4 | 5.0 | 150 | 0.45 |
| E30-5 | 7.0 | 150 | 0.45 |

## E31 — Kalman Filter Deviation

| Bot | Noise Cov | Deviation Pct |
|-----|---|---|
| E31-1 | 0.01 | 3.0 |
| E31-2 | 0.01 | 5.0 |
| E31-3 | 0.01 | 7.0 |
| E31-4 | 0.05 | 3.0 |
| E31-5 | 0.05 | 5.0 |

## E32 — Session Killzone Sweep

| Bot | Session | Drop Pct | Vol Mult |
|-----|---|---|---|
| E32-1 | asia_london | 3.0 | 1.5 |
| E32-2 | asia_london | 5.0 | 2.0 |
| E32-3 | london_ny | 3.0 | 1.5 |
| E32-4 | london_ny | 5.0 | 2.0 |
| E32-5 | ny_close | 3.0 | 1.5 |

## E33 — Williams %R Reversal

| Bot | Confirmation | Wr Threshold |
|-----|---|---|
| E33-1 | green | -90 |
| E33-2 | rsi | -85 |
| E33-3 | vwap | -80 |
| E33-4 | green | -90 |
| E33-5 | rsi | -85 |

## E34 — Choppiness Index Exhaustion

| Bot | Chop Min | Drop Pct | Lookback |
|-----|---|---|---|
| E34-1 | 61.8 | 3.0 | 14 |
| E34-2 | 61.8 | 5.0 | 14 |
| E34-3 | 68.2 | 5.0 | 14 |
| E34-4 | 61.8 | 7.0 | 21 |
| E34-5 | 68.2 | 10.0 | 21 |

## E35 — Fisher Transform Reversal

| Bot | Period | Trigger |
|-----|---|---|
| E35-1 | 9 | -2.0 |
| E35-2 | 9 | -2.5 |
| E35-3 | 14 | -2.5 |
| E35-4 | 14 | -3.0 |
| E35-5 | 21 | -3.0 |

## E36 — ALMA Deviation Entry

| Bot | Sigma | Offset | Window | Drop Pct |
|-----|---|---|---|---|
| E36-1 | 6.0 | 0.85 | 9 | 2.0 |
| E36-2 | 6.0 | 0.85 | 9 | 3.0 |
| E36-3 | 6.0 | 0.85 | 21 | 5.0 |
| E36-4 | 6.0 | 0.85 | 50 | 7.0 |
| E36-5 | 6.0 | 0.85 | 50 | 10.0 |

## E37 — BTC Regime Filter

| Bot | Filter | Drop Pct |
|-----|---|---|
| E37-1 | ema200 | 5.0 |
| E37-2 | ema100 | 5.0 |
| E37-3 | rsi45 | 3.0 |
| E37-4 | drop3 | 5.0 |
| E37-5 | ema200 | 7.0 |

## E38 — Relative Volume Breakout

| Bot | Rsi Max | Drop Pct | Vol Mult |
|-----|---|---|---|
| E38-1 | 40 | 3.0 | 2.0 |
| E38-2 | 40 | 5.0 | 3.0 |
| E38-3 | 40 | 7.0 | 4.0 |
| E38-4 | 45 | 5.0 | 3.0 |
| E38-5 | 35 | 10.0 | 5.0 |

## E39 — MFI Oversold Bounce

| Bot | Mfi Max | Rsi Max | Vol Mult |
|-----|---|---|---|
| E39-1 | 15 | 35 | 1.0 |
| E39-2 | 20 | 35 | 1.2 |
| E39-3 | 25 | 40 | 1.5 |
| E39-4 | 15 | 40 | 1.5 |
| E39-5 | 20 | 45 | 2.0 |

## E40 — Wick Capitulation

| Bot | Drop Pct | Vol Mult | Wick Ratio |
|-----|---|---|---|
| E40-1 | 3.0 | 1.5 | 2.0 |
| E40-2 | 5.0 | 2.0 | 3.0 |
| E40-3 | 5.0 | 3.0 | 4.0 |
| E40-4 | 7.0 | 1.5 | 3.0 |
| E40-5 | 10.0 | 4.0 | 5.0 |

## E41 — TTM Squeeze Fakeout

| Bot | Kc Mult | Bb Period | Fakeout Pct |
|-----|---|---|---|
| E41-1 | 1.5 | 20 | 2.0 |
| E41-2 | 1.5 | 20 | 3.0 |
| E41-3 | 2.0 | 20 | 5.0 |
| E41-4 | 2.0 | 50 | 5.0 |
| E41-5 | 2.5 | 50 | 7.0 |

## E42 — Chaikin Money Flow Divergence

| Bot | Period | Cmf Min | Drop Pct |
|-----|---|---|---|
| E42-1 | 21 | 0.0 | 5.0 |
| E42-2 | 21 | 0.0 | 7.0 |
| E42-3 | 21 | 0.05 | 10.0 |
| E42-4 | 50 | 0.0 | 10.0 |
| E42-5 | 50 | 0.1 | 15.0 |

## E43 — QQE Momentum

| Bot | Qqe Factor |
|-----|---|
| E43-1 | 4.236 |
| E43-2 | 2.618 |
| E43-3 | 3.0 |
| E43-4 | 5.0 |
| E43-5 | 6.0 |

## E44 — Multi-Signal Score Bot

| Bot | Drop Pct | Min Score |
|-----|---|---|
| E44-1 | 3.0 | 2 |
| E44-2 | 3.0 | 3 |
| E44-3 | 5.0 | 3 |
| E44-4 | 3.0 | 4 |
| E44-5 | 5.0 | 4 |

## E45 — Ensemble Best Methods

| Bot | Mode |
|-----|---|
| E45-1 | any2 |
| E45-2 | any2 |
| E45-3 | all |
| E45-4 | any2 |
| E45-5 | all |

## E46 — CVD Approximation

| Bot | Div Pct | Drop Pct | Lookback |
|-----|---|---|---|
| E46-1 | 2.0 | 5.0 | 24 |
| E46-2 | 3.0 | 7.0 | 24 |
| E46-3 | 4.0 | 10.0 | 24 |
| E46-4 | 2.0 | 5.0 | 48 |
| E46-5 | 3.0 | 7.0 | 48 |

## E47 — ATR Expansion Breakout

| Bot | Atr Mult | Vol Mult |
|-----|---|---|
| E47-1 | 1.2 | 1.2 |
| E47-2 | 1.5 | 1.5 |
| E47-3 | 2.0 | 2.0 |
| E47-4 | 2.5 | 2.0 |
| E47-5 | 3.0 | 3.0 |

## E48 — Volume Before Price (Pump)

| Bot | Vol Mult | Max Price Move |
|-----|---|---|
| E48-1 | 2.0 | 5.0 |
| E48-2 | 3.0 | 3.0 |
| E48-3 | 5.0 | 3.0 |
| E48-4 | 7.0 | 2.0 |
| E48-5 | 10.0 | 2.0 |

## E49 — Relative Strength Explosion (Pump)

| Bot | Lookback | Min Strength |
|-----|---|---|
| E49-1 | 4 | 3.0 |
| E49-2 | 4 | 5.0 |
| E49-3 | 4 | 7.0 |
| E49-4 | 4 | 10.0 |
| E49-5 | 6 | 15.0 |

## E50 — Compression Breakout (Pump)

| Bot | Vol Mult | Compression Days |
|-----|---|---|
| E50-1 | 2.0 | 3 |
| E50-2 | 3.0 | 5 |
| E50-3 | 3.0 | 7 |
| E50-4 | 5.0 | 10 |
| E50-5 | 5.0 | 14 |

## E51 — Top Gainers Pullback (Pump)

| Bot | Pump Pct | Max Pullback | Pullback Pct |
|-----|---|---|---|
| E51-1 | 15.0 | 15.0 | 5.0 |
| E51-2 | 20.0 | 20.0 | 8.0 |
| E51-3 | 25.0 | 20.0 | 8.0 |
| E51-4 | 30.0 | 25.0 | 10.0 |
| E51-5 | 50.0 | 30.0 | 15.0 |

## E52 — Wyckoff Flatline Breakout (Pump)

| Bot | Vol Mult | Max Range Pct | Flatline Hours |
|-----|---|---|---|
| E52-1 | 3.0 | 2.0 | 24 |
| E52-2 | 5.0 | 3.0 | 48 |
| E52-3 | 5.0 | 3.0 | 72 |
| E52-4 | 10.0 | 5.0 | 72 |
| E52-5 | 15.0 | 7.0 | 168 |

## E53 — Volatility Expansion Chain (Pump)

| Bot | Vol Mult | Atr Increase |
|-----|---|---|
| E53-1 | 1.5 | 0.2 |
| E53-2 | 2.0 | 0.4 |
| E53-3 | 2.0 | 0.6 |
| E53-4 | 2.5 | 0.8 |
| E53-5 | 3.0 | 1.0 |

## E54 — Failed Breakdown Reversal (Pump)

| Bot | Reclaim Pct | Breakdown Pct |
|-----|---|---|
| E54-1 | 0.5 | 2.0 |
| E54-2 | 0.5 | 3.0 |
| E54-3 | 1.0 | 5.0 |
| E54-4 | 1.0 | 7.0 |
| E54-5 | 1.5 | 10.0 |

## E55 — Relative Volume Leaderboard (Pump)

| Bot | Rsi Max | Rsi Min | Min Vol Mult |
|-----|---|---|---|
| E55-1 | 70 | 40 | 3.0 |
| E55-2 | 70 | 40 | 5.0 |
| E55-3 | 65 | 45 | 7.0 |
| E55-4 | 65 | 45 | 10.0 |
| E55-5 | 70 | 50 | 15.0 |

## E56 — Smart Money Footprint (Pump)

| Bot | Lookback | Vol Mult | Max Price Move |
|-----|---|---|---|
| E56-1 | 8 | 1.5 | 3.0 |
| E56-2 | 10 | 2.0 | 2.0 |
| E56-3 | 12 | 3.0 | 2.0 |
| E56-4 | 16 | 3.0 | 1.5 |
| E56-5 | 20 | 4.0 | 1.0 |

## E57 — Consensus Pump Engine (Pump)

| Bot | Min Votes |
|-----|---|
| E57-1 | 3 |
| E57-2 | 4 |
| E57-3 | 5 |
| E57-4 | 6 |
| E57-5 | 7 |

