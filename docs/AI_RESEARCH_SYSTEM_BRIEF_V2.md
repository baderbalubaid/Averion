# Averion Research System Brief V2
## For AI Validation

---

## 1. Three Champions System

One champion per market regime:
- Bull Champion: used when regime = bull
- Bear Champion: used when regime = bear
- Sideways Champion: used when regime = sideways

Starting champion all regimes: E10 (control group)
Everything must beat E10 to be promoted.

Regime tagged at trade ENTRY (never changes):
Trade opened in bull = always scored in bull leaderboard.

---

## 2. Coin Universe (LOCKED)
- Top 500 coins by market cap (CoinGecko daily)
- Available on MEXC or KuCoin
- 24h volume >= $1,000,000
- 90+ days OHLCV data (excludes new coins)
- Result: ~200-300 tradeable coins

---

## 3. Trade Scaling Plan

| Week | Trades/Bot | Long Total | Short Total |
|------|-----------|-----------|-------------|
| 1 | 1 | 144 | 0 |
| 2 | 10 | 1,440 | 0 |
| 3 | 20 | 2,880 | 0 |
| 4 | 30 | 4,320 | 720 |
| Month 2 | 50 | 7,200 | 720 |

Server thresholds:
- Green: loop < 30s
- Yellow: 30-50s
- Red: > 50s, upgrade to CX33

---

## 4. Market Regime Detection (LOCKED V2)

6 signals scored daily at 04:30:

| Signal | Bull | Bear | Weight |
|--------|------|------|--------|
| BTC 7d change | >+5% = +2 | <-5% = -2 | 2 pts |
| Realized Vol 30d | <30% = +1 | >80% = -1 | 1 pt |
| Market cap 30d | >+10% = +1 | <-10% = -1 | 1 pt |
| Fear and Greed | >65 = +1 | <35 = -1 | 1 pt |
| BTC 200D MA | Above = +1 | Below = -1 | 1 pt |
| Altcoin Season | >75% = +1 | <25% = -1 | 1 pt |

Scale: -7 to +7
- Strong Bull: >= +5
- Bull: +2 to +4
- Sideways: -1 to +1
- Bear: -2 to -4
- Strong Bear: <= -5

Sources (all from existing data):
- BTC 7d change: ohlcv_hourly table
- Realized Vol: std_dev(daily_returns_30d) x sqrt(365)
- Market cap 30d: coin_history table
- Fear and Greed: api.alternative.me/fng/ (free)
- BTC 200D MA: ohlcv_hourly table
- Altcoin Season: % top 50 alts beating BTC from ohlcv_hourly

---

## 5. Data Collected Per Trade

Every research trade records:
- method (E1-E14), variation (E11-3 etc)
- coin, exchange
- entry_price, exit_price
- profit_pct, profit_usdt
- dca_count (DCAs before TP)
- days_open
- max_drawdown_pct
- max_usdt_deployed (entry + all DCAs)
- regime at entry (bull/bear/sideways, never changes)
- entry_signal_data JSONB
- is_research = TRUE
- direction (long/short)

---

## 6. RARS Scoring Formula V2 (LOCKED)

### Weighted Additive (not multiplicative)
Reason: multiplicative collapses if one dimension is weak.

### 5 Dimensions and Weights:

Dimension 1: Capital Efficiency (35%)
cap_efficiency = avg_profit_usdt / (avg_max_usdt_deployed x max(avg_days_open, 1))
Measures profit per dollar deployed per day.

Dimension 2: Drawdown Control (25%)
drawdown_control = 1 - ((max_dd + 0.005) / 100)
Fixed denominator: use max_dd + 0.005 not max(max_dd, 0.01)

Dimension 3: Win Rate (20%)
win_rate = winning_trades / total_closed_trades

Dimension 4: Profit Factor (15%)
profit_factor = gross_profit / max(gross_loss, 0.01)
Capped at 10.0, then normalized: pf_norm = pf_capped / 10.0
Why: Win rate alone can hide big losses on losing trades.

Dimension 5: Consistency Score (5%)
consistency = 1 - (std_dev_of_profits / max(avg_profit, 0.001))
Replaces Recovery Speed (which double-counted days_open).
Calculated via PostgreSQL STDDEV_POP().

### Normalization (before applying weights):
norm = (value - min_across_all_methods) / (max - min)
Each dimension normalized 0-1 relative to ALL methods in same regime.

### Final RARS:
RARS = (0.35 x cap_eff_norm) +
       (0.25 x drawdown_norm) +
       (0.20 x win_rate) +
       (0.15 x profit_factor_norm) +
       (0.05 x consistency_norm)

