# Averion System Map
> Last updated: June 16, 2026
> Read this before every session. Check related code before coding anything.
> Status: WORKING=end-to-end | PARTIAL=coded incomplete | MISSING=not coded

---

## THREE SYSTEMS

| System | Engine | Bots | Table | Rule |
|--------|--------|------|-------|------|
| Research DCA | research_engine.py | 366 (E1-E66) | positions | UNTOUCHABLE |
| Research Scalper | scalper_engine.py + scalper_v2_engine.py | 120 E58 + 120 E58v2 | scalper_positions | E58 UNTOUCHABLE |
| Live | live_long_dca_engine.py + live_scalper_engine.py | 5 live bots | live_dca_positions + live_positions | Active dev |

PM2: id=1 averion-api (api.py port 8080) | id=5 averion-research (research_engine.py)
Server: root@167.233.45.171 | Domain: averionbot.com

---

## THE CHAIN

[1] COIN SELECTED
[2] CATEGORY ASSIGNED
[3] PARAMS CALCULATED
[4] REGIME CHECKED
[5] SIGNAL FIRES
[6] WALLET VERIFIED
[7] ORDER EXECUTED
[8] POSITION TRACKED
[9] DCA MANAGED
[10] TP FIRES
[11] FEE COLLECTED
[12] USER NOTIFIED
[13] REPORT GENERATED

---

## LEGEND

### [1] COIN SELECTED
WHAT: Which coin to trade on which exchange.
WHY: Not every MEXC coin is tradeable. Some are ST flagged, some below minimum order size, some have no volume.
HOW:
- research_engine.py fetches ALL tickers from MEXC via exchange_obj.fetch_tickers()
- Each bot has specific_coins in bot_params (if set, only those coins considered)
- ST flag check: check_st_flag() skips suspended coins
- trades_per_coin controls max concurrent positions per coin
- trades_per_bot controls max total open positions per bot
FILES: research_engine.py | live_long_dca_engine.py | websocket_prices.py
TABLE: Redis price:MEXC:COIN/USDT
SYSTEMS: Research DCA=WORKING | Research Scalper=WORKING | Live DCA=WORKING | Live Scalper=WORKING
GAPS: trades_per_coin and trades_per_bot exist in DB but not fully enforced in all engines
CHANGE IMPACT: research_engine.py + live_long_dca_engine.py + all open position logic

---

### [2] CATEGORY ASSIGNED
WHAT: Every coin placed into 1 of 5 size buckets based on market cap.
WHY: A $5B coin needs tighter DCA spacing than a $1M micro-cap. Category determines safe parameters.
CATEGORIES:
- mega: >$100B (BTC,ETH) spacing=2% TP=1%
- large: $10B-$100B (SOL,BNB) spacing=5% TP=2%
- mid: $1B-$10B spacing=7% TP=4%
- small: $100M-$1B spacing=10% TP=5%
- micro: <$100M spacing=15% TP=8% (most MEXC coins)
HOW:
- classify_coins.py runs daily 03:30 UTC
- Fetches top 250 from CoinGecko, maps symbol to category, writes to coin_history
- Cap protection: upward max +10%/day, downward immediate (prevents fake pumps)
- calculate_coin_params.py reads coin_history, calculates precise params, writes coin_parameters
- On trade open: db.get_all_coin_categories() assigns category to position
FILES: classify_coins.py | calculate_coin_params.py | database.py
TABLES: coin_history | coin_parameters
SYSTEMS: Research DCA=WORKING | Live DCA=WORKING | Scalpers=NOT USED
STATUS: WORKING - 1849 coins classified June 16 2026
LOCKED RULE: Reclassification affects NEW positions only. Open positions keep original forever.
CHANGE IMPACT: coin_parameters + research_engine.py + live_long_dca_engine.py + admin categories tab

---

