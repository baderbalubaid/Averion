# Averion Research System — Final Brief
## All Decisions Locked · Ready to Code

---

## 1. Purpose

Averion runs 144 paper research bots testing 14 entry methods simultaneously.
Goal: Automatically find best entry method per market regime.
System decides automatically — no human reading data needed.
Platform self-improves forever.

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
- 90+ days OHLCV data (excludes new coins)
- Result: 200-300 tradeable coins
- List refreshes daily automatically

---

## 4. Trade Scaling Plan

| Week | Trades/Bot | Long | Short |
|------|-----------|------|-------|
| 1 | 1 | 144 | 0 |
| 2 | 10 | 1,440 | 0 |
| 3 | 20 | 2,880 | 0 |
| 4 | 30 | 4,320 | 720 |
| Month 2 | 50 | 7,200 | 720 |

Server thresholds:
- Green: loop < 30s, proceed
- Yellow: 30-50s, investigate
- Red: > 50s, upgrade to CX33

---

## 5. Market Regime Detection (LOCKED)

5 signals scored daily at 04:30.
Fear and Greed removed (lagging, adds noise).
BTC signals capped at combined max 2 pts (correlated).

| Signal | Bull | Bear | Points |
|--------|------|------|--------|
| BTC 7d change | >+5% = +2 | <-5% = -2 | 2 |
| Realized Vol 30d | <30% = +2 | >80% = -2 | 2 |
| Market cap 30d | >+10% = +1 | <-10% = -1 | 1 |
| BTC 200D MA | Above = +1 | Below = -1 | 1 |
| Altcoin Season | >75% = +1 | <25% = -1 | 1 |

BTC cap: btc_combined = min(2, max(-2, btc_7d + btc_200d))

Scale: -6 to +6 (not 7, BTC cap makes 7 unreachable)
- Strong Bull: >= +4
- Bull: +2 to +3
- Sideways: -1 to +1
- Bear: -2 to -3
- Strong Bear: <= -4

Realized Vol formula (log returns, not simple):
daily_log_returns = ln(close[t] / close[t-1]) for last 30 days
realized_vol = stdev(daily_log_returns) x sqrt(365) x 100

Sources (all from existing collected data):
- BTC 7d: ohlcv_hourly table
- Realized Vol: calculated from ohlcv_hourly
- Market cap 30d: coin_history table
- BTC 200D MA: ohlcv_hourly table
- Altcoin Season: % top 50 alts beating BTC (midnight UTC snapshot from coin_history)

---

## 6. Data Collected Per Trade

Every research trade records:
- method (E1-E14), variation (E11-3 etc)
- coin, exchange
- entry_price, exit_price
- profit_pct, profit_usdt
- dca_count (DCAs before TP)
- days_open
- max_drawdown_pct
- max_usdt_deployed (PEAK capital = entry + all DCAs that fired)
- regime at entry (bull/bear/sideways, NEVER changes after entry)
- entry_signal_data JSONB
- is_research = TRUE
- direction (long/short)
- regime_changed_during_trade BOOLEAN (dashboard only, not in RARS)

---

## 7. RARS Scoring Formula (LOCKED)

### Weighted Additive (not multiplicative)
One weak dimension does not destroy total score.
Weights sum to 100%.

### 4 Dimensions and Weights:

Dimension 1: Capital Efficiency (35%)
cap_efficiency = avg_profit_usdt / (avg_max_usdt_deployed x max(avg_days_open, 1))
avg_max_usdt_deployed = PEAK capital deployed (entry + all DCAs actually fired)
Measures: profit per dollar deployed per day
Note: Use avg not p90 for V1 (fairer, less strict, p90 = V2 improvement)

Dimension 2: Drawdown Control (30%)
drawdown_ctrl = 1 - ((max_dd + 0.005) / 100)
Use max_dd + 0.005 in denominator (not hard floor at 0.01)
Reason: prevents two different drawdowns scoring identically

Dimension 3: Win Rate (20%)
win_rate = winning_trades / total_closed_trades

Dimension 4: Profit Factor (15%)
profit_factor = gross_profit / max(gross_loss, 0.01)
Capped at 10.0, normalized: pf_norm = min(pf, 10) / 10
Reason: catches methods with big losses hiding behind win rate

