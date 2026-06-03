# Averion Research System Brief V3
## Final Version - All Decisions Locked

---

## 1. Purpose

Averion runs 144 paper research bots testing 14 entry methods.
Goal: Automatically find best entry method per market regime.
No human reading data needed - system decides automatically.

---

## 2. Entry Methods (14 total)

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

Method bots: 139
Benchmarks: 5 (BTC Hold, ETH Hold, Simple DCA, Random Entry, Static Spacing)
Total: 144 bots

Short research: 144 bots x 5 coins (BTC, ETH + 3 liquid alts) = 720 short trades

---

## 3. Coin Universe (LOCKED)

- Top 500 coins by market cap (CoinGecko daily)
- Available on MEXC or KuCoin
- 24h volume >= $1,000,000
- 90+ days OHLCV data
- Result: 200-300 tradeable coins

---

## 4. Trade Scaling Plan

| Week | Trades/Bot | Long | Short |
|------|-----------|------|-------|
| 1 | 1 | 144 | 0 |
| 2 | 10 | 1,440 | 0 |
| 3 | 20 | 2,880 | 0 |
| 4 | 30 | 4,320 | 720 |
| Month 2 | 50 | 7,200 | 720 |

Server: Green <30s, Yellow 30-50s, Red >50s upgrade CX33

---

## 5. Market Regime Detection (LOCKED V3)

5 signals scored daily at 04:30.
Fear and Greed REMOVED (lagging indicator).
BTC signals capped at combined max 2 pts (correlated).

| Signal | Bull | Bear | Weight |
|--------|------|------|--------|
| BTC 7d change | >+5% = +2 | <-5% = -2 | 2 pts |
| Realized Vol 30d | <30% = +2 | >80% = -2 | 2 pts |
| Market cap 30d | >+10% = +1 | <-10% = -1 | 1 pt |
| BTC 200D MA | Above = +1 | Below = -1 | 1 pt |
| Altcoin Season | >75% = +1 | <25% = -1 | 1 pt |

BTC cap rule: btc_combined = min(2, max(-2, btc_7d + btc_200d))

Scale: -7 to +7
Strong Bull: >= +5
Bull: +2 to +4
Sideways: -1 to +1
Bear: -2 to -4
Strong Bear: <= -5

Sources (all from existing data):
- BTC 7d: ohlcv_hourly table
- Realized Vol: STDDEV(daily_returns_30d) x SQRT(365) from ohlcv_hourly
- Market cap 30d: coin_history table
- BTC 200D MA: ohlcv_hourly table
- Altcoin Season: % of top 50 alts beating BTC (from ohlcv_hourly, midnight snapshot)

---

## 6. Data Collected Per Trade

Every research trade records:
- method, variation, coin, exchange
- entry_price, exit_price
- profit_pct, profit_usdt
- dca_count, days_open
- max_drawdown_pct
- max_usdt_deployed (PEAK capital = entry + all DCAs fired)
- regime at entry (bull/bear/sideways, NEVER changes)
- entry_signal_data JSONB
- is_research = TRUE
- direction (long/short)

---

## 7. RARS Scoring Formula V3 (LOCKED)

### Weighted Additive (not multiplicative)
One weak dimension does not destroy total score.

### Weights: 35 / 30 / 20 / 15 / 0

Dimension 1: Capital Efficiency (35%)
cap_eff = avg_profit_usdt / (avg_max_usdt_deployed x max(avg_days_open, 1))
avg_max_usdt_deployed = PEAK capital deployed during trade lifetime
Measures: profit per dollar deployed per day

Dimension 2: Drawdown Control (30%)
drawdown_ctrl = 1 - ((max_dd + 0.005) / 100)
Use max_dd + 0.005 NOT max(max_dd, 0.01)
Reason: prevents two different drawdowns scoring identically

Dimension 3: Win Rate (20%)
win_rate = winning_trades / total_closed_trades

Dimension 4: Profit Factor (15%)
profit_factor = gross_profit / max(gross_loss, 0.01)
Capped at 10.0 then normalized: pf_norm = min(pf, 10) / 10
Reason: catches methods with big losses hiding behind high win rate

Dimension 5: Consistency (HARD GATE - not scored)
consistency = std_dev(profit_pct) / max(avg_profit_pct, 0.1)
If consistency > 0.70 (std_dev > 70% of avg_profit):
   data_sparse = TRUE, not eligible for promotion
Reason: cleaner than 5% weight, removes double-counting with Profit Factor

### Normalization (before applying weights):
Step 1: Winsorize at 5th/95th percentile
   Prevents catastrophic outlier compressing all other scores
Step 2: Normalize 0-1
   norm = (value - min) / (max - min)
   min/max calculated across ALL methods in same regime

### Final RARS:
RARS = (0.35 x cap_eff_norm) +
      (0.30 x drawdown_norm) +
      (0.20 x win_rate) +
      (0.15 x profit_factor_norm)