### [3] PARAMS CALCULATED
WHAT: Exact DCA spacing%, TP%, trailing% per coin based on volatility and category.
WHY: One-size DCA% is too tight for volatile micro-caps and too loose for stable large-caps.
HOW:
- calculate_coin_params.py fetches 90 days hourly OHLCV from ohlcv_data table
- Calculates ATR, median drop%, median recovery%, volatility
- Applies category limits (micro: spacing 15-40%, TP 8-20%)
- Writes to coin_parameters: dca_spacing, take_profit_pct, trailing_pct, size_multiplier
- No data fallback: uses category defaults
- Runs daily 04:00 UTC
FILES: calculate_coin_params.py | fetch_ohlcv.py
TABLES: ohlcv_data | coin_parameters
SYSTEMS: Research DCA=WORKING | Live DCA=WORKING | Scalpers=NOT USED
STATUS: WORKING
CHANGE IMPACT: coin_parameters + all open position DCA/TP logic + report CSVs

---

### [4] REGIME CHECKED
WHAT: Current Bitcoin market condition: bull / bear / sideways.
WHY: Methods that work in bull may fail in bear. Tagging every trade with regime lets us analyze which methods work in which conditions and eventually auto-select best method per regime.
HOW:
- get_btc_regime_data() in research_engine.py runs every cycle
- BTC price vs SMA50: bull if BTC > SMA50x1.02 | bear if BTC < SMA50x0.98 | sideways otherwise
- Also captures: btc_24h_change, btc_dominance, btc_sma50
- Stored in Redis btc:regime_data (10 min TTL) shared by all engines
- Recorded on every position open in all systems
FILES: research_engine.py (line 408) | live_long_dca_engine.py | scalper_v2_engine.py
REDIS KEY: btc:regime_data
TABLES: positions.btc_regime | scalper_positions.btc_regime | live_dca_positions.btc_regime
SYSTEMS: Research DCA=WORKING | Research Scalper=WORKING | Live DCA=WORKING
STATUS: WORKING - currently ALL data is bear (BTC below SMA50)
MISSING:
- Regime-aware champion selection (Phase 4)
- Dashboard regime sub-tabs (show only when 30+ trades per regime)
- Auto-switch live bot method based on regime
CHANGE IMPACT: research_engine.py line 408 + all position tables + report regime breakdown

---

### [5] SIGNAL FIRES
WHAT: Entry method evaluates price data and decides YES or NO to open a position.
WHY: We dont buy randomly. Each method looks for a specific market condition.

DCA SIGNALS (E1-E66):
- entry_signals.py contains all 58+ methods
- Each receives OHLCV data + current price + BTC data, returns True/False
- research_engine.py calls es.check_entry_signal() once per coin per 130s cycle

SCALPER E58 SIGNAL:
- Fires on every WebSocket tick (not cycle based)
- Did price jump >= trigger_pct% in last window_sec seconds?
- Uses in-memory price_history deque (300 entries)

SCALPER E58v2 SIGNAL (velocity):
- Fires on every WebSocket tick
- ALL three must be true:
  change_3s >= vel_3s (e.g. +3% in 3 seconds)
  change_10s >= vel_10s (e.g. +6% in 10 seconds)
  accel_ratio >= threshold (recent faster than average)
- PLUS pump-chase guard: reject if +8% in 5s / +40% in 30s / +60% in 60s
- Catches entry DURING pump not after

FILES: entry_signals.py | research_engine.py | scalper_engine.py | scalper_v2_engine.py | live_long_dca_engine.py
SYSTEMS: All=WORKING
STATUS: WORKING
CHANGE IMPACT: entry_signals.py + engine using it + reset research bots for clean comparison

---

