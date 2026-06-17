# Coin Classification System v2 - LOCKED SPEC
Finalized June 17 2026 after multi-AI review (ChatGPT + Gemini)
Applies to Smart DCA method only (research AND live, identically)
This replaces calculate_coin_params.py logic entirely

---

## What Changed From v1

Spacing formula: MIN(ATR*1.5, median_drop*0.85) -> MAX(ATR*1.5, median_drop*0.85)
Trailing formula: ATR*0.8 -> TP*0.25
TP formula: unchanged, median_recovery*0.8
Sample size check: none -> minimum 15 events else category default
Daily change cap: none -> spacing/TP +-20%, trailing +-15%, size_mult +-10%
Circuit breaker: none -> freeze + alert on extreme single-day data
New coins: none -> hard gate, blocked from Smart DCA until 30 days old
Stablecoins/pegged assets: none -> hardcoded exclusion blacklist
Category limits: hardcoded in Python -> DB table, admin-editable with guardrails
Audit trail: none -> full history table, every change logged
Position snapshot: none -> every position stores params it opened with
Delisted coins: not detected -> detected, frozen, alerted, no auto-sell
Per-exchange calc: hardcoded MEXC only -> stays MEXC-only for now

---

## 1. Categories (unchanged)
5 categories by market cap: Mega/Large/Mid/Small/Micro.
Classification signal = market cap only. Volume/age/volatility do NOT
affect category assignment.

## 2. Category Limits (NEW: DB-editable with guardrails)
Move CATEGORY_LIMITS from hardcoded Python into a new DB table:
category_limits (category, spacing_min, spacing_max, tp_min, tp_max,
trail_min, trail_max, size_min, size_max, updated_at, updated_by)

Admin can edit via dashboard, but every edit must pass:
- new_min < new_max (hard validation)
- values within absolute sane bounds (spacing never >50%, TP never >30%)
- preview shown before confirm: affected coin count
- every edit logged to audit trail

Daily cron alert: if >30% of coins in a category pinned at MIN or MAX
for 3+ consecutive days, send admin alert. Informational only.

## 3. New Coin Hard Gate (LOCKED — revised June 17 2026)
market_age_days was found unreliable: it measures how long Averion's
own tracking has watched a coin, not the coin's real-world age, and
resets to zero on any system wipe. CoinGecko genesis_date was tested
and rejected (0/19 real coins returned a usable value in live testing,
plus 42% rate-limiting even at conservative request pacing). Replaced
with a category-override + locally-tracked first_seen_at approach,
requiring zero external API calls and surviving any future wipe.

Final rule:
- Mega / Large / Mid cap: always eligible for Smart DCA immediately,
  regardless of age. A coin reaching $1B+ market cap is definitionally
  not an unproven new listing.
- Small / Micro cap, 0-30 days since first_seen_at: NOT eligible for
  Smart DCA. No new positions opened at all. This is a hard exclusion,
  not a "use safe defaults" fallback — the risk being protected against
  is the unproven coin itself (delisting, liquidity collapse, extreme
  pump/dump), not merely uncertain parameters. Conservative parameters
  do not make an unproven coin safe to hold.
- Small / Micro cap, 31-90 days: eligible. Parameters = 70% category
  default blended with 30% coin-specific calculation.
- Small / Micro cap, 90+ days: eligible for 100% coin-specific
  calculation, BUT ONLY IF the sample-size gate also passes (15+ drop
  events AND 15+ recovery events in the lookback window — same minimum
  as section 5). If sample size fails even past 90 days, remain on
  100% category default rather than trust a thin sample. Age alone is
  not sufficient; a coin can be old but still data-thin if it rarely
  trades.

first_seen_at is tracked locally: set once, the first time
classify_coins.py ever sees a given coin, and never overwritten again
even across future system/research wipes.

## 4. Stablecoin / Pegged Asset Exclusion (NEW)
Hardcoded exclusion list: USDC, USDT, FDUSD, TUSD, DAI, BUSD, USDP,
GUSD, WBTC, WBETH, stETH, wstETH, cbETH, rETH (extendable).
Never enter Smart DCA coin selection regardless of market cap.

## 5. Per-Coin Calculation (formula v2)

Minimum sample size check (NEW):
Need at least 15 valid drop events AND 15 valid recovery events.
If either below 15: use category default midpoint instead.

If sample size sufficient:
atr_pct = ATR_14 / current_price * 100
median_drop = median of qualifying drop events (>=15 required)
median_recovery = median of qualifying recovery events (>=15 required)

spacing_raw = MAX(atr_pct * 1.5, median_drop * 0.85)
spacing = clamp(spacing_raw, category.spacing_min, category.spacing_max)

tp_raw = median_recovery * 0.8
tp = clamp(tp_raw, category.tp_min, category.tp_max)

trailing_raw = tp * 0.25
trailing = clamp(trailing_raw, category.trail_min, category.trail_max)

size_mult = clamp(1 + atr_pct/10, category.size_min, category.size_max)

## 6. Daily Change Cap (NEW)
Clamp against yesterday's stored value, applied AFTER category clamp:
spacing: max change +-20% of yesterday
TP: max change +-20% of yesterday
trailing: max change +-15% of yesterday
size_mult: max change +-10% of yesterday

## 7. Circuit Breaker (NEW)
Before normal calculation, check data integrity. If ANY true, FREEZE
(keep yesterday's params, no recalculation) and alert admin:
- today's ATR > 3x yesterday's ATR
- price gap > 50% in a single day
- median_drop changed > 2x from yesterday
- zero volume in last 24 hours
- missing/null candles in recent window

Frozen coins flagged data_quality = frozen_anomaly, skipped until
anomaly clears or admin reviews manually.

## 8. Delisted / Dead Coin Detection (NEW)
Detected when ANY of:
- no OHLCV data for 24+ hours
- exchange returns BadSymbol / ExchangeNotAvailable via CCXT
- 24h volume = exactly 0

On detection:
- Mark coin status = UNTRADEABLE
- Stop opening new positions immediately
- Hide from new bot coin-selection lists
- Alert admin + affected users via Telegram
- Do NOT auto-sell open positions, freeze and let user/admin decide

## 9. Audit Trail (NEW)
New table coin_parameter_history:
coin, exchange, category, old_spacing, new_spacing, old_tp, new_tp,
old_trail, new_trail, old_size_mult, new_size_mult,
sample_count_drops, sample_count_recoveries, data_quality,
frozen_reason (nullable), calculation_version, created_at

Every daily run inserts one row per coin, whether value changed or not.

## 10. Position Snapshot (NEW)
Every position (research AND live, all tables: positions,
scalper_positions, live_dca_positions) stores at open time:
category_at_open, spacing_at_open, tp_at_open, trail_at_open,
size_mult_at_open, calculation_version

## 11. Calculation Versioning (NEW)
Every coin_parameters row and position snapshot tags
calculation_version = v2. Future changes increment this (v3, v4...).

---

## Implementation Note - Research Data Reset
This changes the actual formula, so existing research trade data
(generated under v1) is not comparable to v2 results. Research data
will be wiped and restarted fresh under v2 so all bots compete on
identical, current logic from day one.