### Per regime separately:
- RARS_bull: only trades where regime_at_entry = bull
- RARS_bear: only trades where regime_at_entry = bear
- RARS_sideways: only sideways trades
- RARS_overall: informational only

### Scoring level:
- Score per VARIATION (E11-3 separately from E11-7)
- Promote per METHOD (median of all variations)
- Deploy best VARIATION within winning method

### Median not mean:
Use MEDIAN across all coins per method.
Prevents one lucky coin skewing entire method score.

---

## 8. Short RARS Formula (Separate, LOCKED)

Never mix Long and Short RARS in same ranking.
Direction tag in research_scores.

Short DCA profits from momentum (price rises then drops).
Long DCA profits from mean reversion.

Short RARS weights:
| Dimension | Weight |
|-----------|--------|
| Drawdown Control (max adverse move) | 35% |
| Win Rate | 25% |
| Capital Efficiency (profit/coin_value x days) | 20% |
| Buyback Success Rate (positions closed via TP / total) | 15% |
| Profit Factor | 5% |

Buyback success = positions closed via TP / total closed short positions
NOT orders filled / orders placed (intermediate cancels = noise)

---

## 9. Three Champions System (LOCKED)

One champion per regime:
- Bull Champion
- Bear Champion
- Sideways Champion

Starting champion all 3 regimes: E10 (control group)
Everything must beat E10 to be promoted.

How bot uses champion:
Every 60s cycle reads today regime from market_regimes table.
Looks up champion for that regime from smart_dca_champions table.
All NEW positions use that method signal.
EXISTING positions never affected (keep original params).

Champion change = update one DB row, instant, no restart needed.

---

## 10. Promotion Eligibility (LOCKED)

ALL of these required before any promotion considered:
- 100 total closed trades
- 30 trades in TARGET REGIME specifically
- Tested in 3+ different regimes
- 30-day cooldown after any parameter change
- Consistency gate passed (std_dev not too high)
- data_sparse = FALSE

30 regime trades rationale:
Statistical significance for binary outcome at 95% confidence
requires ~30 samples to detect 15% difference in win rates.
Matches our 15% promotion margin mathematically.

---

## 11. Three-Tier Promotion System (LOCKED)

IMPORTANT: Tiers evaluated in order. Tier 2 only if Tier 1 fails. Tier 3 only if both fail.

### Tier 1 (preferred):
- 4 consecutive weeks beating champion
- In CURRENT regime throughout (resets if regime changes)
- challenger RARS >= champion_rars_at_challenge_start x 1.15
- 20+ trades in those 4 weeks
- champion_rars_at_challenge_start LOCKED when challenger first detected
 (prevents moving target - champion improvement cannot block promotion)

### Tier 2 (only if Tier 1 never confirmed):
- 6 wins out of any rolling 8 consecutive weeks
- Same 15% margin above locked champion RARS
- 30+ trades in those 8 weeks
- PAUSE (not reset) if regime changes mid-window

### Tier 3 (only if Tier 1 AND Tier 2 both failed after 6 months):
- Full 6 months completed
- Highest RARS overall AND beats E10 by 15%
- Must have 30 regime-specific trades
- Must be best method overall (not just better than E10)
- Always produces a winner if eligible

### If nobody beats E10 at all:
- Telegram alert to Bader
- no_alpha_detected = TRUE in smart_dca_champions
- Keep E10 as champion
- Do NOT auto-switch to Simple DCA
- Human reviews data

### Tier 1 vs Tier 2 regime behavior:
Tier 1: RESETS on regime change (needs 4 consecutive in SAME regime)
Tier 2: PAUSES on regime change (rolling window keeps evidence, resumes when regime returns)

---

## 12. Bear Market Rules (LOCKED)

### Normal bear confirmation: 2 weeks
Bear markets move fast. 4 weeks too slow for capital protection.
Bull and Sideways = 4 weeks.

### Bear circuit breaker (emergency only):
If current bear champion max_drawdown > 30% in last 30 days:
- Switch IMMEDIATELY to lowest-drawdown challenger with 20+ trades
- No waiting for confirmation weeks
- Telegram alert: EMERGENCY SWITCH
- Bader can revert manually at any time
- This only changes WHICH METHOD signals entries
- Does NOT affect: DCA spacing, TP%, coin selection, trade size

Why 30% threshold (not 25%):
25% can happen in normal bear market volatility.
30% = method genuinely failing, not just market noise.

---

## 13. Auto-Switch System (LOCKED)

Admin dashboard toggle: [Auto Switch: ON/OFF]

When ON:
- Confirmation achieved -> switch immediately -> notify Bader

When OFF:
- Confirmation achieved -> alert Bader -> wait approval