### [6] WALLET VERIFIED
WHAT: Before opening, check virtual wallet has enough capital for base order.
WHY: Each bot links to a virtual wallet. Multiple bots can share one wallet or have separate isolated wallets.
HOW:
- Each bot has wallet_id linking to virtual_wallets table
- Wallet has: allocation_amount (total) | current_balance (available) | committed_usdt (in open positions)
- Before open: check current_balance >= base_order
- After open: committed_usdt increases, current_balance decreases
- After TP: committed_usdt decreases, current_balance increases by profit
FILES: live_long_dca_engine.py (load_wallet line 148) | api.py | executor.py
TABLES: virtual_wallets | wallet_transactions
SYSTEMS: Live DCA=WORKING | Live Scalper=WORKING | Research=NOT USED (unlimited paper)
STATUS: WORKING for live
WALLETS LIVE NOW:
- id=1 Paper Wallet $10000 (research + live E31/E54)
- id=2 S10 $1000 (live scalper S10)
- id=3 S25 $1000 (live scalper S25)
CHANGE IMPACT: virtual_wallets + live_long_dca_engine.py + live_scalper_engine.py + executor.py + api.py + exchanges UI + bots UI

---

### [7] ORDER EXECUTED
WHAT: Actual buy order sent to exchange (or simulated for paper).
WHY: This is where intent becomes action.
HOW:
- executor.py has two adapters:
  PaperAdapter: simulates fill at current price, no real exchange call
  LiveAdapter: calls CCXT, places real market order, waits for fill
- Checks exchange minimum order size before placing
- Records: fill_price, fee_usdt, order_id, price_age_ms
- Market orders only (exception: Short DCA buyback uses limit)
- PAPER_MODE in .env (default=true, safe)
FILES: executor.py | exchanges.py | database.py
TABLES: positions / live_dca_positions / scalper_positions (INSERT on open)
SYSTEMS: Research=WORKING paper | Live=PARTIAL paper sim
STATUS: PARTIAL - paper working, limited live testing
CHANGE IMPACT: executor.py + exchanges.py + all position INSERT queries

---

### [8] POSITION TRACKED
WHAT: After opening, position recorded in DB and engine monitors every cycle for TP and DCA.
WHY: Bot must always know state: coin, entry price, DCA level, current PnL, TP status.
TRACKED PER POSITION:
- coin, direction, avg_cost, quantity, total_invested
- dca_count, last_buy_price (used for next DCA trigger)
- tp_armed, peak_price (for trailing TP)
- btc_regime, btc_24h_change_pct, btc_dominance, btc_sma50_at_entry
- market_age_days, category
- status: open / standby / tp_fired / closed / dead / archived
FILES: research_engine.py | live_long_dca_engine.py | database.py
TABLES: positions | live_dca_positions
SYSTEMS: All=WORKING
STATUS: WORKING

---

### [9] DCA MANAGED
WHAT: When price drops below trigger price, bot buys more to lower average cost.
WHY: Instead of panic selling on a dip, buy more at lower price so smaller recovery needed to profit.
HOW:
- Every 130 seconds, engine scores ALL open positions:
  score = loss_pct / required_usdt_for_next_dca
  Higher score = more recovery per dollar = funded first
- ONE best candidate picked (highest score)
- Check: current price <= last_buy_price x (1 - dca_spacing%)
- If yes AND wallet has capital: execute DCA buy
- Updates: avg_cost, dca_count, last_buy_price, total_invested
- After DCA: immediate rescan
- After TP fires: freed capital + immediate rescan
DCA AMOUNT: base_order x size_multiplier ^ dca_count
DCA SPACING SOURCE: coin_parameters.dca_spacing (calculated daily) OR bot.dca_pct (manual)
ONE DCA PER CYCLE: intentional. Predictable and auditable.
DCA NEVER STOPS: regardless of reserve balance (locked rule)
FILES: research_engine.py (run_smart_dca_queue) | live_long_dca_engine.py
TABLES: positions | live_dca_positions (UPDATE avg_cost, dca_count)
SYSTEMS: Research DCA=WORKING | Live DCA=WORKING | Scalpers=NOT USED
STATUS: WORKING
CHANGE IMPACT: DCA spacing from coin_parameters + last_buy_price logic + wallet balance check

---