### Per regime separately:
- RARS_bull: only bull regime trades
- RARS_bear: only bear regime trades
- RARS_sideways: only sideways trades
- RARS_overall: all trades (informational only)

### Median not mean (LOCKED):
Use MEDIAN across all coins, not average.
Prevents one lucky coin skewing entire method score.

---

## 7. Short RARS Formula (Separate)

Short DCA profits from momentum (price rises then drops).
Long DCA profits from mean reversion (price falls then recovers).
Never mix Long and Short RARS in same ranking.

Short RARS dimensions:
| Dimension | Weight |
|-----------|--------|
| Buyback Success Rate (orders filled / placed) | 30% |
| Capital Efficiency (profit / coin_value x days) | 30% |
| Win Rate | 20% |
| Drawdown Control (max adverse move) | 15% |
| Profit Factor | 5% |

Stored with direction = short tag in research_scores.

---

## 8. Three-Tier Promotion System (LOCKED)

### Eligibility (all required):
- Minimum 100 closed trades total
- Tested in 3+ market regimes
- 30-day cooldown after parameter change
- data_sparse = FALSE

### Tier 1 (preferred):
- 4 consecutive winning weeks
- challenger RARS >= champion RARS x 1.15
- minimum 20 trades in those 4 weeks
- regime stays same throughout (resets if regime flips)

### Tier 2 (fallback):
- 6 wins out of any 8 consecutive weeks
- challenger RARS >= champion RARS x 1.15
- minimum 30 trades in those 8 weeks

### Tier 3 (last resort after 6 months):
- Full 6 months completed
- No Tier 1 or Tier 2 qualification
- Highest RARS beats E10 by 15%
- Always produces a winner

### If nobody beats E10 at all:
- Telegram alert to Bader
- Mark: no_alpha_detected = TRUE
- Keep E10 as champion
- Do NOT auto-switch to Simple DCA
- Human reviews

### Bear confirmation = 2 weeks (not 4):
Bear market moves fast. 4 weeks too slow for capital protection.
Bull and Sideways = 4 weeks.

---

## 9. Auto-Switch System (LOCKED)

Admin dashboard toggle: [Auto Switch: ON/OFF]

When ON: confirmed -> switch immediately -> notify Bader
When OFF: confirmed -> alert Bader -> wait approval

Notification always sent:
"Champion switched: Bull E10-1 -> E11-3
RARS: 0.745 vs 0.621 (+20% above threshold)
4 consecutive weeks confirmed, 47 trades
[View Report] [Revert if needed]"

Manual override always available.
Champion change = update one DB row, instant effect.

---

## 10. Never Delete Policy (LOCKED)

All 14 methods run forever.
Poor performers -> Monitor tier (not deleted).
Reason: bear loser = next bull winner.
Only replace: zero-trade bots (signal never fires).
All data kept forever (< 5MB per year).

---

## 11. Weekly Report Structure (LOCKED)

Generated Sunday 05:00, pushed GitHub, markdown download.

Sections:
1. Current champions (Bull, Bear, Sideways)
2. Challengers in confirmation (week X of 4)
3. BULL LEADERBOARD (bull trades only)
4. BEAR LEADERBOARD (bear trades only)
5. SIDEWAYS LEADERBOARD (sideways trades only)
6. Benchmark comparison table
7. Regime analysis this week
8. Server health stats
9. Alerts (zero-trade, declining methods)

Per method shows:
Open positions:
- Coin, opened date, days open, entry, current, DCAs, PnL%, max drawdown so far

Closed trades this week:
- Coin, entry, exit, days, DCAs, USDT deployed, profit%, regime

Performance summary:
- Win rate, avg profit, avg loss, profit factor
- Max drawdown, avg DCAs, avg days, USDT deployed avg
- Capital efficiency score, consistency score
- RARS per regime, vs E10, vs Random Entry
- Data sparse flag

---

## 12. Database Schema Required

smart_dca_champions table (MISSING from current schema):
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
    auto_switch BOOLEAN DEFAULT TRUE,
    switched_at TIMESTAMP,
    previous_method VARCHAR(20),
    no_alpha_detected BOOLEAN DEFAULT FALSE,
    fallback_to_random BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO smart_dca_champions (regime, method, best_variation)
VALUES ('bull','E10','E10-1'),
       ('bear','E10','E10-1'),
       ('sideways','E10','E10-1')
ON CONFLICT (regime) DO NOTHING;

champion_challengers table:
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
    pct_above_champion DECIMAL(10,4),
    first_detected TIMESTAMP DEFAULT NOW(),
    last_confirmed TIMESTAMP DEFAULT NOW(),
    reset_count INTEGER DEFAULT 0
);