### Consistency Gate (not scored, gate only):
Applied ONLY after 100 trades (not before - too noisy early)
consistency = std_dev(profit_pct) / max(abs(avg_profit_pct), 0.1)
If consistency > 0.90: not eligible for promotion
Gate is lenient (90% not 70%) - reality check: early data is noisy

### Normalization (LOCKED order - critical):
Step 1: Check consistency gate on RAW values (before winsorization)
Step 2: Winsorize at 5th/95th percentile on RAW values
Step 3: Normalize 0-1 using min/max of winsorized values
Step 4: Apply weights to get RARS

IMPORTANT: Exclude benchmarks from normalization pool.
Normalize only 139 method variations against each other.
Benchmarks shown in report for comparison only.

### Final RARS:
RARS = (0.35 x cap_eff_norm) +
      (0.30 x drawdown_norm) +
      (0.20 x win_rate) +
      (0.15 x profit_factor_norm)

### Per regime separately:
- RARS_bull: trades where regime_at_entry = bull only
- RARS_bear: trades where regime_at_entry = bear only
- RARS_sideways: sideways only
- RARS_overall: informational only, not used for promotion

### Scoring and promotion level:
Score: per VARIATION (E11-3 tracked separately)
Promote: best VARIATION that meets all criteria
(not method median - avoids burying alpha in weak variations)
Champion: specific variation deployed (e.g. E11-3, not E11)

### Median across coins (not mean):
Use MEDIAN of coin results per variation.
Prevents one lucky/unlucky coin skewing score.

---

## 8. Short RARS Formula (Separate, LOCKED)

Never mix Long and Short RARS in same ranking.
Tag: direction = short in research_scores.

Short DCA profits from momentum (price rises then drops).
Long DCA profits from mean reversion (price falls then recovers).

Short RARS dimensions:
| Dimension | Weight | Notes |
|-----------|--------|-------|
| Drawdown Control | 35% | Unlimited loss risk - priority 1 |
| Win Rate | 25% | Still needs to win |
| Capital Efficiency | 20% | Profit per coin-value x days |
| Buyback Success Rate | 15% | Operational success |
| Profit Factor | 5% | Tiebreaker |

Buyback success definition (precise):
buyback_success = positions_closed_via_TP / total_short_positions_OPENED
Use total OPENED (not total closed) - includes stuck positions
closed via TP = success
closed by any other means (manual, circuit breaker, ST flag) = failure

---

## 9. Three Champions System (LOCKED)

One champion per regime:
- Bull Champion
- Bear Champion
- Sideways Champion

Starting champion all 3 regimes: E10 variation E10-1 (control group)
Everything must beat E10 to be promoted.

How bot uses champion:
Every 60s cycle reads today regime from market_regimes table.
Looks up champion for that regime from smart_dca_champions.
All NEW positions use that method+variation signal.
EXISTING positions never affected (keep original params forever).

Champion change = update one DB row, instant, no restart needed.

---

## 10. Promotion Eligibility (LOCKED - Realistic)

ALL required before any tier considered:
- 50 total closed trades (was 100 - reality check)
- 20 trades in TARGET REGIME specifically (was 30)
- 3+ different regimes tested
- 30-day cooldown after parameter change
- Consistency gate passed (only if total trades >= 100)

Why lower thresholds:
In 6 months some variations may only reach 50-80 trades.
Lower threshold = real promotions happen.
Higher threshold = E10 stays champion forever.

---

## 11. Three-Tier Promotion System (LOCKED)

Evaluated in strict order. Tier 2 only if Tier 1 fails. Tier 3 only if both fail.

### Tier 1 (preferred):
- 4 consecutive weeks beating champion in CURRENT regime
- challenger RARS >= champion_rars_locked x 1.10 (10% margin)
- 10+ trades in those 4 weeks
- champion_rars_locked = MAX(current_rars, avg_rars_last_4_weeks) at challenge start
- RESETS if regime changes (consecutive streak broken)
- When Tier 1 resets: all prior weekly wins preserved in Tier 2 window automatically