### [10] TP FIRES
WHAT: When price rises enough above average cost, bot sells to realize profit.
WHY: Without TP bot holds forever. TP captures profits and frees capital for new trades.
HOW DCA TP WORKS:
- Every WebSocket tick: check_tp() called for each open position
- TP price = avg_cost x (1 + tp_pct%)
- Phase 1: price hits TP price, TP armed, start tracking peak
- Phase 2: price pulls back trail_pct% from peak, SELL
- If tp_pct - trail_pct < 1%: direct market sell (no trailing)
- Trailing only for Long DCA (not Short DCA)
- TP% source: coin_parameters.take_profit_pct
HOW SCALPER EXIT WORKS:
- Timer: exit after max_hold_sec
- Trailing stop (E58v2): trail from peak after 2% profit
- Stop loss: if price drops stop_loss_pct% from entry
FILES: research_engine.py (check_tp line 267) | live_long_dca_engine.py | websocket_prices.py
TABLES: positions.tp_armed | positions.peak_price | positions.status
SYSTEMS: All=WORKING
STATUS: WORKING (critical bug fixed - was only running twice daily, now real-time)
CHANGE IMPACT: check_tp logic + websocket callback + coin_parameters tp_pct + trailing formula

---

### [11] FEE COLLECTED
WHAT: 20% of profit taken when position closes in profit and moved to platform reserve.
WHY: Averion earns only when user earns. Loss months = $0 fee.
HOW:
- Position closes, calculate gross profit = total_sold_usdt - total_invested
- If profit > 0: fee = profit x 20%
- db.deduct_performance_fee(user_id, position_id, fee, gross_profit) called
- Deducts from user reserve_wallet balance
- Reserve alerts: <$5 warning | <$2 critical | $0 new positions pause
- Referral: 2.5% of 20% fee to referrer reserve wallet
NO FEE ON: research system | 0% fee accounts | loss trades
FILES: live_long_dca_engine.py (line 345) | database.py (deduct_performance_fee)
TABLES: reserve_wallets | wallet_transactions
SYSTEMS: Live DCA=PARTIAL | Live Scalper=MISSING
STATUS: PARTIAL - coded but NOWPayments top-up not complete
MISSING:
- NOWPayments API for reserve wallet top-up
- Reserve wallet balance UI for user
- Fee transfer to owner wallet (TRC20)
- Referral fee distribution
CHANGE IMPACT: database.py + live engines + reserve_wallets table + legal docs

---

### [12] USER NOTIFIED
WHAT: User informed about trade opens, DCAs, closes, and daily summaries.
WHY: Users cannot watch dashboard 24/7. Telegram and email keep them informed.
WHAT EXISTS:
- Telegram trade open: tg.notify_trade_open() in research_engine.py WORKING
- Telegram trade closed: tg.notify_trade_closed() in research_engine.py WORKING
- Telegram DCA: tg.notify_dca() in research_engine.py WORKING
- Daily/Weekly/Monthly reports: telegram.py CODED
- Verification code: WORKING
MISSING:
- Live DCA engine has NO telegram calls
- Live Scalper has NO telegram calls
- Email trade notifications (only verification email works)
- User Telegram connection UI
- Profit notification showing fee deducted
FILES: telegram.py | research_engine.py | live_long_dca_engine.py (missing calls)
TABLES: users.telegram_chat_id
SYSTEMS: Research DCA=WORKING | Live DCA=MISSING | Live Scalper=MISSING
STATUS: PARTIAL
CHANGE IMPACT: telegram.py + all engine files + users.telegram_chat_id

---

### [13] REPORT GENERATED
WHAT: Daily automated reports showing research performance to identify which methods to promote.
WHY: With 366+ bots running, manual review impossible. Reports rank methods so we know what works.
HOW:
- bash /home/averion/Averion/generate_reports.sh - one command generates everything
- generate_dca_report.py: reports/RESEARCH_DCA.md (58 methods)
- generate_scalper_report.py: reports/RESEARCH_SCALPER.md (120 E58 bots)
- generate_scalper_v2_report.py: reports/RESEARCH_SCALPER_V2.md (120 E58v2 bots)
- 12 CSV files: TOP5 bots + ALL trades per system per ranking type
- All pushed to GitHub automatically
- Runs daily after 05:00 UTC via daily_cron.sh
REPORT INCLUDES: Win rate | avg PnL | median PnL | std deviation | max streak | regime breakdown | market_age_days
FILES: generate_reports.sh | generate_dca_report.py | generate_scalper_report.py | generate_scalper_v2_report.py
TABLES: positions + scalper_positions (read only)
SYSTEMS: Research=WORKING | Live reports=MISSING
STATUS: WORKING

