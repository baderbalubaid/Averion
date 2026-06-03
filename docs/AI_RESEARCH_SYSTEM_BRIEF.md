# Averion Research System — Complete Brief for AI Review

## Context
Averion is a public automated crypto DCA trading platform.
144 paper research bots run simultaneously testing 14 entry methods.
Goal: Find best entry method per market regime automatically.

---

## 1. Research Bot Structure

### 14 Entry Methods
| Method | Name | Variations |
|--------|------|-----------|
| E1 | VWAP + RSI Deviation | 12 |
| E2 | Panic Exhaustion | 9 |
| E3 | Volume Climax | 12 |
| E4 | Time-Cycle Window | 9 |
| E5 | Multi-Timeframe | 12 |
| E6 | Z-Score Statistical | 9 |
| E7 | Volatility Squeeze | 9 |
| E8 | Swing Structure Shift | 9 |
| E9 | Sequential Candle Decay | 9 |
| E10 | Pure Drop Threshold (control) | 12 |
| E11 | QFL Base Bounce | 9 |
| E12 | Support/Resistance Reclaim | 9 |
| E13 | EMA + MACD + RSI Confluence | 10 |
| E14 | Stoch RSI Pullback + Trend | 9 |

### 5 Benchmarks (comparison only · never promoted)
- BTC Buy and Hold
- ETH Buy and Hold
- Simple DCA ASAP
- Random Entry DCA
- Static Spacing DCA

### Total: 144 bots (139 method + 5 benchmark)

---

## 2. Coin Universe (LOCKED)
- Top 500 coins by market cap (CoinGecko daily)
- Must be available on MEXC or KuCoin
- 24h volume > $100,000
- New coins excluded (high risk)
- Result: ~200-300 tradeable coins

---

## 3. Trade Scaling Plan
| Week | Trades Per Bot | Total | Action |
|------|---------------|-------|--------|
| 1 | 1 | 144 | Baseline |
| 2 | 10 | 1,440 | First data |
| 3 | 20 | 2,880 | Load test |
| 4 | 30 | 4,320 | Server check |
| Month 2 | 50 | 7,200 | Full capacity |

Plus 144 Short bots × 5 coins = 720 after Long stable.

Server thresholds:
- Green: loop < 30s
- Yellow: 30-50s
- Red: > 50s · upgrade to CX33

---

## 4. Market Regime Detection (LOCKED)

4 signals scored daily at 04:30:

| Signal | Bull +1 | Bear -1 |
|--------|---------|---------|
| BTC 7d change | > +5% | < -5% |
| Fear & Greed | > 65 | < 35 |
| BTC dominance | Falling | Rising |
| Market cap 30d | > +10% | < -10% |

Score +3/+4 = Strong Bull
Score 0 = Sideways
Score -3/-4 = Strong Bear

Source: api.alternative.me/fng/ (free · daily)

---

## 5. Data Collected Per Trade
Every research trade records:
- method · variation · coin · exchange
- entry_price · exit_price
- profit_pct · profit_usdt
- dca_count (DCAs before TP)
- days_open (time in trade)
- max_drawdown_pct
- regime at entry (bull/bear/sideways)
- entry_signal_data JSONB (raw indicator values)
- is_research = TRUE

---

## 6. Scoring Formula — RARS

### 5 Dimensions:

Dimension 1 — Win Rate
win_rate = wins / total_closed_trades

Dimension 2 — Average Profit per Win
avg_profit = sum(winning profits) / win_count

Dimension 3 — Max Drawdown Control
max_dd = maximum drawdown across all trades
(lower = better)

Dimension 4 — Capital Efficiency (KEY DIMENSION)
cap_efficiency = avg_profit / (avg_dca_count × avg_days_open)

Example:
Method A: 5% profit · 2 DCAs · 8 days = 5/(2×8) = 0.313
Method B: 5% profit · 6 DCAs · 30 days = 5/(6×30) = 0.028
Method A is 11× more efficient

Dimension 5 — Recovery Speed
recovery = 1 / avg_days_open

### Final Score:
RARS = (win_rate × avg_profit × cap_efficiency) / max(max_dd, 0.01)

### Calculated separately per regime:
- Bull RARS (trades where regime = bull)
- Bear RARS (trades where regime = bear)
- Sideways RARS (trades where regime = sideways)