### Tier 1 "failed" definition:
8 weeks passed without achieving 4 consecutive.
Regime resets do NOT count as failure - only time expiry.
After 8 weeks without Tier 1 success: Tier 2 activates.

### Tier 2 (only after Tier 1 fails):
- 6 wins out of any rolling 8 consecutive weeks
- Same 10% margin above locked champion RARS
- 15+ trades in those 8 weeks
- PAUSES (not resets) if regime changes
- Paused weeks = no data, not counted as loss or win
- Tier 1 reset evidence carries forward into Tier 2 window

### Tier 3 (only after Tier 1 AND Tier 2 both fail after 6 months):
- Full 6 months completed
- Highest RARS variation that:
 1. Beats E10 by 10%
 2. Meets all eligibility (50 trades, 20 regime trades)
 3. If multiple qualify: highest RARS wins
 4. If none qualify: no_alpha_detected = TRUE
- Always produces a winner if any eligible method exists

### If nobody beats E10 at all:
- Telegram alert to Bader
- no_alpha_detected = TRUE in smart_dca_champions
- Keep E10 as champion
- Do NOT auto-switch to Simple DCA
- Human reviews situation

### Promotion margin:
10% above champion (not 15% - reality check)
Reason: 15% is hard to sustain over 4 consecutive weeks
10% is meaningful edge while remaining achievable

---

## 12. Bear Market Rules (LOCKED)

### Normal bear confirmation: 2 weeks
Bull and Sideways = 4 weeks.
Bear moves faster, need faster response.

### Bear circuit breaker (emergency only):
Trigger: current bear champion max_drawdown > 40% in last 30 days
(raised from 30% - reality check: 30% is normal in bear markets)

Grace period: new champion gets 30-day grace (no circuit breaker check)
Reason: outlier drawdown in first week should not trigger switch

Cooldown: maximum ONE circuit breaker switch per 30 days per regime

On trigger - use LIVE query (not cached Sunday data):
SELECT method, variation, AVG(max_drawdown_pct) as recent_dd
FROM positions
WHERE is_research = TRUE
AND regime_at_entry = current_regime
AND opened_at >= NOW() - INTERVAL 14 days
AND method != current_champion
GROUP BY method, variation
HAVING COUNT(*) >= 20
ORDER BY recent_dd ASC
LIMIT 1

Edge case 1: No qualified replacement (< 20 trades)
Action: Switch to E10 as safe fallback regardless of drawdown

Edge case 2: All methods distressed (all > 40% drawdown)
Action: Do NOT switch, alert Bader:
"All methods in distress - manual review required"
Keep current champion, no_alpha_detected = TRUE

Edge case 3: Circuit breaker fires on E10 itself
Action: Same as edge case 2 - alert and do not switch

What circuit breaker changes: ONLY which method signals entries
Does NOT change: DCA spacing, TP%, coin selection, trade size, existing positions

---

## 13. Auto-Switch System (LOCKED)

Admin dashboard toggle: [Auto Switch: ON/OFF]

When ON: confirmed -> switch immediately -> notify Bader
When OFF: confirmed -> alert Bader -> wait approval

Always notify regardless of toggle:
"Champion switched: Bull E10-1 -> E11-3
RARS: 0.687 vs 0.621 (+10.6% above threshold)
Method: Tier 1 confirmed (4 weeks, 38 trades)
[View Report] [Revert if needed]"

Manual override always available, instant effect.
Revert to previous champion with one click.
Champion change = one DB row update.

---

## 14. Never Delete Policy (LOCKED)

All 14 methods run forever.
Poor performers -> Monitor tier (never deleted).
Reason: bear loser = next bull winner on regime flip.
Only replacement: zero-trade bots (signal never triggers in 30 days).
Replace with: looser variation of same method.
All data kept forever (< 5MB per year).

---

## 15. Confidence Tiers (Metadata Only)

Shown in report and dashboard for context only.
Does NOT affect scoring or promotion.

| Tier | Trades |
|------|--------|
| Bronze | 50-199 |
| Silver | 200-499 |
| Gold | 500-1999 |
| Platinum | 2000+ |

Prevents misreading RARS 0.82 (52 trades) as equal to RARS 0.79 (3,400 trades).