---

## STATUS MATRIX

| Step | Research DCA | Research Scalper | Live DCA | Live Scalper |
|------|-------------|-----------------|----------|--------------|
| [1] Coin Selected | WORKING | WORKING | WORKING | WORKING |
| [2] Category Assigned | WORKING | NOT USED | WORKING | NOT USED |
| [3] Params Calculated | WORKING | NOT USED | WORKING | NOT USED |
| [4] Regime Checked | WORKING | WORKING | WORKING | PARTIAL |
| [5] Signal Fires | WORKING | WORKING | WORKING | WORKING |
| [6] Wallet Verified | NOT USED | NOT USED | WORKING | WORKING |
| [7] Order Executed | WORKING paper | WORKING paper | PARTIAL | PARTIAL |
| [8] Position Tracked | WORKING | WORKING | WORKING | WORKING |
| [9] DCA Managed | WORKING | NOT USED | WORKING | NOT USED |
| [10] TP Fires | WORKING | WORKING | WORKING | WORKING |
| [11] Fee Collected | NOT USED | NOT USED | PARTIAL | MISSING |
| [12] User Notified | WORKING | MISSING | MISSING | MISSING |
| [13] Report Generated | WORKING | WORKING | MISSING | MISSING |

---

## WHAT IS NOT BUILT YET

| Feature | Priority |
|---------|---------|
| Live trade notifications Telegram | Before public launch |
| NOWPayments reserve wallet top-up | Before public launch |
| Fee transfer to owner TRC20 | Before public launch |
| Referral fee distribution | Before public launch |
| Email trade notifications | Before public launch |
| User Telegram connection UI | Before public launch |
| Short DCA system | Future |
| Regime-aware champion selection | Phase 4 |
| Bot creation wizard public | Before public launch |
| User registration public flow | Before public launch |
| Emergency halt | Before public launch |
| 100 trade limit enforcement | Before public launch |
| Paper timer 90 day auto-close | Before public launch |
| Live performance reports | Future |

---

## CHANGE IMPACT GUIDE

Change coin classification:
- classify_coins.py | coin_history | calculate_coin_params.py | coin_parameters
- research_engine.py | live_long_dca_engine.py | admin categories tab

Change DCA spacing or TP%:
- calculate_coin_params.py | coin_parameters
- research_engine.py | live_long_dca_engine.py
- Open positions NOT affected (locked rule)

Change regime detection:
- research_engine.py line 408 | live_long_dca_engine.py | scalper_v2_engine.py
- Redis btc:regime_data | all position tables btc_regime | report generators

Change scalper E58v2 signal:
- scalper_v2_engine.py | websocket_prices.py | scalper_positions
- admin Scalper V2 tabs | RESEARCH_SCALPER_V2.md | reset bots for clean data

Change wallet balance logic:
- virtual_wallets | live_long_dca_engine.py | live_scalper_engine.py
- executor.py | api.py wallet endpoints | exchanges UI | bots UI

Change fee calculation:
- database.py deduct_performance_fee | live_long_dca_engine.py
- reserve_wallets | legal docs | email templates | Telegram

Change position status values:
- positions status enum | ALL queries in research_engine.py
- live_long_dca_engine.py | api.py | frontend trades/history
- LOCKED: only 6 values: open / standby / tp_fired / closed / dead / archived

Change entry signal E1-E66:
- entry_signals.py | research_engine.py | live_long_dca_engine.py
- Running research bots need reset for clean comparison

---

## KEY FILES