research_scores additions needed:
ALTER TABLE research_scores
ADD COLUMN IF NOT EXISTS direction VARCHAR(10) DEFAULT 'long',
ADD COLUMN IF NOT EXISTS gross_profit DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS gross_loss DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS profit_factor DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS consistency_score DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS avg_dca_count DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS avg_days_open DECIMAL(10,4) DEFAULT 0,
ADD COLUMN IF NOT EXISTS avg_usdt_deployed DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS cap_efficiency DECIMAL(20,8) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_bull DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_bear DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_sideways DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS rars_overall DECIMAL(10,6) DEFAULT 0,
ADD COLUMN IF NOT EXISTS data_sparse BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS buyback_success_rate DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS inventory_locked_days DECIMAL(10,2);

---

## 13. All Locked Decisions

| Decision | Rule |
|----------|------|
| Champions | 3 (Bull, Bear, Sideways) |
| Starting champion | E10 control group |
| Regime tagging | At entry, never changes |
| Tier 1 confirmation | 4 consecutive, 20 trades, +15% |
| Tier 2 confirmation | 6 of 8 weeks, 30 trades, +15% |
| Tier 3 confirmation | 6 months, best RARS, +15% |
| Bear confirmation | 2 weeks not 4 |
| Window reset | On regime change mid-confirmation |
| Auto-switch | Toggleable, always notify |
| Deletion | Never |
| Coins | Top 500, $1M volume, 90d data |
| RARS | Weighted additive, 5 dimensions |
| Weights | 35/25/20/15/5 |
| Cap efficiency | profit_usdt / (deployed x days) |
| Normalization | 0-1 per dimension across all methods |
| Scoring | Per variation, promote per method |
| Short RARS | Separate formula |
| Report | Weekly Sunday, markdown, GitHub |
| Data retention | Forever |
| All lose | Alert Bader, keep E10 |
| Volume filter | $1M minimum |
| Regime signals | 6 signals, scale -7 to +7 |

---

## 14. Questions for AI Review V2

1. Is weighted additive RARS correct for DCA?
   Are weights 35/25/20/15/5 optimal?

2. Is capital efficiency formula correct?
   profit_usdt / (avg_max_usdt_deployed x avg_days_open)

3. Is 3-tier promotion system correct?
   Any gaps that could produce wrong champion?

4. Is 2 weeks for bear confirmation right?
   Should it be even shorter (1 week)?

5. Are 6 regime signals sufficient and weighted correctly?

6. Should we add sub-regimes (Bull-High-Vol etc)?
   Or keep 3 simple regimes?

7. Consistency score formula correct?
   1 - (std_dev / avg_profit)

8. Short RARS: is buyback_success_rate most important?

9. Minimum bear trades before bear champion reliable?
   Our 100 trade minimum enough?

10. Any flaw in tiered promotion that could produce wrong champion?

---

## 13. generate_metrics.py Flow (Weekly Automation)

Runs every Sunday 05:00 automatically.
No human action needed.

Step 1: Read all closed research trades from DB
- Separate by direction (long/short)
- Separate by regime (bull/bear/sideways)

Step 2: For each regime, score each variation
- Skip if trades < 30 (mark data_sparse=TRUE)
- Calculate 5 raw dimensions
- Calculate RARS per variation

Step 3: Normalize all dimensions 0-1
- Find min/max across ALL variations in regime
- Normalize each dimension relative to peers

Step 4: Apply weights, calculate final RARS
- RARS = 0.35*cap + 0.25*dd + 0.20*wr + 0.15*pf + 0.05*con

Step 5: Aggregate to method level
- Use MEDIAN of variations (not mean)
- Best variation identified per method

Step 6: Check promotion tiers per regime
- Tier 1: 4 consecutive weeks + 20 trades + 15% margin
- Tier 2: 6 of 8 weeks + 30 trades + 15% margin
- Tier 3: 6 months passed + best RARS + 15% over E10

Step 7: If champion confirmed
- auto_switch ON: switch immediately
- auto_switch OFF: alert Bader, wait approval
- Always send Telegram notification

Step 8: Save all scores to research_scores table

Step 9: Generate markdown weekly report
- 3 separate leaderboards (Bull/Bear/Sideways)
- Per method: open positions + closed trades
- Benchmark comparison
- Alerts and server health

Step 10: Push report to GitHub
- URL: github.com/baderbalubaid/Averion/research/

Step 11: Telegram notification
- "Weekly report ready"
- Champion status
- Any changes
- Download URL