---

## 16. Weekly Report Structure (LOCKED)

Generated Sunday 05:00, pushed GitHub, markdown download.

Sections:
1. Current champions (Bull, Bear, Sideways) with confidence tier
2. Challengers in confirmation (Tier, Week X of 4/8)
3. BULL LEADERBOARD (only bull-regime trades scored)
4. BEAR LEADERBOARD (only bear-regime trades scored)
5. SIDEWAYS LEADERBOARD (only sideways trades scored)
6. Benchmark comparison (for reference only, not in normalization)
7. Regime this week + signal breakdown (which signals fired)
8. Server health (loop time, trade counts, DB size)
9. Alerts (zero-trade bots, methods approaching gate failure)

Per method per leaderboard shows:

Open positions:
- Coin, opened date, days open, entry price, current price
- DCAs fired, current PnL%, max drawdown so far
- regime_changed_during_trade flag

Closed trades this week:
- Coin, entry, exit, days, DCAs, USDT deployed, profit%, regime tag

Performance summary:
- Win rate, avg profit per win, avg loss per loss
- Profit factor, max drawdown, avg DCAs, avg days
- Avg USDT deployed (peak), capital efficiency score
- RARS_bull, RARS_bear, RARS_sideways, RARS_overall
- vs E10, vs Random Entry benchmark
- Confidence tier, trades in each regime
- Consistency gate: passed/failed/not yet applied (< 100 trades)
- data_sparse flag, low_frequency note if applicable

Low frequency method note (E4 etc):
"Low frequency method - Tier 1 may be impossible.
Monitoring via Tier 2 and Tier 3 paths."

---

## 17. Database Schema Required