| File | Purpose | Touch when |
|------|---------|-----------|
| research_engine.py | Research DCA main loop | UNTOUCHABLE unless critical bug |
| scalper_engine.py | Research E58 scalper | UNTOUCHABLE control group |
| scalper_v2_engine.py | Research E58v2 velocity | Active development |
| live_long_dca_engine.py | Live DCA trading | Active development |
| live_scalper_engine.py | Live scalper trading | Active development |
| websocket_prices.py | Feeds ALL engines prices | Touch carefully - breaks everything |
| entry_signals.py | All E1-E66 signal logic | Adding or fixing entry methods |
| executor.py | Paper + Live order execution | Adding exchanges or order types |
| database.py | All DB functions | Schema changes |
| api.py | All HTTP endpoints | Adding features |
| classify_coins.py | Coin to category | Changing classification |
| calculate_coin_params.py | Category to DCA/TP params | Changing param logic |
| generate_reports.sh | One command all reports | Adding report type |
| automation/daily_cron.sh | Daily automation | Adding scheduled tasks |
| bot_loop.py | OLD engine NOT in PM2 | DO NOT RUN - replaced |

---

## LIVE BOTS NOW

| Bot ID | Name | Method | Wallet | Engine |
|--------|------|--------|--------|--------|
| 738 | S10 | Live Scalper | id=2 $1000 | live_scalper_engine.py |
| 739 | S25 | Live Scalper | id=3 $1000 | live_scalper_engine.py |
| 745 | E31 DCA | E31 | id=1 $10000 | live_long_dca_engine.py |
| 746 | E31-2 | E31 | id=1 | live_long_dca_engine.py |
| 748 | E54 | E54 | id=1 | live_long_dca_engine.py |

---

## CRON SCHEDULE

- Every hour: fetch_ohlcv.py (OHLCV data collection)
- 03:00 UTC: DB backup + system health
- 03:30 UTC: classify_coins.py (CoinGecko classification)
- 04:00 UTC: calculate_coin_params.py (DCA/TP params)
- 04:30 UTC: rars_scoring.py
- 05:00 UTC: check_paper_timer.py
- After 05:00: generate_reports.sh (all reports to GitHub)
- 17:00 UTC: save_scalper_snapshot.py

---

## USER-FACING FEATURES

### BOT CREATION WIZARD
WHAT: Step-by-step flow for creating a new bot.
WHY: Users need guided setup to configure exchange, wallet, method, and parameters correctly.
FILE: create-bot.html (1399 lines)

SCALPER PATH (7 steps):
- step-0: Bot type selection (DCA or Scalper)
- step-1: Exchange selection
- step-2: Wallet selection or create new wallet
- step-3-scalper: Scalper method selection (S10/S25/etc)
- step-4-scalper: Select variant from research winners
- step-5-scalper: Review + launch
- review-scalper: Confirmation

DCA PATH (10 steps):
- step-0: Bot type selection
- step-1: Exchange selection
- step-2: Wallet selection or create new
- step-3-dca: Direction (Long / Short)
- step-4-dca: Method selection (Smart DCA / ASAP / Mean-Reversion / TradingView)
- step-4b-dca: Coin selection (All / Top X by volume / Custom list)
- step-5-dca: Order settings (base order, entry type, DCA type)
- step-6-dca: DCA settings (spacing, size multiplier, trades per bot, trades per coin)
- step-7-dca: TP settings (TP%, trailing%, profit coin)
- step-8-dca: Reserve floor + auto-resume settings
- review-dca: Summary + launch

WHAT IS CODED: Basic flow exists. Exchange + wallet selection working.
WHAT IS MISSING:
- Short DCA direction not coded in any engine
- Limit order type selection UI exists but not wired to engine
- Profit coin selection (USDT vs base coin) UI exists but not coded in live engine
- Reserve floor settings UI exists but not wired to live engine
- TradingView webhook method not coded
- Bot type validation against exchange minimum order size
STATUS: PARTIAL - basic DCA bot creation works, many settings not wired to engines

---