ALWAYS notify Bader regardless of toggle setting:
"Champion switched: Bull E10-1 -> E11-3
RARS: 0.745 vs 0.621 (+20% above threshold)
Confirmed: 4 weeks, 47 trades
[View Report] [Revert if needed]"

Manual override always available.
Revert to previous champion with one click.

---

## 14. Never Delete Policy (LOCKED)

All 14 methods run forever.
Poor performers -> Monitor tier only (never deleted).
Reason: bear loser = next bull winner on regime flip.
Only replacement: zero-trade bots (signal never triggers in 30 days).
Replace with: looser variation of same method.
All data kept forever (less than 5MB per year).

---

## 15. Confidence Tiers (Metadata Only, Not in RARS)

Shown in report and dashboard for context.
Does NOT affect scoring or promotion.

| Tier | Trades |
|------|--------|
| Bronze | 100-499 |
| Silver | 500-999 |
| Gold | 1000-4999 |
| Platinum | 5000+ |

Prevents misreading RARS 0.85 with 102 trades
as equal to RARS 0.83 with 8,400 trades.

---

## 16. Weekly Report Structure (LOCKED)

Generated Sunday 05:00, pushed to GitHub, markdown download.
URL: github.com/baderbalubaid/Averion/main/research/

Sections:
1. Current champions (Bull, Bear, Sideways)
2. Challengers in confirmation (Tier, Week X of 4)
3. BULL LEADERBOARD (only bull-regime trades)
4. BEAR LEADERBOARD (only bear-regime trades)
5. SIDEWAYS LEADERBOARD (only sideways trades)
6. Benchmark comparison
7. Regime this week + signal breakdown
8. Server health
9. Alerts

Per method per leaderboard:
Open positions:
- Coin, opened date, days open, entry, current price, DCAs, PnL%, max DD so far

Closed trades this week:
- Coin, entry, exit, days, DCAs, USDT deployed, profit%, regime tag

Performance summary:
- Win rate, avg profit, avg loss, profit factor
- Max drawdown, avg DCAs, avg days, avg USDT deployed
- Capital efficiency, RARS per regime
- vs E10, vs Random Entry, vs BTC Hold
- Confidence tier, data_sparse flag, consistency gate result

---

## 17. Database Schema Required

New tables needed before research starts:

CREATE TABLE smart_dca_champions (
   id SERIAL PRIMARY KEY,
   regime VARCHAR(20) NOT NULL UNIQUE,
   method VARCHAR(20) NOT NULL DEFAULT 'E10',
   best_variation VARCHAR(20) DEFAULT 'E10-1',
   rars_score DECIMAL(10,6) DEFAULT 0,
   confirmed_at TIMESTAMP,
   confirmation_weeks INTEGER DEFAULT 0,
   challenger_method VARCHAR(20),
   challenger_variation VARCHAR(20),
   challenger_weeks INTEGER DEFAULT 0,
   challenger_rars DECIMAL(10,6),
   champion_rars_at_challenge_start DECIMAL(10,6),
   auto_switch BOOLEAN DEFAULT TRUE,
   switched_at TIMESTAMP,
   previous_method VARCHAR(20),
   no_alpha_detected BOOLEAN DEFAULT FALSE,
   fallback_to_random BOOLEAN DEFAULT FALSE,
   circuit_breaker_fired BOOLEAN DEFAULT FALSE,
   created_at TIMESTAMP DEFAULT NOW(),
   updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO smart_dca_champions (regime, method, best_variation)
VALUES ('bull','E10','E10-1'),
      ('bear','E10','E10-1'),
      ('sideways','E10','E10-1')
ON CONFLICT (regime) DO NOTHING;

CREATE TABLE champion_challengers (
   id SERIAL PRIMARY KEY,
   regime VARCHAR(20) NOT NULL,
   method VARCHAR(20) NOT NULL,
   best_variation VARCHAR(20),
   tier INTEGER DEFAULT 1,
   weeks_confirmed INTEGER DEFAULT 0,
   weeks_total INTEGER DEFAULT 0,
   trades_in_window INTEGER DEFAULT 0,
   challenger_rars DECIMAL(10,6),
   champion_rars_locked DECIMAL(10,6),
   pct_above_champion DECIMAL(10,4),
   window_start_date TIMESTAMP DEFAULT NOW(),
   paused BOOLEAN DEFAULT FALSE,
   first_detected TIMESTAMP DEFAULT NOW(),
   last_confirmed TIMESTAMP DEFAULT NOW(),
   reset_count INTEGER DEFAULT 0
);

research_scores additions:
ALTER TABLE research_scores
ADD COLUMN IF NOT EXISTS direction VARCHAR(10) DEFAULT 'long',
ADD COLUMN IF NOT EXISTS gross_profit DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS gross_loss DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS profit_factor DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS consistency_gate_passed BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS avg_dca_count DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS avg_days_open DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS avg_usdt_deployed DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS p90_usdt_deployed DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS cap_efficiency DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_bull DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_bear DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_sideways DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_overall DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS data_sparse BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS confidence_tier VARCHAR(10) DEFAULT 'bronze',
ADD COLUMN IF NOT EXISTS regime_trade_counts JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS buyback_success_rate DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS inventory_locked_days DECIMAL(10,2);

---

## 18. generate_metrics.py Flow (LOCKED)

Runs every Sunday 05:00 automatically. Zero human action needed.

Step 1: Read all closed research trades from DB
Step 2: Separate by direction (long/short) and regime (bull/bear/sideways)
Step 3: For each regime, for each variation:
       - Skip if trades < 30 (mark data_sparse=TRUE)
       - Check consistency gate (std_dev/avg_profit < 0.70)
       - Calculate 4 raw dimensions
Step 4: Winsorize all dimension values at 5th/95th percentile
Step 5: Normalize each dimension 0-1 across ALL variations
Step 6: Calculate RARS = 0.35*cap + 0.30*dd + 0.20*wr + 0.15*pf
Step 7: Use MEDIAN across coins (not mean)
Step 8: Aggregate to method level (median of variations)
       Identify best variation per method
Step 9: Check eligibility (100 total, 30 regime, consistency gate)
Step 10: Check promotion tiers:
        Tier 1: 4 consecutive? (ONLY if not already confirmed)
        Tier 2: 6 of 8 rolling? (ONLY if Tier 1 failed)
        Tier 3: 6 months + best RARS? (ONLY if Tier 1+2 both failed)
Step 11: Check bear circuit breaker (max_dd > 30%)
Step 12: Execute champion switch if confirmed
        auto_switch ON: switch + notify
        auto_switch OFF: alert + wait
Step 13: Save all scores to research_scores table
Step 14: Generate 3 separate leaderboards (Bull/Bear/Sideways)
Step 15: Generate full markdown report
Step 16: Push report to GitHub
Step 17: Telegram notification with champion status and download URL

Zero trades in a week: counter unchanged (no win, no loss, no reset)

---

## 19. All Locked Decisions

| Decision | Rule |
|----------|------|
| Champions | 3 (Bull, Bear, Sideways) |
| Starting champion | E10 control group |
| Regime tag | At entry, never changes |
| Signals | 5 signals (Fear+Greed removed) |
| Signal scale | -7 to +7 |
| BTC cap | Combined BTC signals max +/-2 |
| RARS | Weighted additive |
| Weights | 35/30/20/15 (no consistency weight) |
| Consistency | Hard gate (std_dev < 70% of avg_profit) |
| Winsorize | 5th/95th percentile before normalize |
| Normalization | 0-1 per dimension across all methods |
| Scoring | Per variation, promote per method |
| Champion locked RARS | Locked at challenge start |
| Promotion margin | 15% above locked champion RARS |
| Tier 1 | 4 consecutive weeks, 20 trades |
| Tier 2 | 6 of 8 rolling weeks, 30 trades (Tier 1 must fail first) |
| Tier 3 | 6 months, best RARS, beats E10 (Tier 1+2 must fail) |
| Tier 1 on regime flip | RESET |
| Tier 2 on regime flip | PAUSE |
| Bear confirmation | 2 weeks |
| Bear circuit breaker | 30% drawdown -> emergency switch |
| Auto-switch | Toggleable, always notify |
| Deletion | Never |
| Coins | Top 500, $1M volume, 90d data |
| Short RARS | Separate formula, Drawdown 35% first |
| Report | Weekly Sunday, markdown, GitHub |
| Data retention | Forever |
| All lose | Alert Bader, keep E10 |
| Zero trades week | Counter unchanged |
| Confidence tiers | Metadata only, not in RARS |
| Regime trades min | 30 in target regime |

---

## 20. Questions for AI Review V3

1. Is RARS V3 (35/30/20/15) correct for DCA platform?
  Is removing Consistency Score as weighted dimension correct?

2. Is capital efficiency formula final?
  profit_usdt / (avg_max_usdt_deployed x max(avg_days_open, 1))

3. Is removing Fear & Greed correct?
  Are 5 signals sufficient?

4. Is BTC signal cap at +/-2 combined correct?

5. Is 3-tier system complete after V3 fixes?
  Tier 1 only, Tier 2 only if Tier 1 fails, Tier 3 last resort?

6. Is bear circuit breaker at 30% correct?
  Right threshold? Any edge cases?

7. Is Tier 1 RESET and Tier 2 PAUSE correct behavior on regime flip?

8. Is Short RARS with Drawdown 35% correct?
  Is buyback definition (closed via TP / total) correct?

9. Is consistency hard gate at 70% the right threshold?

10. Any remaining flaw that could produce wrong champion
   after 6 months of data collection?