---

## 7. Three Regime Champions (LOCKED)

One champion per regime:
- Smart DCA Bull Champion
- Smart DCA Bear Champion
- Smart DCA Sideways Champion

System auto-switches based on daily regime.
New positions always use current regime champion.
Existing positions never affected (keep original params).

### Champion Switch Rules:
1. Challenger beats champion 4 consecutive weeks
2. In CURRENT regime specifically
3. Minimum 100 trades
4. Auto-switch if toggle ON · alert if toggle OFF
5. Always notify Bader via Telegram

### Switch in code = update ONE DB row:
UPDATE smart_dca_champions
SET method = new_method
WHERE regime = 'bull'

No code change · no restart · instant effect.

---

## 8. Auto-Switch Toggle (LOCKED)

Admin dashboard toggle:
[Auto Switch: ON/OFF]

ON: 4 weeks confirmed → auto-switch → notify
OFF: 4 weeks confirmed → alert → wait approval

Either way: Bader always notified · can always revert.
Periodic AI review when champion changes or monthly.

---

## 9. Never Delete Policy (LOCKED)

- All 14 methods run forever
- Poor performers → Monitor tier (not deleted)
- Reason: bear market loser = bull market winner
- Only zero-trade bots replaced (signal too strict)
- Data kept forever (< 5MB per year)

---

## 10. Weekly Report Format (LOCKED)

Generated Sunday 05:00 · pushed to GitHub · markdown download.

Structure:
- Current champions (Bull · Bear · Sideways)
- Challengers in confirmation (week X of 4)
- Full ranking table all 14 methods
- Per method: open positions with full details
- Per method: closed trades this week
- Per method: performance summary
- Benchmark comparison table
- Regime analysis (best method per regime)
- Server health stats
- Alerts (zero-trade bots · declining methods)

Open position detail shows:
- Coin · opened date · days open
- Entry price · current price
- DCA count · current P&L
- Max drawdown so far

Closed trade detail shows:
- Coin · entry · exit · days · DCAs · profit% · regime

---

## 11. Promotion Eligibility (LOCKED)

| Trades | Status |
|--------|--------|
| < 30 | Provisional · track only |
| 30-99 | Developing · score calculated |
| 100+ | Eligible for promotion |
| 0 in 30 days | Replace with looser variation |

Requirements for promotion:
- 100+ closed trades
- Tested in 3+ market regimes
- RARS beats E10 control group
- RARS beats Simple DCA benchmark
- 30-day cooldown after parameter change

---

## 12. generate_metrics.py Weekly Flow

Every Sunday 05:00:
1. Read all closed research trades from DB
2. Calculate RARS per method per regime
3. Check challengers (weeks ahead)
4. Auto-switch if 4 weeks confirmed + toggle ON
5. Generate full markdown report
6. Push report to GitHub
7. Send Telegram: report ready + champion status

---

## 13. Locked Decisions Summary

| Topic | Decision |
|-------|----------|
| Champions | 3 (Bull · Bear · Sideways) |
| Confirmation | 4 consecutive weeks |
| Auto-switch | Toggleable ON/OFF |
| Deletion | Never |
| Coins | Top 500 market cap · liquid |
| Trade scaling | 1→10→20→30→50 per bot |
| Report | Weekly Sunday · markdown |
| Data retention | Forever |
| Minimum trades | 30 provisional · 100 eligible |
| Regime source | 4 signals majority vote |

---

## 14. Questions for AI Review

1. Is RARS the right metric for DCA systems?
   Better alternatives: Sharpe ratio · Sortino · Profit Factor?

2. Are 5 dimensions correct and complete?
   Missing any important dimension?

3. Capital efficiency formula correct?
   profit / (dca_count × days) — better formula?

4. Is 4-week confirmation right?
   Too long · too short · should vary by regime?

5. Score per variation (E11-3) or per method (E11 average)?

6. Top 500 market cap filter — right threshold?
   Should volume filter be different?

7. What if ALL methods lose to benchmarks?
   Auto-switch to Simple DCA or alert human?

8. How to handle short research differently from long?
   Same scoring formula or different?

9. Low-frequency methods (E4 max 3 signals/week)
   Should they be penalized or just wait for 100 trades?

10. Any regime detection signals we are missing?
    Better than our 4-signal approach?