### BOT STATE MACHINE
WHAT: Each bot has two toggles (Trading ON/OFF · DCA ON/OFF) plus reserve floor protection.
WHY: User needs control over bot behavior without deleting it. Reserve floor prevents overspending.
DESIGNED BEHAVIOR:
- STATE 1 Normal: Trading ON, DCA ON, TP always ON
- STATE 2 Floor Hit (reserve <= floor): Trading OFF, DCA ON, snapshot saved
- STATE 3 Zero Capital: DCA fires when capital available, TP always ON
- STATE 4 Resumed (reserve > threshold): Trading back ON, snapshot restored
- Each bot has independent floor and threshold
- Auto-resume: ON by default
FILES: create-bot.html (step-8-dca UI) | live_long_dca_engine.py (missing)
TABLES: bots.reserve_floor | bots.resume_threshold | bots.auto_resume (need to verify exist)
STATUS: MISSING - UI step exists but engine has no floor/state logic coded
CHANGE IMPACT: live_long_dca_engine.py + virtual_wallets + bots table + Telegram notifications

---

### SHORT DCA
WHAT: User holds a coin, bot sells portions as price rises, buys all back cheaper when price drops.
WHY: Profit from coins user already holds without selling everything at once.
DESIGNED BEHAVIOR:
- User must already hold coin on exchange before creating bot
- Bot sells portions as price rises (widening spacing)
- Avg sell price = weighted average of all sells
- TP triggers when price drops below avg_sell_price - TP%
- Buyback uses limit orders only (reserves USDT on exchange)
- No trailing for Short DCA (fixed limit buyback)
- Profit coin: USDT (keep difference) or base coin (buy more)
FILES: create-bot.html (step-3-dca direction selection)
STATUS: MISSING - UI direction selection exists, NO engine code for short DCA
CHANGE IMPACT: needs new short_dca_engine.py or major live_long_dca_engine.py additions

---

### PROFIT COIN
WHAT: User chooses whether profit is received in USDT or base coin.
WHY: Some users want to accumulate the coin, others want USDT back.
DESIGNED BEHAVIOR:
- Long + USDT: sell all coin, receive USDT
- Long + base coin: sell enough to recover invested USDT, keep profit as coin
- Short + USDT: buy back less coin than sold, difference stays as USDT
- Short + base coin: buy back same USDT value at lower price = more coin
FILES: create-bot.html (step-7-dca) | live_long_dca_engine.py (missing)
TABLE: bots.profit_coin | positions.profit_coin
STATUS: MISSING - UI exists, engine does not implement it
CHANGE IMPACT: live_long_dca_engine.py TP execution + executor.py sell logic

---

### RESERVE WALLET + FEE SYSTEM
WHAT: User pre-funds a reserve wallet. 20% of each winning trade is auto-deducted.
WHY: Averion earns only when user earns. Reserve prevents monthly invoicing.
DESIGNED BEHAVIOR:
- User deposits USDT to reserve via NOWPayments (TRC20/BEP20)
- Minimum top-up $10. New users get $5 free trial credit
- After winning trade: fee = profit x 20% deducted from reserve
- 0% fee accounts: relatives/admin selected only
- Referral: 2.5% of 20% fee goes to referrer reserve forever
- Reserve alerts: <$5 warning | <$2 critical | $0 new positions pause
- Fee transfer to owner wallet: TRC20 when threshold reached (default $10)
FILES: database.py (deduct_performance_fee) | live_long_dca_engine.py (line 345)
TABLES: reserve_wallets | wallet_transactions
STATUS:
- Fee deduction on close: PARTIAL (coded in live_long_dca_engine.py but not verified live)
- NOWPayments top-up: MISSING
- Reserve balance UI for user: MISSING
- Fee transfer to owner TRC20: MISSING
- Referral distribution: MISSING
- Free trial credit: MISSING
CHANGE IMPACT: database.py + live engines + reserve_wallets + legal docs + Telegram alerts

---