smart_dca_champions (create before research starts):
CREATE TABLE smart_dca_champions (
   id SERIAL PRIMARY KEY,
   regime VARCHAR(20) NOT NULL UNIQUE,
   method VARCHAR(20) NOT NULL DEFAULT 'E10',
   best_variation VARCHAR(20) DEFAULT 'E10-1',
   rars_score DECIMAL(10,6) DEFAULT 0,
   confirmed_at TIMESTAMP,
   confirmation_tier INTEGER DEFAULT 0,
   challenger_method VARCHAR(20),
   challenger_variation VARCHAR(20),
   challenger_weeks INTEGER DEFAULT 0,
   challenger_rars DECIMAL(10,6),
   champion_rars_locked DECIMAL(10,6),
   auto_switch BOOLEAN DEFAULT TRUE,
   switched_at TIMESTAMP,
   previous_method VARCHAR(20),
   no_alpha_detected BOOLEAN DEFAULT FALSE,
   circuit_breaker_fired BOOLEAN DEFAULT FALSE,
   circuit_breaker_last_fired TIMESTAMP,
   days_as_champion INTEGER DEFAULT 0,
   created_at TIMESTAMP DEFAULT NOW(),
   updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO smart_dca_champions (regime, method, best_variation)
VALUES ('bull','E10','E10-1'),
      ('bear','E10','E10-1'),
      ('sideways','E10','E10-1')
ON CONFLICT (regime) DO NOTHING;

champion_challengers:
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
   paused_at TIMESTAMP,
   paused_weeks_accumulated INTEGER DEFAULT 0,
   historical_wins JSONB DEFAULT '[]',
   tier1_failed_at TIMESTAMP,
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
ADD COLUMN IF NOT EXISTS consistency_checked BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS avg_dca_count DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS avg_days_open DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS avg_usdt_deployed DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS cap_efficiency DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_bull DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_bear DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_sideways DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_overall DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS data_sparse BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS confidence_tier VARCHAR(10) DEFAULT 'bronze',
ADD COLUMN IF NOT EXISTS regime_trade_counts JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS buyback_success_rate DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS low_frequency BOOLEAN DEFAULT FALSE;

trades additions:
ALTER TABLE trades
ADD COLUMN IF NOT EXISTS regime_changed_during_trade BOOLEAN DEFAULT FALSE;

market_regimes additions:
ALTER TABLE market_regimes
ADD COLUMN IF NOT EXISTS signal_agreement_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS btc_combined_score INTEGER DEFAULT 0;

---

## 18. generate_metrics.py Flow (LOCKED)

Runs every Sunday 05:00 automatically. Zero human action needed.

Step 1: Read all closed research trades from DB
Step 2: Separate by direction (long/short) and regime (bull/bear/sideways)
Step 3: For each variation in each regime:
       - Skip if trades < 50 (mark data_sparse=TRUE)
       - If trades >= 100: check consistency gate on RAW values
       - Calculate 4 raw dimensions
Step 4: Winsorize raw dimension values at 5th/95th percentile
       (exclude benchmarks from this pool)
Step 5: Normalize each dimension 0-1 across all 139 variations only
Step 6: Calculate RARS = 0.35*cap + 0.30*dd + 0.20*wr + 0.15*pf
Step 7: Use MEDIAN across coins (not mean)
Step 8: Determine confidence tier based on trade count
Step 9: Check promotion per regime (strict order):
       a. Check Tier 1 (4 consecutive + 10 trades + 10% margin)
       b. If Tier 1 failed (8 weeks): activate Tier 2
       c. Check Tier 2 (6 of 8 rolling + 15 trades + 10% margin)
       d. If 6 months elapsed and Tier 1+2 both failed: check Tier 3
Step 10: Check bear circuit breaker (live query, not cached)
        Skip if champion < 30 days old
        Skip if circuit breaker fired in last 30 days
Step 11: Execute champion switch if confirmed
        auto_switch ON: switch + notify immediately
        auto_switch OFF: alert + wait for approval
Step 12: Save scores to research_scores table
Step 13: Generate 3 leaderboards (Bull/Bear/Sideways)
Step 14: Generate full markdown weekly report
Step 15: Push report to GitHub
Step 16: Telegram notification:
        "Weekly report ready
         Bull: E10-1 (no change) Bronze
         Bear: E10-1 (no change) Bronze
         Sideways: E10-1 (no change) Bronze
         [Download URL]"

Zero trades week: confirmation counter unchanged (no win, no loss, no reset)
Paused weeks (regime flip): not counted as win or loss in Tier 2 window

---

## 19. All Locked Decisions

| Decision | Rule |
|----------|------|
| Champions | 3 (Bull, Bear, Sideways) |
| Starting champion | E10-1 all regimes |
| Regime tag | At entry, never changes |
| Signals | 5 signals (Fear+Greed removed) |
| Signal scale | -6 to +6 |
| BTC cap | Combined BTC max +/-2 |
| Realized Vol | Log returns formula |
| RARS | Weighted additive, 4 dimensions |
| Weights | 35/30/20/15 |
| Consistency | Hard gate 90% (only after 100 trades) |
| Winsorize | Raw values first, 5th/95th percentile |
| Normalization | 0-1, exclude benchmarks from pool |
| Scoring | Per variation, promote best variation |
| Champion RARS locked | MAX(current, 4-week avg) at challenge start |
| Promotion margin | 10% above locked champion |
| Eligibility | 50 total, 20 regime-specific trades |
| Tier 1 | 4 consecutive, 10 trades, 10% margin |
| Tier 1 failed | 8 weeks without completion |
| Tier 1 reset | Preserves evidence for Tier 2 |
| Tier 2 | 6 of 8 rolling, 15 trades (Tier 1 must fail) |
| Tier 2 regime flip | PAUSE not reset |
| Tier 3 | 6 months, best RARS, beats E10 by 10% |
| Bear confirmation | 2 weeks |
| Circuit breaker | 40% drawdown, live query, 30-day grace |
| Circuit breaker cooldown | One switch per 30 days |
| Circuit breaker fallback | E10 if no qualified challenger |
| All distressed | Alert Bader, keep current, no switch |
| Auto-switch | Toggleable, always notify |
| Deletion | Never |
| Coins | Top 500, $1M volume, 90d data |
| Short RARS | Separate formula, Drawdown 35% first |
| Buyback success | TP closes / total opened |
| Report | Weekly Sunday, markdown, GitHub |
| Data retention | Forever |
| Zero trades week | Counter unchanged |
| Confidence tiers | Metadata only |
| Low frequency | Note in report, Tier 2/3 paths available |