### TELEGRAM NOTIFICATIONS
WHAT: User receives real-time alerts about trades, DCAs, reserve balance, and daily reports.
WHY: Users cannot watch dashboard 24/7.
CONNECTION FLOW (designed):
1. Settings → Notifications → Connect Telegram
2. Dashboard shows unique code
3. User sends /connect CODE to @AverionBot
4. All notifications go to one direct chat

NOTIFICATION TYPES CODED IN telegram.py:
- notify_trade_open(): trade opened alert
- notify_trade_closed(): trade closed with PnL
- notify_dca(): DCA level fired
- send_daily_report(): daily summary
- send_weekly_report(): weekly summary
- send_monthly_report(): monthly summary
- send_verification_code(): login verification

WHERE NOTIFICATIONS ARE CALLED:
- research_engine.py: calls notify_trade_open, notify_trade_closed, notify_dca (WORKING)
- live_long_dca_engine.py: NO telegram calls (MISSING)
- live_scalper_engine.py: NO telegram calls (MISSING)

MISSING:
- User Telegram connection UI in settings
- Reserve low/critical/zero alerts
- Bot paused/resumed alerts (state machine)
- ST flag alerts
- Live engine notification calls
FILES: telegram.py | research_engine.py | settings.html
TABLES: users.telegram_chat_id
STATUS: PARTIAL - functions coded, live engines not wired, connection UI missing

---

### DASHBOARD PAGES STATUS

| Page | File | Status | Missing |
|------|------|--------|---------|
| Login | login.html | WORKING | - |
| Register | register.html | WORKING | Public flow not tested |
| Dashboard/Home | dashboard.html | WORKING | Real exchange balance |
| Bots list | bots.html | WORKING | - |
| Bot detail | bot-detail.html | PARTIAL | Action buttons, add funds |
| Trades | trades.html | PARTIAL | Action button not clickable |
| History | history.html | WORKING | - |
| Exchanges | exchanges.html | WORKING | - |
| Create Bot | create-bot.html | PARTIAL | Many settings not wired |
| Settings | settings.html | PARTIAL | Telegram connect missing |
| Admin | admin.html | WORKING | All tabs working |

---

### EXCHANGES SUPPORTED
DESIGNED: 7 exchanges via CCXT
1. MEXC - LIVE NOW (WebSocket + paper trading)
2. Binance - coded in CCXT wrapper, not tested live
3. KuCoin - coded, not tested
4. OKX - coded, not tested
5. Gate.io - coded, not tested
6. Bybit - coded, not tested
7. Bitget - coded, not tested

FILES: exchanges.py (CCXT wrapper) | executor.py
STATUS: MEXC=WORKING | Others=CODED NOT TESTED

---

### USER REGISTRATION + ONBOARDING
DESIGNED FLOW:
1. Register: email + password + referral code (optional, locked at registration)
2. Email verification code sent
3. Dashboard access after verification
4. Connect exchange API keys
5. Create first bot via wizard
6. Top up reserve wallet ($5 free trial credit auto-added)

STATUS:
- Registration form: WORKING
- Email verification: WORKING
- Exchange connection: WORKING
- Bot creation wizard: PARTIAL
- Reserve wallet top-up: MISSING
- Free trial credit: MISSING
- Referral code at registration: CODED (locked, cannot change after)
FILES: auth.py | register.html | login.html | api.py

---

### ADMIN SYSTEM
WHAT: Full admin control panel for platform management.
FILE: admin.html
TABS AND STATUS:
- Health & Control: WORKING (server health, PM2 status)
- Research & Trades: WORKING (all sub-tabs including Scalper V2)
  Sub-tabs: Bots | Trades | DCA Queue | History | Champ RARS | Champ Score | Scalper RARS | Scalper Score | Scalper V2 RARS | Scalper V2 Score | Coin Categories
- Users: WORKING (list, suspend, fee type)
- Platform Stats: WORKING
- Controls: PARTIAL (emergency halt UI exists but not wired to engine)
MISSING:
- Emergency halt wired to bot engines
- Fee collection oversight
- NOWPayments webhook management
FILES: admin.html | api.py (admin endpoints)

