# Locked Decisions

> These decisions are FINAL. Do not re-suggest, re-discuss, or modify without Bader explicitly saying "discuss this decision". AI must respect all decisions below.

---

## Trading Logic

- DCA spacing calculated from LAST BUY PRICE — never average cost
- Market orders are the default for guaranteed execution
- Limit orders available per bot via wizard (entry + DCA)
- Short DCA buyback always uses limit order (reserve USDT)
- Trailing safety (Smart DCA only): if TP% - Trail% < 1% → direct market TP
- NO maximum DCA levels — smart queue handles capital allocation forever
- Bot NEVER stops running — detects new funds within 60 seconds
- Open positions are NOT affected by reclassification (Option A)
- One pair per bot — no duplicate coin on same bot — cross-bot is fine
- Paper stays paper FOREVER — live stays live — NO conversion ever
- Short DCA = spot only — user must already hold the coin — min exchange order size required
- Profit coin = user chooses USDT or base coin — works for both Long and Short
- All slippage handling uses market orders by default · limit orders available per bot setting

## Slippage Handling
- Check order book depth before every DCA
- If available quantity at target price >= $1 minimum → buy at target price
- If available quantity < exchange pair minimum → buy at exchange minimum order size (not $1 · exchanges reject orders below their minimum)
- Never chase price more than exchange minimum above target
- Always executes something when triggered — never stuck waiting

## ST Flag (Exchange Suspended Trading)
- If exchange marks coin as ST → auto sell immediately (market order)
- Do not open new positions on ST coins
- When ST cleared → resume normally
- Telegram alert when ST detected and when cleared
- Works via CCXT on all 7 exchanges
- This is the ONLY forced close — user controls everything else

## Smart Queue
- Score = Loss% divided by USDT required for next DCA
- Higher score = more recovery per dollar = funded first
- ONE DCA per cycle — predictable and auditable
- When TP fires → freed capital → IMMEDIATE rescan
- Queue naturally prevents duplicate DCAs (last buy price always updates)
- Queue naturally handles crash scenarios (capital depletes gradually)
- No special crash detection needed — queue is the protection

## Reclassification
- Reclassification uses percentage-based trigger not fixed price threshold
- No phantom buys possible — percentage from last buy price always moves
- Smart queue handles reclassification correctly
- CoinGecko for market cap classification ONLY
- Exchange data (CCXT) for volume/OHLCV/coin list

## Cap Protection
- Upward: recorded_cap = min(real_cap, previous × 1.10) — max +10% per day
- Downward: recorded_cap = real_cap — full drop recorded immediately
- Protects against fake pumps and market manipulation
- Original idea by Bader

## Data Sources
- Exchange data via CCXT: coin list + 24h volume + OHLCV
- CoinGecko: market cap ONLY for classification — once daily 3am
- Never mixed in same calculation — clean separation
- CoinGecko failure fallback: use last recorded cap — skip reclassification that day

## Business Model
- Performance fee = 20% of realized profits only
- Loss months = $0 fee — no high water mark — no rollover
- Reserve wallet = fee pre-funding only — NOT trading capital
- Reserve wallet uses NOWPayments (0.5% fee) — unique address per user
- Minimum top-up = $10
- New user gets $5 free trial credit
- Reserve alerts: <$5 warning · <$2 critical · $0 new positions pause
- Referral = 3% of 20% fee → referrer reserve wallet — forever
- Referral code entered at registration ONLY — cannot change after
- Regular customers always pay 20% — no discount ever
- 0% fee accounts = relatives/selected by admin only — no reserve needed
- Admin accounts = no fee · no reserve — all income to owner wallet
- Fee transfer threshold = $10 default (admin adjustable in panel)
- Month-end force transfer regardless of threshold
- Transfer to owner wallet via TRC20 (cheapest fees)

## Infrastructure
- Health check every 1 hour (CPU · RAM · Disk · PM2 · trades count)
- 3am cron staggered:
  - 03:00 Infrastructure (CCXT upgrade · restart · backup)
  - 03:30 Data & Classification (CoinGecko · parameters · volume)
  - 04:00 Reporting (snapshot · metrics · Excel · Telegram)
  - 04:30 Sunday only (cleanup · disk · DB VACUUM · weekly report)

## Security
- PAPER_MODE moved to .env file — never in config.py
- Default PAPER_MODE = true always (safe by default)
- 10 second countdown warning when switching to LIVE mode
- Red banner across full topbar in LIVE mode

## Paper Trade Rules
- Paper trades count toward 100 trade limit (shared with live)
- Paper maximum = 30 of 100
- Auto-close ALL paper trades if ZERO live trades for 90 days
- Day 83 warning · Day 89 final warning · Day 90 auto-close
- Timer resets when a NEW live position OPENS (not closes · opening only)

## Dashboard
- Settings tab = account info ONLY — bot config lives in wizard
- Bots tab = flat list — not grouped by exchange
- Exchange badge per row: M=MEXC · B=Binance · K=KuCoin etc
- Two toggles per bot: Trading (new positions) + DCA (averaging)
- Both independent — can mix ON/OFF in any combination

## Decisions From AI Review (May 2026)
- No complex state machine needed — queue + last buy price prevents duplicates
- No special crash detection needed — smart queue is the protection
- Dead coin scenario: ST flag handles it — no forced close otherwise
- Reclassification mid-ladder: not a bug — percentage trigger always correct
- One DCA per cycle: intentional — predictable over speed
- 60 second interval: intentional — DCA swing system not scalping
- High water mark: intentionally excluded — simplicity over complexity

---

## GitHub Repository

- Repo is currently PUBLIC (needed for Claude to fetch docs)
- Switch back to PRIVATE when averionbot.com launches publicly
- Remove GitHub token from all docs at same time
- Both actions happen together on launch day

## Reclassification Effect on Existing Positions (LOCKED)

- Reclassification affects NEW positions only
- Existing open positions keep original parameters forever
- Parameters never change mid-position automatically
- User controls existing positions via Add Funds · Close · Toggle DCA OFF
- Reason: predictable · trustworthy · user always in control

## Recovery Buy System (LOCKED)

- REMOVED from spec
- Smart queue already handles stuck positions naturally
- User has Add Funds for manual intervention
- Queue scores Loss% / USDT = naturally prioritizes stuck positions
- Simpler system = better system

## Paper Mode Virtual Funding (LOCKED)

- Paper trades use UNLIMITED virtual balance
- No artificial funding limits for paper trading
- Abuse prevented by existing rules:
  - Max 30 paper trades per user
  - 90 day auto-close if no live trades
  - Server cost protection built in
- Dashboard shows clearly:
  "PAPER MODE — Virtual funds unlimited
   Switch to live trading to use real funds"
- Purpose: testing · research · learning bot behavior

## Exchange Minimum Order Rules (LOCKED)

- Bot creates normally — no blocking at wizard
- Trading holds per coin if minimum not met
- Bot settings page shows error section:
  - Active coins · Pending coins (needs funds) · Cannot trade coins
  - Each with reason and suggested fix
- Add Funds: blocks if amount < exchange minimum
- Short DCA two-way calculation:
  - User sets TP% → system calculates minimum quantity needed
  - User sets quantity → system calculates minimum TP% needed
  - Live feedback shown before saving
  - Dashboard warning if current settings cannot meet minimum



## Multi-Exchange Bot Behavior (Point 8 — LOCKED)

- One bot tied to one exchange only
- Multiple bots allowed per exchange (e.g. 10 bots on MEXC)
- Each bot has its OWN smart queue
- Capital isolated per bot via Virtual Wallet System

## Virtual Wallet System (NEW FEATURE — LOCKED)

- User creates named virtual wallets per exchange
- Example: "Long Test 1" · "Short BTC" · "RVN Wallet"
- Each wallet links to exchange balance (fixed $ or "All")
- Bot links to one wallet at creation (changeable anytime)
- Same wallet = shared queue + shared capital between bots
- Different wallet = completely isolated queue + capital
- Wallets visible in new Wallets section per exchange
- Bot creation wizard Step 2.5: Select or Create Wallet
- Solves: short bot isolation · capital sharing · queue control
- No other trading platform has this feature — unique to Averion

## Short DCA Lifecycle (Point 9 — LOCKED)

- Full worked example added to 03_TRADING_SYSTEM.md
- User must hold coin before opening Short DCA
- Bot sells portions as price rises (widening spacing)
- Avg sell price calculated from all sells combined
- TP triggers when price drops below avg sell price - TP%
- Trailing arms then fires on TRAIL% pullback
- Buy back uses collected USDT only
- Profit = difference between avg sell and buy back price
- Profit coin: USDT (keep difference) or base coin (buy more)

## Bot Deletion Behavior (Point 10 — LOCKED)

- Bot has 0 open positions:
  - Shows [Delete Bot] button only
  - Clean delete · no warning needed

- Bot has open positions:
  - Shows [Close All and Delete] button
  - Click shows warning modal with:
    - Count of positions
    - Estimated P&L per position (green/red)
    - Net total P&L (green/red)
    - Cannot be undone warning
  - [Cancel] [Close All and Delete]
  - Market orders close all positions
  - Bot deleted after all closed

## External Service Outages (Point 11 - LOCKED)

- CoinGecko down: use last recorded cap · skip reclassification · retry next 3am
- Telegram down: bot continues trading · alerts queued · max 50 queued · send when recovered
- NOWPayments: DB log all deposits (not Excel) · admin can export to Excel anytime
  - Table: reserve_deposits (user_id · amount_sent · amount_received · network · tx_hash · status · timestamps)
  - Admin panel shows deposit log with Match button for unknown deposits
  - Admin can export full log to Excel anytime
- Exchange API down: CCXT retries with exponential backoff · after 5 fails → Telegram alert
  - Pause that exchange only · other exchanges continue · auto-resume when recovered
- Bot NEVER stops for any external service failure

## Exchange API Key Rules (LOCKED)

- IP whitelist reminder shown when user adds API key
- Server IP displayed prominently in admin panel Tab 5
- Reminder shows which exchanges require IP whitelist:
  - Binance · OKX = required
  - KuCoin = recommended
  - MEXC · Gate.io · Bybit · Bitget = optional
- User must confirm IP whitelisted before saving key
- Bot detects API key rejection → Telegram alert → exchange paused
- Some exchanges expire keys after 90 days → bot detects → alerts user

## Data Retention Policy (Point 12 - LOCKED)

- Trade history: FOREVER (tax records · research needs full history)
- OHLCV hourly: 90 days rolling (older compressed to daily summary)
- Daily summaries: FOREVER (tiny storage · long term analysis)
- Research decisions: FOREVER (never repeat failed experiments)
- Balance history: FOREVER (all time chart for users)
- Telegram logs: 30 days (Sunday cleanup cron handles this)
- Error logs: 30 days (Sunday cleanup cron handles this)
- Deposit logs: FOREVER (financial records · dispute resolution)

## Monetization & Bot Limits (LOCKED)

### Free Tier
- 5 bots included free forever
- 100 trades open maximum (hard limit always)
- 100 trade bundle per month included
- 1 exchange connection
- 20% performance fee on profits

### Paid Additions (from reserve wallet)
- Extra bots: $1 per bot per 30 days
- Extra trade bundles:
 - 200 trades: $3/month
 - 500 trades: $5/month
 - 1000 trades: $8/month
 - Unlimited: $15/month
- All deducted automatically 1st of every month
- Performance fee deducted per winning trade (ongoing)

### Auto-Deduction Rules
- 1st of month: bot fees deducted first · trade bundle second
- If reserve insufficient:
 - Deduct what is available
 - Last created bot turns OFF automatically
 - Existing positions on expired bot continue to TP
 - No new positions on expired bot
 - Telegram alert sent immediately
- No grace period for monthly fee shortage
- Manual renewal always — never automatic

### Bot Slot System
- Free slots: 5
- Paid slots: however many purchased
- Active bots cannot exceed total slots
- User turns off one bot → slot freed → another bot can activate
- Last created bot expires first when slots exceeded
- Expired bot shows in dashboard: EXPIRED · renew to open new positions

### Trade Limit Rules
- 100 open trades hard limit — always — regardless of bundle
- Bundle = how many can be opened this month total
- When one closes → new one can open (within limit)
- Dashboard shows: Open 67/100 · Bundle used 234/500

### API Key Abuse Prevention
- Exchange UID fingerprint captured on API key creation
- Same UID cannot be added twice (anti-fraud Layer 2)
- Prevents free bot limit bypass via multiple API keys
- Cannot bypass without creating entirely new exchange account (requires exchange KYC)

## Concurrent Bot Limits (Point 13 - LOCKED)

- 5 bots free TOTAL across all exchanges (not per exchange)
- Prevents abuse: 10 exchanges would give 50 free bots if per-exchange
- Extra bots: $1 per bot per month from reserve wallet
- Server load = total bots regardless of exchange
- Price fetching shared across all bots on same exchange = efficient
- No hard technical API rate limit issue with current architecture

## Customer Telegram Channels (LOCKED)

- ONE direct chat with @AverionBot — not separate channels
- Old 3-channel design removed — Option C confirmed permanently
- See "Customer Telegram Setup" section for full details
- Message types: TRADE · ALERT · REPORT — all in one chat
- Customer toggles each type ON/OFF independently

## Daily Telegram Report Per Exchange (LOCKED)

Format:
🌙 Averion Daily Report — Date
📊 Exchange Name
Capital: $X
Open trades: X
Closed today: X
Profit today: +$X
Fees due: $X
Available funds: $X
🤖 System: CPU% · RAM% · All exchanges ✅

## PWA Install Hint (LOCKED)

- Detect if user is in browser vs installed PWA
- Browser + not dismissed → show weekly hint:
  "💡 Add Averion to home screen for app experience
   [How to do it] [✓ Don't show again]"
- Dismissed → never show again (localStorage)
- PWA detected → never show hint
- Simple JavaScript matchMedia check

## Manual Bot Type (LOCKED)

- Separate bot type: Manual
- User picks specific coins manually
- Not affected by Smart DCA automation
- Has own virtual wallet
- Allows second position on same coin
  (Manual bot + Smart bot can both hold RVN)
- Research data kept separate from auto bots
- Available in bot creation wizard Step 2

## Virtual Wallet System (LOCKED)

- See full definition above in "Virtual Wallet System (NEW FEATURE)"
- Same wallet = shared queue + shared capital
- Different wallet = isolated queue + capital
- Wallets section shown per exchange in dashboard
- Bot creation wizard Step 2.5: Select or Create Wallet

## Entry Method Promotion Formula (Point 7 - LOCKED)

Validated by ChatGPT · Gemini · DeepSeek independently.

### Normalization (all components to 0-1 first)
- WR_norm = Win Rate (already 0-1)
- AP_norm = (profit - min) / (max - min)
- RS_norm = inverted: 1/(recovery_hours+1) then normalized
- DD_norm = 1 - drawdown% (lower drawdown = higher score)
- Floor: max(drawdown, 0.01) to prevent division by zero

### Scoring Formula
Score = (WR_norm^0.30) x (AP_norm^0.20) x (RS_norm^0.15) x (DD_norm^0.35)

### Weights Rationale
- Drawdown 35%: survivability first - matches Averion philosophy
- Win Rate 30%: DCA relies on consistency
- Avg Profit 20%: reward but not chase profit
- Recovery Speed 15%: capital efficiency tiebreaker

### Formula Adjustment Feature
- Admin can adjust weights via sliders in Tab 4
- Weights must always total 100%
- System recalculates ALL historical scores on change
- Old ranking saved for comparison
- 30 day cooldown between weight changes
- Enables regime-specific tuning (bull/bear markets)

### Promotion Rules
- Minimum 100 closed trades before scoring
- Below 30 trades: score = 0 · not eligible regardless of win rate
- 30-99 trades: score calculated but marked PROVISIONAL · cannot promote
- 100+ trades: full promotion eligibility
- Tested across 3+ market regimes
- Score beats E10 control group (promotion score must be > E10 score)
- Score beats Simple DCA benchmark (promotion score must be > Simple DCA score)
- "Beat" = higher normalized promotion score · not just higher return
- 30 day cooldown after any parameter change

### Deletion Rules
- 3 consecutive quarterly reviews failed
- Win rate below 40% consistently
- Underperforms E10 control group

## Research Bot Monthly Elimination Rule (LOCKED)

- Monthly quick check — NOT parameter adjustment
- Eliminate ONLY bots with zero trades in 30 days
- Reason: signal too strict → never triggers on any coin
- Replace eliminated bot with looser variation of same method
- Do NOT eliminate bots with few trades — only zero trades
- Full 6 month review still applies for promotion/deletion
- This prevents server resources wasted on untriggerable bots

## 5 Benchmark Bots — Purpose (LOCKED)

- BTC Buy and Hold: pure market exposure baseline
- ETH Buy and Hold: alternative market exposure
- Simple DCA ASAP: tests if waiting for signal adds value
- Random Entry DCA: tests if signals beat pure luck
- Static Spacing DCA: tests if widening spacing adds value

All 10 entry methods must beat relevant benchmarks
to be considered for Smart DCA promotion.
If methods lose to Random Entry = signals are noise.
If methods lose to BTC Hold = wrong market regime.

## Smart Queue Tie-Breaker (LOCKED)

When two positions have identical scores (Loss% / USDT required):

Step 1: Highest loss $ amount wins
- Position with bigger absolute loss funded first
- Closing bigger loss = better recovery for customer
- More capital freed when TP eventually fires

Step 2: If still equal → oldest position wins
- Position open longest gets priority
- Simple · deterministic · fair
- Easy to implement and audit

## Partial Liquidity DCA Handling (LOCKED)

When DCA triggers but full amount not available:

1. Buy whatever available immediately (market order)
2. Recalculate avg cost and TP target after every partial buy
3. Remaining amount goes to STANDBY — not back to queue
4. Standby monitors price only — fires when price reaches same DCA level again
5. Standby does NOT compete with queue — completely separate system
6. Queue continues normally for other coins while RVN is in standby
7. When price reaches DCA level again → standby buys remaining
8. If remaining < exchange minimum → add to next DCA level amount
9. After standby complete → position returns to normal queue
10. Each partial buy recorded as separate trade for full audit trail

## API Key Expiry Flow (LOCKED)

Step 1: Bot detects API rejection (CCXT auth error)
- Exchange marked PAUSED in DB
- Telegram Alerts: MEXC API key rejected · action required
- Dashboard: red banner · API KEY INVALID · [Update API Key] button

Step 2: User updates API key in Settings
- Bot tests connection automatically
- If valid → exchange resumes immediately

Step 3: Auto-resume on reconnection
- Bot fetches current prices immediately
- Any TP that triggered during downtime → fires immediately
- Any DCA that triggered → enters queue normally
- Everything resumes automatically — no manual intervention
- 60s loop continues as normal

Step 4: If user never fixes (rare)
- Positions stay paused · shown in dashboard
- Telegram reminder every 24 hours
- After 7 days: reminder to close positions manually on exchange
- Admin can mark positions closed if needed
- Nothing forced ever

## API Disconnection Auto-Archive (LOCKED)

If exchange never reconnects:
- Day 1: Telegram alert + dashboard red banner
- Day 7: Warning to close positions manually on exchange
- Day 30: Strong warning · monthly alerts begin from here
- Monthly: reminder sent every 30 days
- Month 6: Monthly reminder + "6 months disconnected" warning
- Month 12: Monthly reminder + "Account will be archived in 30 days"
- Day 365: Auto-archive all positions
  - Status changed to EXPIRED
  - Removed from active dashboard
  - Kept in History tab forever (tax records)
  - Telegram final notice sent
  - DB cleaned · no data deleted
- Reason: safety net for edge cases
  (hospitalized · abandoned account · lost access)
- Monthly alerts prevent user being surprised at day 365

## Performance Fee Calculation (LOCKED)

- Performance fee = 20% of NET profit (after exchange trading fees)
- Formula: Net Profit = Exit Value - Entry Cost - Exchange Fees
- Performance Fee = Net Profit x 20%
- Exchange fees tracked per order via CCXT (fee.cost field)
- All fees summed across entry + DCAs + TP sell
- Fairer to customer · transparent · builds trust
- Small difference in practice but correct approach

## Short DCA Buyback — Limit Order Exception (LOCKED)

Short DCA is the ONLY exception to market orders rule:
- Sells: market orders (immediate execution)
- Buyback: limit order (reserves USDT on exchange)

Why limit order for buyback:
- USDT from sells must be reserved on exchange
- Prevents queue from using Short funds for Long DCAs
- Exchange holds USDT → guaranteed buyback when price drops
- No trailing needed → fixed limit price = exact profit target

After every Short DCA sell:
1. Receive USDT from market sell
2. Cancel previous limit buy order (if exists)
3. Recalculate new avg sell price + new TP target
4. Place new limit buy order at new TP target price
5. Exchange reserves exact USDT needed
6. Queue cannot touch reserved funds

Timing Protection Rule:
- When Short DCA sell executes → flag: PENDING_BUYBACK
- Long DCA bots sharing same Virtual Wallet on same exchange → HOLD new DCAs
- Hold lasts until limit buy order confirmed by exchange (~2 seconds)
- Then Long DCA resumes normally
- Prevents queue grabbing Short funds during placement delay

Priority Order (same exchange · same wallet):
1. Short DCA buyback (always first)
2. TP exits (free capital immediately)
3. Long DCA queue (normal scoring)

## Reserve Wallet Debt System (LOCKED)

- Position closes at profit → fee calculated (profit × 20%)
- Reserve has enough → fee deducted immediately ✅
- Reserve empty or insufficient → fee recorded as debt

### When debt exists (even $0.01):
- Bot remains ON — status never changes
- NO new positions open — zero new trades fire
- Existing open positions continue normally to TP
- Dashboard shows debt in RED with [Top Up Now] button
- Telegram alert sent immediately when debt created
- Telegram reminder every 7 days while debt unpaid

### When user tops up:
- Debt deducted first automatically
- Remaining amount = new reserve balance
- New positions resume automatically — no manual action needed
- Telegram: debt cleared · balance shown · trading resumed

### Rules (LOCKED):
- Even $0.01 debt = no new positions · no exceptions
- Bot status stays ON — user never needs to restart
- No debt write-off ever — must be paid in full
- No maximum debt limit
- 0% fee accounts (family/admin): no fees · no debt · no reserve needed
- Debt history kept FOREVER (financial records · tax · disputes)
- Active unpaid debt kept forever until paid

## CoinGecko Rate Limiting Solution (LOCKED)

- Use /coins/markets endpoint (250 coins per call)
- Fetch ALL coins dynamically - not limited to 1870
- New coins appear automatically in next batch
- Process: fetch page 1 · page 2 · page 3 · until empty page returned
- Empty page = all coins fetched · stop automatically
- Free tier: 50 calls/minute · well within limit
- Parameters: vs_currency=usd · per_page=250 · page=N
- Never call individual /coins/{id} endpoint
- Dynamic · scalable · always complete

## Smart Queue Cycle Definition (LOCKED)

- One cycle = one 60 second price check loop
- ONE DCA executed per cycle maximum
- When TP fires mid-cycle:
  - Capital freed immediately
  - Queue rescores immediately
  - Next DCA waits for next 60s cycle
  - Never two DCAs in same 60s window
- Maximum DCA rate = one per 60 seconds
- Predictable · auditable · never chaotic

## Server Clock Sync (LOCKED)

- Install chrony on Hetzner Day 1
- Syncs with multiple NTP servers automatically
- Prevents clock drift that causes exchange API rejections
- Ubuntu 24.04 has systemd-timesyncd by default
- Chrony provides better accuracy for trading systems
- One install · runs forever · never needs attention

## Dust Accumulation Handling (LOCKED)

- After every TP sell: check remaining coin balance
- If remaining < exchange minimum order size = dust
- Dust marked in DB · excluded from calculations
- Shown in dashboard: Dust: 0.00003 BTC
- Weekly Sunday cron: attempt to sell each coin's dust individually (NOT combined)
  - If total dust value >= minimum order → sell
  - If still too small → ignore · keep in dashboard
- Dust never causes errors · never blocks calculations
- Small cosmetic issue only · handled gracefully

## NOWPayments Webhook Reliability (LOCKED)

Three layer system:

Layer 1 — Webhook (primary · instant)
- NOWPayments fires webhook → credit user immediately
- payment_id saved to DB · status = CREDITED

Layer 2 — Hourly polling (fallback)
- Every hour: check NOWPayments API for last 24h payments
- Compare against DB · any missing payment_id → credit now
- Catches all missed webhooks automatically

Layer 3 — Admin manual reconciliation
- Admin deposit log shows ALL payments sorted by newest
- Status per payment: Credited · Pending · Unknown · Failed
- [Match] button for unknown deposits (no user match)
- [Credit Manually] button for stuck payments
- [Export Excel] for full records

Duplicate Protection:
- Check payment_id exists in DB before every credit
- If exists → skip · if not exists → credit
- Never double-credits under any circumstance

## ST Flag — Entry Check + Exit Rule (LOCKED)

Before entering ANY new position:
- Check ST flag for that coin
- If ST active → skip · do not enter
- Move to next qualifying coin
- Telegram alert: coin skipped due to ST

During open position:
- ST detected → auto sell immediately (market order)
- No exceptions · even at significant loss
- Reason: some money better than nothing
- Coin may become permanently untradeable
- Telegram alert: position closed · ST detected · P&L shown
- Capital freed → queue rescores immediately

## Smart Queue Insufficient Funds Behavior (LOCKED)

Queue never blocks on insufficient funds:
- Score all positions by Loss% / USDT required
- Attempt to fund #1 highest score
- If insufficient funds → SKIP · move to #2
- Attempt #2 · if insufficient → SKIP · move to #3
- Continue until funded position found or list exhausted
- Execute best affordable position
- Remaining positions retry next 60s cycle
- Capital always deployed to best available option
- Never idle when something can be funded
- Low balance Telegram alert when NO position can be funded

## OHLCV Data Gap Handling (LOCKED)

New coins under 90 days:
- Handled by confidence tier system already
- Under 30 days = category defaults
- 30-90 days = blend own data + defaults
- Over 90 days = fully own data

Missing candles from exchange outage:
- Skip missing candles in ATR calculation
- Never fake or interpolate data
- Use available candles only
- Gap fills automatically next hourly fetch
- If gap over 24 hours → admin Telegram alert
- Bot continues trading with available data
- Minor accuracy impact only · self-correcting

## Customer Telegram Setup (LOCKED)

One direct chat with @AverionBot — professional and simple.
No separate channels needed — ever.

Connection flow:
1. Settings → Notifications → [Connect Telegram]
2. Dashboard shows unique code: /connect ABC123XYZ
3. Customer opens Telegram → finds @AverionBot
4. Sends: /connect ABC123XYZ
5. Bot confirms connection
6. All notifications go to one direct chat

Message format — clearly labeled:
- 🟢 TRADE: every buy · sell · DCA · TP
- 🔴 ALERT: reserve low · ST flag · errors · urgent
- 📊 REPORT: daily · weekly · monthly summaries

Customer controls in Settings:
- Toggle each message type ON/OFF independently
- Alerts recommended always ON
- Customer can mute bot in Telegram if needed

Why Option C is correct permanently:
- One chat = everything in one place
- Professional · clean · simple
- No multi-channel complexity ever
- WhatsApp Business and best Telegram bots use this approach

## Short DCA Spacing Formula (LOCKED)

Reference price: price at bot activation (not avg hold price)
Direction: rises instead of drops (mirrors Long DCA)

Trigger formula:
- Level 1: activation_price x (1 + DCA%)
- Level 2+: last_sell_price x (1 + DCA% x spacing_multiplier^level)
- Mirrors Long DCA geometry exactly — just direction reversed

Order types (LOCKED):
- Sell orders: MARKET (immediate execution always)
- Buyback order: LIMIT (reserves USDT on exchange)

After every market sell:
1. Update last_sell_price
2. Cancel previous limit buy order
3. Recalculate avg_sell_price (weighted average of all sells)
4. Recalculate TP target = avg_sell_price x (1 - TP%)
5. Place new limit buy at TP target price
6. Exchange reserves exact USDT needed for buyback

TP formula for Short DCA:
- TP target = avg_sell_price x (1 - TP%)
- Price drops to TP target → limit buy fills
- Profit = total USDT collected - total USDT spent on buyback

## CCXT Version Management (LOCKED)

- Never blind auto-upgrade on live server
- Safe automated upgrade process:

Step 1: Weekly check for new CCXT version
Step 2: If new version found:
  - Install in temporary virtual environment only
  - Run 5 validation tests:
    1. Fetch live price from MEXC
    2. Fetch order book
    3. Fetch account balance
    4. Fetch OHLCV data
    5. Parse order response format
Step 3: All tests pass → upgrade main installation → restart bot
Step 4: Any test fails → stay on current version → retry next week
- Telegram notification after every attempt (pass or fail)
- Fully automatic · zero manual intervention needed
- Never breaks live bot · always tested before applying

## Attention Log — Customer Dashboard (LOCKED)

Top section of Bots tab — hidden when empty.
Appears automatically when any item needs attention.

Severity levels:
- Red: action required (checkpoint · API expired · ST flag · reserve empty)
- Yellow: awareness only (standby active · low volume · exchange paused)
- Green: auto-resolved info (CCXT upgraded · exchange reconnected)

Items shown in log:
- DCA checkpoint reached → [Continue] [Pause] [Sell Now]
- Reserve wallet low/empty → [Top Up]
- API key expired → [Update Key]
- ST flag detected → [View Position]
- Standby active (partial DCA waiting) → [View] [Cancel]
- Dead coin detected → [View Position]
- Low volume warning → [View Position]
- Delisted coin → [Mark Closed]
- Exchange paused → [Update Key]

Behavior:
- Empty = section completely hidden
- Items exist = section shows at top of Bots tab
- User resolves item = disappears from log
- All resolved = section hidden again
- Clean · not annoying · always visible when needed

Also sent to Telegram for critical items
Dashboard is primary · Telegram is secondary

## Base Coin Selection (LOCKED)

- User selects quote currency at bot creation: USDT or BTC
- USDT bot: trades RVN/USDT · BTC/USDT · ETH/USDT etc
- BTC bot: trades RVN/BTC · ETH/BTC etc
- User must have selected base coin on exchange
- Bot checks base coin balance before every trade
- Cannot mix: one bot = one base currency always
- Shown clearly in bot creation wizard Step 3

## Position Price Bar — Live View (LOCKED)

- Every open position shows live progress bar
- Bar displays three markers:
  - Current price (live · updates every 60s)
  - Next DCA trigger price
  - TP target price
- Visual indicator: how close to DCA or TP
- Shown in: Bots tab position row + Position detail screen

## Position Detail Screen (LOCKED)

- Each position has unique ID number
- Click any position → opens detail screen
- Shows:
  - Position ID · Coin · Exchange · Bot name
  - Current price · Avg cost · Quantity
  - Total invested · Unrealized P&L
  - Progress bar (Current · Next DCA · TP)
  - Full DCA history table:
    - Each DCA: level · timestamp · price · amount · quantity
  - Total funds in this trade
  - Total coin quantity accumulated
  - Entry method used

## Telegram Notifications — Final (LOCKED)

- ONE chat with @AverionBot — Option C confirmed permanently
- User toggles each message TYPE on/off independently

Message types:
- Trade notifications: every buy · DCA · sell · TP
  (toggle ON/OFF — high volume · many mute this)
- Alert notifications: reserve low · API expired · ST flag
  (one alert per event · never repeated · never annoying)
- Daily report: closed trades count · profit · fees
- Weekly report: total profit in USDT + coins
- Monthly report: full summary

Settings tab shows:
- Connected: @AverionBot ✅
- Trade notifications: [ON/OFF]
- Alert notifications: [ON/OFF]
- Daily report: [ON/OFF]
- Weekly report: [ON/OFF]
- Monthly report: [ON/OFF]

## Short Bot Partial Holdings — Standby (LOCKED)

- User sets bot to sell 100 RVN
- Exchange only has 50 RVN available
- Bot shows hint: "Only 50 RVN available · waiting for more"
- Bot sells available 50 RVN immediately
- Standby activates: waiting for remaining 50 RVN
- When user receives 50 more RVN → bot resumes immediately
- Same standby system as partial DCA liquidity
- No manual action needed · fully automatic

## Reserve Wallet Debt Display (LOCKED)

- Position closes at profit · fee = $5 · reserve = $0
- Dashboard shows: Fees due: -$5.00 (red)
- User deposits $10:
  - Debt $5 deducted first automatically
  - Remaining $5.00 shown as balance
  - Telegram: "Reserve topped up · $5 debt cleared · $5.00 remaining"
- Debt shown clearly in red until cleared
- Never hidden · always transparent

## Paper Trade Timer Reset (LOCKED)

- Timer resets when live trade OPENS only
- Closing a live trade does NOT reset timer
- Only OPENING a new live trade resets 90-day counter
- Reason: user could close last live trade on Day 89
 and never open another — timer would reset incorrectly

## Short DCA Balance Check (LOCKED)

- Check coin balance on exchange before EVERY Short DCA sell
- If balance insufficient → standby system activates
- Telegram alert: insufficient balance for Short DCA sell
- Attention log: warning shown in dashboard
- Bot waits for sufficient balance automatically
- No manual action needed

## Database Backup Strategy (LOCKED)

- Daily 3am: pg_dump → /home/averion/backups/
- Filename: averion_YYYY-MM-DD.sql
- Keep last 7 days only (auto-delete older)
- Phase 4: local backups sufficient for personal use
- Phase 6: add Hetzner Volume 10GB at €0.48/month
 for off-disk disaster recovery before public launch
- Telegram alert if backup fails

## MAX_COINS Production Assertion (LOCKED)

- MAX_COINS = 100 exists in Replit only (memory limit)
- Remove MAX_COINS completely on Hetzner Day 1
- Add startup assertion in main.py:
 If MAX_COINS set AND PAPER_MODE=false → refuse to start
 Error message: Remove MAX_COINS before going live
- Prevents silent coin limit in production
- Already in DAY1_CHECKLIST.md as reminder

## Unconfirmed Order Reconciliation on Startup (LOCKED)

- On every PM2 restart or bot startup:
 1. Fetch last 100 orders from each exchange via CCXT
 2. Compare against DB trades table
 3. Any order on exchange NOT in DB → insert as trade
 4. Any DB trade marked pending → verify with exchange
 5. Fill all gaps before resuming queue
- Prevents: mid-trade PM2 crash losing order confirmation
- Takes approximately 5 seconds on startup
- Critical for data integrity with real money

## Exchange Passphrase (LOCKED)

- KuCoin · OKX · Bitget require 3 credentials:
  API Key · API Secret · API Passphrase
- Passphrase stored encrypted in exchanges.passphrase_enc
- User enters passphrase when adding exchange in settings
- CCXT uses all 3 credentials for authentication
- MEXC · Binance · Gate.io · Bybit = no passphrase needed

## Dashboard Login Brute Force Protection (LOCKED)

- Track failed login attempts in Redis per IP
- 5 failures in 15 minutes → 30 minute cooldown
- Admin can clear blocked IPs in admin panel
- Applies to both user login and admin login
- Telegram alert to admin when IP blocked

## Subscription Billing History (LOCKED)

- Every monthly deduction recorded in subscription_billing table
- Columns: user_id · billing_date · bot_fee · bundle_fee · total
- Records which bots affected when insufficient reserve
- Used for: billing disputes · audit trail · admin reporting
- Never deleted — financial records forever

## Standby System — No Timeout (LOCKED)

- Standby has NO timeout — waits forever
- standby_timeout_at column renamed to standby_created_at in DB (audit only · never used as timeout)
- Two exit conditions only:
  1. Price returns to DCA level → fills remainder
  2. Position hits TP → standby cancelled automatically
- Partial fill accumulation:
  - $2 filled + $7.50 standby = $9.50 total
  - Remaining $0.50 < minimum → added to next DCA level
- No user configuration needed for timeout
- TP always handles final exit naturally

## DCA Checkpoint — TP Always Wins (LOCKED)

- Bot NEVER pauses for checkpoint
- TP always runs regardless of checkpoint state
- Checkpoint behavior:
  - Position reaches configured DCA level
  - DCA turns OFF automatically at checkpoint
  - Attention log shows warning with cost hint
  - TP continues running normally
  - If price rises to TP → sells immediately ✅
- User can turn DCA back ON manually:
  - Shows hint: next DCA cost + trigger price
  - [Turn DCA ON for this level] button
  - User decision always — never forced
- Core principle: TP is the goal · DCA is optional

## Short DCA Implementation Priority (LOCKED)

- Short DCA = Phase 5 feature (not Day 1)
- Day 1 Hetzner: focus on Smart DCA + 10 entry methods
- Server capacity testing comes first
- Continue revenuebot.io for Short DCA meanwhile
- Short DCA proven concept: same as 3commas · revenuebot.io
- Limit order for buyback = correct and necessary
  Without it: Long DCA queue steals Short funds
- Minimum 100 paper Short trades before any live Short
- Test on MEXC first (already familiar exchange)

## PM2 Startup Sequence (LOCKED)

- hetzner_day1.sh: sleep 5 after PostgreSQL starts
- main.py startup sequence:
  1. Wait for PostgreSQL ready (retry every 5s · max 60s)
  2. Wait for Redis ready (retry every 3s · max 30s)
  3. Run unconfirmed order reconciliation
  4. Start bot loop only after all services ready
- If DB not ready after 60s: log clear error · exit · PM2 retries
- Admin dashboard shows: startup status per service

## Admin Dashboard Startup Status (LOCKED)

Shows real-time service status on startup:
- PostgreSQL: ✅ Running / ❌ Not Running
- Redis: ✅ Running / ❌ Not Running  
- Bot Loop: ✅ Running / ⏳ Starting / ❌ Stopped
- Last Reconciliation: timestamp
- CCXT Version: current version
- All shown with professional colored indicators
- Same style as rest of dashboard (dark theme)

## Short DCA Limit Order Auto-Recovery (LOCKED)

Problem: User accidentally cancels limit buyback on exchange
Bot detects: limit order no longer exists on exchange

Recovery flow:
1. Hourly check: verify all Short DCA limit orders still active
2. If limit order cancelled/missing on exchange:
   → Flag position: BUYBACK_MISSING
   → Check available USDT in wallet
   → If USDT available: place new limit order immediately
   → If USDT gone (stolen by Long DCA queue):
     · Set same exchange Long DCA bots: HOLD
     · Telegram alert: Short buyback recovering
     · Wait for next Long DCA TP to free capital
     · When capital available: place limit order
     · Release Long DCA HOLD
3. Attention log: shows recovery status
4. User can also press [Force Recover] button

## Limit Order Monitoring (LOCKED)

All limit orders checked every hour:
- Short DCA buyback orders
- Any other limit orders (future features)
- If missing on exchange → auto-recovery triggered
- Uses CCXT fetchOrder() to verify status
- Cross-references with DB short_buyback_orders table

## Platform Approach (LOCKED)

- Build public-ready from Day 1 — not personal then upgrade
- No technical debt from "personal first" approach
- Server starts small (CX23) · scales with users
- Admin dashboard monitors capacity · easy upgrade path

## Day 1 Exchange Priority (LOCKED)

- MEXC: Long DCA (primary test exchange)
- KuCoin: Long DCA (Bader actively trades here)
- Both exchanges needed from Day 1
- KuCoin requires passphrase_enc (already in schema)
- Short DCA: Phase 5 (MEXC first · then KuCoin)

## Virtual Wallet — Day 1 Feature (LOCKED)

- Virtual wallet system built from Day 1
- Not Phase 5 · not deferred
- Reason: build once · build right · public platform
- Every bot assigned to a wallet from creation
- Default wallet created automatically per exchange
- User can create named wallets anytime
- No migration needed later

## Daily Cron Schedule — Final (LOCKED)

03:00 — Infrastructure
- Check CCXT version number only · log if update available
- Full CCXT upgrade runs Sunday 05:30 only (not daily)
- pm2 restart averion
- PostgreSQL backup → /backups/averion_YYYY-MM-DD.sql
- Keep last 7 days · delete older
- Telegram admin: "Daily maintenance started"

03:30 — CoinGecko Fetch
- Fetch all coins market caps (250 per call · dynamic)
- Store raw caps in coin_history (source: coingecko)
- No classification yet · raw data only

04:00 — CoinMarketCap Fetch
- Fetch all coins market caps from CMC API
- Store raw caps in coin_history (source: cmc)
- No classification yet · raw data only

04:30 — Classification
- Average: recorded_cap = (CoinGecko + CMC) / 2
- If only one source: use that source
- If both fail: use last recorded · Telegram alert
- Apply cap protection formula
- Classify all coins into categories
- Reclassify changed coins · Telegram alert per change
- Update coin_history with final recorded_cap + category

05:00 — Reporting
- Generate Excel report (9 sheets · fresh classification)
- Update metrics/latest.json → push to GitHub
- Send daily Telegram to admin (health + stats)
- Send daily Telegram to each customer (their summary)
- Save report to /reports/ folder

05:30 — Sunday Only
- DB VACUUM + ANALYZE
- Delete logs older than 30 days
- Delete Excel reports older than 30 days
- Disk space check → alert if >70%
- Weekly Telegram summary (profit + fees + rankings)
- Check CCXT version → safe upgrade if available

## Dashboard vs Cron (LOCKED)

Dashboard: live data · updates every 60 seconds
- Prices from Redis (updated every 60s from exchanges)
- Positions from PostgreSQL (updated after every trade)
- P&L calculated live · always accurate
- No dependency on cron schedule

Cron: daily batch processing at 3am-5:30am
- Classification · reports · maintenance
- Does NOT affect dashboard live accuracy
- Two completely independent systems

## Admin Dashboard Cron Control (LOCKED)

Admin dashboard shows live cron status:
- Each step: ✅ Complete · ❌ Failed · ⏳ Running · — Skipped
- Last run time · duration · records processed · errors
- [Re-run] button per step — triggers immediately
- [View Logs] button per step — shows full output

Re-run behavior:
- Runs that specific step only
- Uses latest available data
- Updates status live with spinner
- Admin can re-run any step independently
- Example: CoinGecko failed → re-run CoinGecko
  → then re-run Classification
  → then re-run Reporting

Steps shown:
1. Infrastructure (03:00)
2. CoinGecko Fetch (03:30)
3. CoinMarketCap Fetch (04:00)
4. Classification (04:30)
5. Reporting (05:00)
6. Sunday Cleanup (05:30 · Sunday only)

All steps visible · all independently re-runnable
No need to wait for next day if any step fails

## Admin Dashboard Log Copy Button (LOCKED)

- Every log output has [Copy] button
- One click copies full log to clipboard
- User pastes to Claude/ChatGPT for debugging
- No screenshots needed · no typing errors
- Applies to: cron logs · error logs · trade logs
- Available in: admin dashboard · attention log

## Standalone Component Architecture (LOCKED)

Each component fails independently:
- CoinGecko down → CMC covers · no platform impact
- CMC down → CoinGecko covers · no platform impact
- Both down → last recorded caps · Telegram alert
- Telegram down → alerts queue in DB · retry hourly
- Redis down → bot reads PostgreSQL directly (slower)
- Backup fails → Telegram alert · bot continues
- CCXT upgrade fails → stays on current version
- Excel generation fails → Telegram alert · retry tomorrow

Admin dashboard toggle per component:
- [ON/OFF] CoinGecko integration
- [ON/OFF] CMC integration
- [ON/OFF] Telegram notifications
- [ON/OFF] Excel report generation
- [ON/OFF] GitHub metrics push
- [ON/OFF] CCXT auto-upgrade

Philosophy: nothing brings down entire platform
Each piece fails gracefully · independently

## Diagnostics Report System (LOCKED)

- Auto-generated every hour
- Pushed to GitHub automatically
- Always latest at:
  https://raw.githubusercontent.com/baderbalubaid/Averion/main/diagnostics/latest.md

Contains:
- Auto-analysis with explanations (🔴🟡🟢)
- 30 day system health table
- 30 day cron performance table
- 30 day bot events table
- 30 day trade events table
- Server upgrade guide

Admin dashboard buttons:
- [📋 Copy Markdown] → paste directly to Claude
- [🔗 Copy URL] → Claude fetches from GitHub
- [📥 Download] → save locally

Rolling 30 days:
- Day 31 automatically deleted
- New day added automatically
- No manual cleanup needed

How to use with Claude:
"Read this and diagnose:
 https://raw.githubusercontent.com/baderbalubaid/Averion/main/diagnostics/latest.md"

## Limit Orders for Entry and DCA (LOCKED)

User selects per bot in wizard:
- Entry order type: [Market] or [Limit]
- DCA order type: [Market] or [Limit]
- Can switch ON/OFF anytime · even mid-trade

Limit DCA behavior:
- Places limit buy for NEXT DCA level only
- Not all levels at once (avoids locking USDT)
- Partial fill → avg cost + TP recalculate immediately
- TP fires → cancel pending limit → USDT freed
- Remaining < minimum order → add to next DCA level
- Example: $10 DCA · $2 fills · $7.50 fills · $0.50 remaining
  → $0.50 added to next DCA level amount

Trailing TP:
- Trailing TP disappears when limit DCA mode ON
- Common sense: limit orders cannot trail
- Option hidden automatically in wizard when limit selected

ON → bot places limit order on exchange immediately
OFF → cancels all pending limit orders · USDT returned

## Sequential Trade Gates (LOCKED)

Two separate bot settings:
- Trades per bot: max concurrent open trades from this bot
- Trades per coin: how many times same coin repeats

Gate conditions (per bot):
- [DCA trigger ON/OFF]: opens next trade when current hits DCA level
- [Timer ON/OFF]: opens next trade after X hours from last opened
- Both ON: whichever comes first opens next trade
- Both OFF: only 1 trade per coin (default behavior)

Sequence behavior:
- Trades open one by one in sequence
- Last opened trade = gate reference always
- When reference trade closes → previous becomes reference
- Sequence continues forever · no hard stop
- When one closes → slot opens → new trade can start

Entry method:
- All trades in bot use same parameters
- Same DCA% · spacing · TP% · entry method
- No per-trade customization · simple · consistent

Example:
Trades per bot: 20 · Trades per coin: 3 · Gate: both
→ Bot opens max 20 trades total
→ Any coin max 3 concurrent trades
→ Each coin's trades open sequentially via gate
→ Last opened = reference for next gate trigger

## Feature Phasing — Final (LOCKED)

### Phase 4 — Day 1 Hetzner (paper mode first)
Must work:
- User login (basic auth · admin only)
- Add exchange (MEXC + KuCoin)
- Create bot (basic wizard)
- Paper trading loop (60s cycles)
- Long DCA market orders (paper)
- Smart queue (Loss% / USDT)
- Trailing TP
- Telegram notifications
- Dashboard showing positions
- 144 research bots launched
- Daily cron (CoinGecko · CMC · classify · report)
- Classification engine
- Basic admin dashboard
- Diagnostics auto-generated hourly

Not in Phase 4:
- Short DCA · Limit orders · Sequential gates
- NOWPayments · Public registration
- Virtual wallet UI · Full admin dashboard

### Phase 4.5 — First Live Trade
- After 7+ days paper stable
- $1 test order on MEXC
- Then KuCoin Long DCA live
- Small amounts · monitor carefully

### Phase 5 — After Live Stable
- Short DCA (MEXC first)
- Limit orders (entry + DCA)
- Sequential trade gates
- Virtual wallet UI
- Full admin dashboard
- Smart DCA entry methods proven

### Phase 6 — Public Launch
- NOWPayments integration
- Public registration
- Full authentication
- Performance fees system
- Reserve wallet payments
- Marketing

### Phase 7 — Scale
- More exchanges
- More features
- Server upgrades
- Referral system active

## Gate Reference Promotion Rule (LOCKED)

When reference trade closes:
- Highest sequence_number still open = new reference
- Example: Trades 1·2·3 open · Trade 3 closes
  → Trade 2 becomes reference (highest still open)
- is_gate_reference updated immediately on close
- gate_reference_since = timestamp when became reference

Timer reset rule:
- Timer always measures from gate_reference_since
- NOT from when trade originally opened
- Example: Trade 2 opened 15:00 · became reference 22:00
  Gate timer 5h → next trade at 03:00 (not 20:00)
- Timer resets completely when reference changes
- DCA trigger also resets · watches new reference only

## Short DCA HOLD Rule — Simplified (LOCKED)

Previous rule removed: HOLD Long DCAs 2 seconds
New rule:
- PENDING_BUYBACK flag set when limit order being placed
- Long DCA bots on SAME Virtual Wallet check flag at start of each cycle
- If PENDING_BUYBACK = TRUE → skip this cycle
- Bots on DIFFERENT Virtual Wallet → unaffected · continue normally
- After limit order confirmed placed → flag cleared
- Long DCA resumes next 60s cycle automatically
- 60s cycle handles timing naturally · no manual hold needed

## MAX_COINS Removal — Day 1 (LOCKED)

- Do NOT add MAX_COINS to Hetzner .env
- Replit-only variable · never used on Hetzner
- Simply leave it out of .env completely
- Startup assertion refuses to start if found with PAPER_MODE=false

## Security Session Management (LOCKED)

- JWT token expires 30 days on same device
- Day 30: verification code sent via Telegram or email (FREE)
- Enter code → fresh 30 days granted
- New device: login + immediate verification code required
- Wrong code 3 times → account locked · admin Telegram alert
- No SMS · Telegram or email only (free)

## API Key Withdrawal Warning (LOCKED)

When user adds exchange:
- Required checkbox (cannot save without):
  ☑ "I confirm withdrawal permission is DISABLED on this API key"
- Warning shown in red:
  "Never enable withdrawal permission on your API key!
   If compromised, attacker cannot withdraw your funds."
- Link to guide per exchange showing how to disable
- User responsibility · platform warns clearly
- No automatic withdrawal testing from our side

## Security Audit Log (LOCKED)

Record every critical action in security_audit_log:
- User login: IP · device · timestamp
- Failed login attempts
- API key added/deleted
- Exchange added/deleted
- Bot created/deleted
- Admin actions (every admin endpoint)
- Password changed
- Telegram connected/disconnected
- Verification code sent/used

## API Rate Limiting (LOCKED)

Phase 4-6: not needed
- Queue system naturally limits requests
- Max 100 trades · one DCA per 60s
- Login already brute force protected ✅
Before Phase 6 public launch: add FastAPI middleware
- 60 requests/minute per token
- Easy to add · implement in Phase 5 preparation
- Also before Phase 6: Fernet key rotation · session token hashing · withdrawal validation

## Email Verification at Registration (LOCKED)

- Required before accessing dashboard
- Flow:
  1. User registers → account created (unverified)
  2. 6-digit code sent to email immediately
  3. Redirect to verify page
  4. Enter code → verified → go to dashboard
  5. Cannot access dashboard until verified

- Email service: Resend free tier (3,000/month forever)
- Setup needed: resend.com account + API key
- Add to .env: RESEND_API_KEY · SENDER_EMAIL
- Columns already in schema: email_verified · email_verify_code
- Implement when averionbot.com domain is ready (Day 2)
- Sender email: noreply@averionbot.com


## CoinGecko + CMC Averaging Formula (LOCKED)

### Formula (step by step)
1. Fetch market cap from CoinGecko
2. Fetch market cap from CoinMarketCap
3. Both available → average = (CoinGecko + CMC) / 2
4. Only CoinGecko available → use CoinGecko cap
5. Only CMC available → use CMC cap
6. Both failed → use last recorded cap · Telegram alert
7. If they disagree by more than 100% → use the LOWER value
  (conservative · survivability first · prevents fake cap inflation)

### Why lower value on disagreement
- Protects against data errors classifying coin too high
- A Micro Cap classified as Small Cap = wider DCA spacing = less risk
- A Small Cap classified as Micro Cap = tighter DCA spacing = more trades
- Better to be conservative than aggressive on cap classification

### Example
- CoinGecko: $50M · CMC: $120M · Difference: 140% > 100%
- Use lower: $50M → Micro Cap parameters applied ✅
- CoinGecko: $50M · CMC: $60M · Difference: 20% < 100%  
- Use average: $55M → Micro Cap parameters applied ✅

## Email Architecture (LOCKED)

### Domain (LOCKED)
- One domain only: averionbot.com
- Dashboard: averionbot.com/dashboard
- Admin: averionbot.com/ops-XXXX
- API: averionbot.com/api

### Two Email Systems

Human email (Google Workspace):
- admin@averionbot.com
- support@averionbot.com
- billing@averionbot.com
- $6/mo per user

Automated email (Resend):
- noreply@averionbot.com
- Free: 3,000/month · 100/day
- verification · reset · reports · alerts

### EmailProvider Abstraction (LOCKED)
- All email through email_service.py
- Never call Resend directly
- Switching provider = change one file only

### Marketing Email (Future)
- Phase 6+: Brevo or MailerLite
- Separate from transactional
- Transactional stays on Resend forever

## Manual Bot — Full Specification (LOCKED)

### What is Manual Bot
- Separate bot type where user manually selects
 which coin to open a position on
- Not affected by Smart DCA automation or signals
- User has full control over every position opened
- All standard features work: DCA · TP · queue · alerts

### Bot Creation (one time setup)
User sets defaults when creating bot:
- Name · Exchange · Direction (Long/Short)
- Select Virtual Wallet
- Default base order size ($)
- Default DCA %
- Default spacing multiplier
- Default size multiplier
- Default TP %
- Default trailing %
- Default trades per coin (e.g. 1)
- OR toggle Smart DCA ON:
 → Spacing + TP calculated automatically
 → User can still override per position

### Opening a Position (real time)
From bot dashboard:
1. Search bar → type coin name (fast search)
2. Coin appears with current live price
3. All default parameters pre-filled
4. User can override ANY field before firing:
  - Order size
  - DCA %
  - Spacing multiplier
  - TP %
  - Trailing %
  - Trades per coin (override for this position only)
5. Smart DCA selected + user enters TP%:
  → User value OVERWRITES smart calculation
6. Hint shown if order size < exchange minimum
7. [Open Position] → market order fires immediately
8. Position tracked normally with all features

### Trades Per Coin Override (LOCKED)
- Default trades per coin set at bot creation
- When opening position user can change it
- Example:
 · Default = 1 · RVN already open
 · User wants second RVN position
 · Changes trades per coin to 2 for this open
 · System allows it · two positions tracked separately
 · Each has own DCA · TP · history
- Gives expert users full control
- Safe defaults protect beginners

### Manual Bot Rules (LOCKED)
- Has own virtual wallet (isolated capital)
- Allows multiple positions on same coin
 (unlike auto bots which enforce one pair per bot)
- Research data kept separate from auto bots
- Manual positions do NOT affect Smart DCA research scores
- Available in bot creation wizard Step 2
- All standard features apply:
 DCA · TP · smart queue · Telegram alerts · history

## Market Regime Classification (LOCKED)

### Why This Matters
Research promotion requires 3+ regimes tested.
Without tagging · bull-market bot gets promoted incorrectly.
180 days of data becomes untrustworthy.

### Daily Regime Determination (runs at 04:30 cron)
After classification · determine daily regime:

Bull Market:
- BTC 7-day change > +5%
- AND market volatility < 60%

Bear Market:
- BTC 7-day change < -5%
- OR market volatility > 80%

Sideways:
- Everything else

### Storage
- Written to market_regimes table daily
- research_scores.regimes_tested JSONB updated
- Promotion BLOCKED if fewer than 3 regimes tested

### Promotion Score = MEDIAN (LOCKED)
- Use MEDIAN across all coins tested · NOT mean/sum
- Prevents one lucky/unlucky altcoin skewing results
- Example: method trades 50 coins
  · 1 coin 10x's → mean distorted · median accurate
- generate_metrics.py must calculate median per method
- This is the most important research integrity rule

### Regime Tagging in Research Scores
- regimes_tested JSONB stores array of regimes seen
- Example: ["bull", "bear", "sideways"]
- Minimum 3 unique regimes before promotion eligible
- Bot can run 180 days all bull → no promotion possible

## Short Research Bots (LOCKED)

### Structure
- 144 Short paper bots · same methods as Long grid
- 5 selected coins only: BTC · ETH + 3 high-liquidity alts
- All paper mode · virtual balance · no real coins needed
- direction = 'short' tagged in research_scores
- Completely separate research from Long bots

### One Winner — Smart DCA (Short)
- Same promotion formula as Long
- Median score across all 5 coins → one winner
- Winner becomes Smart DCA (Short) engine
- Long has its own Smart winner · Short has its own
- Two separate smart engines · never mixed

### Trade Count
- 144 bots × 5 coins = 720 paper short trades
- Data collected over same 6 month period as Long

### Reports
- One combined Short research report
- Shows all 14 entry methods + 5 benchmarks ranked by median score
- Benchmarks visible for comparison · not promotion-eligible
- Winner declared after 6 months · same rules as Long
- Admin sees Long + Short results in Tab 4

### Short Research Logs
- Separate log file: research_short.log
- Separate metrics: metrics/short_latest.json
- Pushed to GitHub alongside Long metrics

## Custom Entry Method (LOCKED)

### What It Is
- User-defined entry signal built in bot wizard
- Available alongside: Smart DCA · ASAP · Mean Reversion
- User selects which indicators to use + thresholds
- Saved as named preset · reusable across bots

### Entry Method Selection in Wizard Step 3
○ Smart DCA (auto · best research winner)
○ ASAP (immediate · no signal wait)
○ Mean Reversion (E1 preset · RSI+VWAP)
○ Custom Entry ← user builds own signal

### Custom Entry Builder
User selects indicators to include:
- ☑ RSI · set threshold (e.g. < 35)
- ☑ EMA · set fast/slow (e.g. 9/21)
- ☑ MACD · crossover required ON/OFF
- ☑ Volume spike · set multiplier (e.g. 1.5x)
- ☑ Stoch RSI · set oversold level (e.g. 20)
- ☑ Bollinger Band · price below lower band

Confluence setting:
- Any 1 condition met → entry
- Any 2 conditions met → entry
- Any 3 conditions met → entry
- ALL conditions met → entry (strictest)

### Saving Custom Entry
- User names the setup: "My Setup 1"
- Saved to user account
- Reusable when creating future bots
- Editable anytime (affects new positions only)
- Multiple saved setups allowed

### Research Tracking
- Custom entry bots tagged: entry_method = 'custom'
- Parameters stored in bots table as JSONB
- Not included in Smart DCA promotion research
- User's own data · private to their account

---

## Admin Copy Bot System (LOCKED)

### Option A — Copy Specific Bot
- [Copy Bot] button on any bot in admin user view
- Creates identical bot on admin account with:
  · Same entry method
  · Same DCA% · spacing · TP% · trailing
  · Same exchange type
  · Same virtual wallet type
  · Admin's own API key used
  · Admin sets own order size
- Live mirror behavior:
  · Source bot opens position → admin bot opens same coin
  · Source bot closes position → admin bot closes too
  · Admin can also close manually anytime
  · If admin closes manually → source bot unaffected
- Mirror status shown on bot card: MIRRORING @username
- Stop mirror anytime → [Stop Mirror] button
- Existing positions continue to TP after stop

### Option B — Mirror Exchange
- [Mirror Exchange] button in admin user detail page
- Select user + which exchange to mirror
- Behavior:
  · Every new bot user creates on that exchange
    → auto-creates identical bot on admin account
  · Every position user opens → admin opens same
  · Every close → admin closes same
  · Admin uses own API key + own order sizes
- Admin can pause mirror anytime
- Existing positions continue normally after pause
- New bots stop being created after pause

### Both Options Rules (LOCKED)
- Admin only · never visible to regular users
- Admin account = 0% fee · no reserve needed
- Mirror data shown in admin Tab 5:
  · Which users being mirrored
  · Which bots being copied
  · P&L from mirrored positions
  · [Stop] button per mirror
- Copy Bot and Mirror Exchange independent
  · Can use both simultaneously
  · Can mirror exchange AND copy specific bots
    from different users at same time

### DB Tables Needed
- bot_mirrors: bot_id · source_bot_id · admin_id · active
- exchange_mirrors: exchange_id · source_user_id · admin_id · active

## Dust Handling — Per Coin Only (LOCKED)

- Dust evaluated and sold PER INDIVIDUAL ASSET only
- Cannot combine dust from different coins into one order
- Example: 0.00003 BTC dust + 0.4 RVN dust = TWO separate checks
- Sunday cron checks each coin's dust value independently:
 · If RVN dust value >= exchange minimum → market sell RVN
 · If BTC dust value >= exchange minimum → market sell BTC
 · If still too small → keep waiting · check next Sunday
- No cross-asset bundling ever · exchanges don't support it
- Each coin sold back to its quote currency (USDT) separately

---

## E4 Time-Cycle Window — Extended (LOCKED)

- Original E4 fired Sunday UTC 22:00-23:00 only
- Problem: max 26 opportunities in 6 months · never reaches 100 trades
- Fix: E4 now fires on THREE weekly windows:
 · Sunday UTC 22:00-23:00
 · Monday UTC 00:00-02:00
 · Wednesday UTC 12:00-14:00
- This gives ~78 opportunities in 6 months · enough for evaluation
- All other E4 parameters unchanged
- Still tests time-cycle hypothesis · just more data points

---

## Research Replacement Bot Scoring (LOCKED)

- Monthly elimination: replace zero-trade bots with looser variation
- Replacement bots are EXCLUDED from promotion scoring
- Replacement bot must complete a FULL 6-month cycle before eligible
- Tagged in research_scores: replacement_bot = TRUE
- Promotion only considers bots that ran full period from Day 1
- Reason: prevents artificially high scores from partial periods
- Replacement bots still tracked · data kept · just not promoted

---

## PENDING_BUYBACK Deadlock Protection (LOCKED)

Problem:
- Server crashes after Short DCA sell fires
- But before limit buy order placed on exchange
- PENDING_BUYBACK flag stuck TRUE in DB forever
- ALL Long DCA bots on same exchange frozen indefinitely

Solution — Two layer protection:

Layer 1: 60 second timeout
- PENDING_BUYBACK flag auto-clears after 60 seconds
- Next bot loop cycle checks: if flag > 60s old → clear it
- Long DCA resumes automatically

Layer 2: Startup reconciliation
- On every PM2 restart · check all PENDING_BUYBACK flags
- For each flag: verify limit order exists on exchange
- If limit order confirmed → keep flag until filled
- If no limit order found → clear flag · place new limit order
- If USDT insufficient → alert admin · clear flag

DB column needed:
- positions.pending_buyback_since TIMESTAMP
- Set when flag = TRUE · cleared when flag = FALSE
- Used to detect stale flags older than 60 seconds

---

## Client Order ID Convention (LOCKED)

All orders submitted via CCXT must use clientOrderId:

Format: avr_{bot_id}_{position_id}_{dca_level}_{timestamp}

Example: avr_42_187_3_1748293847

Benefits:
- Startup reconciliation can parse owner from exchange order
- No guessing which bot or position owns an unconfirmed order
- Works across all 7 exchanges that support clientOrderId
- Exchange clientOrderId support:
  · MEXC: ✅ supported
  · KuCoin: ✅ supported
  · Binance: ✅ supported
  · Bybit: ✅ supported
  · OKX: ✅ supported
  · Gate.io: ✅ supported
  · Bitget: ✅ supported
  · Fallback for any unsupported: symbol + timestamp + amount match

Implementation:
- CCXT params: {'clientOrderId': f'avr_{bot_id}_{position_id}_{level}_{int(time.time())}'}
- Stored in trades.client_order_id column
- Reconciliation parses this string to map back to position

DB column needed:
- trades.client_order_id VARCHAR(100)

## Research Bot Launch Sequence (LOCKED)

### Day 3 Launch Plan
- Day 1: Server setup · DB · PM2 · bot loop
- Day 2: Domain · SSL · dashboard · admin
- Day 3 Step 1: Launch 144 Long research bots only
- Day 3 Step 2: Monitor loop time for 24 hours
  · Loop time < 30s → proceed ✅
  · Loop time 30-50s → investigate before Short bots
  · Loop time > 50s → fix before adding Short bots
- Day 4+: Launch 144 Short research bots IF capacity confirmed
- Total max: 288 research bots on CX23 (2 vCPU · 4GB RAM)

### Capacity Thresholds
- Green: loop < 30s · all bots firing normally
- Yellow: loop 30-50s · monitor · consider upgrade
- Red: loop > 50s · pause adding bots · upgrade server
- CX33 upgrade (4 vCPU · 8GB): €17.99/month if needed

### Why Separate Launch
- 288 bots simultaneous = unknown server impact
- Staged launch = safe · measurable · reversible
- Short bots use same coins × 5 = more API calls
- Better to confirm Long bots stable first

## Email Verification Resend (LOCKED)

### Problem
Email delayed or spam-filtered → user stuck on verify page → abandons registration.

### Solution
Verify page shows countdown timer + resend button:
- "Code sent to email@example.com"
- Timer: "Resend available in 2:00" · counts down
- After 2 minutes → [Resend Code] button appears
- Click → new 6-digit code generated
- Old code invalidated immediately
- New email sent via Resend
- Timer resets to 2:00

### Rules (LOCKED)
- Minimum 2 minutes between resends
- Maximum 5 resends per hour per email
- Each new code invalidates previous code
- Code expires after 30 minutes always
- Resend count tracked in DB · resets hourly
- After 5 resends in 1 hour → show message:
 "Too many attempts · try again in 1 hour"
- Resend available on verify page only · not after verified

## Dead Coin Terminal State (LOCKED)

### Position Status Values
- active: position open · trading normally
- standby: waiting for partial DCA completion
- tp_fired: TP triggered · closing in progress
- closed: position closed · profit/loss recorded
- dead: coin delisted without ST flag · no recovery possible
- archived: auto-archived after 365 days disconnected

### Dead Coin Flow (No ST Flag)
When exchange removes pair without ST warning:
1. CCXT returns error on price fetch for that coin
2. After 3 consecutive failures → mark position: dead
3. Dashboard shows: DEAD COIN · [Mark Closed Manually] button
4. Attention log: red warning · manual action required
5. User goes to exchange · closes position manually
6. User clicks [Mark Closed Manually] in dashboard
7. Position status → archived · P&L estimated from last known price
8. Capital freed from virtual wallet

### DB Status Values (LOCKED)
positions.status:
- 'open' → active trading
- 'standby' → partial DCA waiting
- 'closed' → normal close · TP or manual
- 'dead' → coin delisted · no trading possible
- 'archived' → historical record only

### Source of Truth (LOCKED)
PostgreSQL is the source of truth.
Exchange state is reconciled against DB on every startup.
In any conflict: DB wins · exchange state verified · never assumed.

## Research Bot Lifecycle Policy (LOCKED)

### Philosophy
Research never fully stops — platform always self-improving.
No other DCA platform continuously validates its own algorithm.
This is a permanent competitive advantage.

### Phase 1 — Months 1-6 (Full Grid)
- All 144 bots running simultaneously
- Monthly elimination: replace zero-trade bots only
- At 6 months: winner selected → Smart DCA default
- Data kept forever — never deleted

### Phase 2 — Months 7-12 (Validation)
- Keep top 30% bots running (~45 bots)
- Drop obvious losers (worst scores · zero trades)
- Monitor: does winner still beat benchmarks?
- If new method overtakes → promote new winner

### Phase 3 — Annual Review (Ongoing Forever)
- Is current Smart DCA winner still winning?
- Did market regime change favor different method?
- Promote new winner if consistently better
- Research cycle repeats indefinitely

### Bot Count Over Time
- Month 1-6: 144 bots (full grid)
- Month 7-12: ~45 bots (top 30%)
- Year 2+: ~20 bots (champion + challengers)
- Never drop below 5 bots (always have competition)

### Admin Paper Trade Limit (LOCKED)
- Regular users: 30 paper trades maximum
- Admin account: UNLIMITED paper trades
- Research bots run under admin account
- is_admin check skips paper limit entirely
- Research trades tagged: is_research = TRUE
- Research data kept FOREVER · never purged
- Storage cost = negligible (< 5MB per year)

### Research Data Retention
- All research trades: kept FOREVER
- Reason: baseline for future comparisons
- Reason: proof of why winner was selected
- Reason: regime history invaluable long term
- research_scores table: never delete rows
- Only add · never remove historical data

## Fee Debt vs Subscription Shortage — Clear Distinction (LOCKED)

Two completely different systems · never confused:

### Performance Fee Debt
- Triggered when: position closes at profit · reserve insufficient
- Bot status: stays ON · never changes
- Effect: no NEW positions open
- Resolution: user tops up → debt cleared → resumes automatically
- Example: won $50 · owe $10 fee · reserve = $0
  → bot ON · no new trades · debt shown in red

### Subscription/Slot Fee Shortage  
- Triggered when: 1st of month · reserve cannot cover bot fees
- Bot status: changes to EXPIRED (last created bot first)
- Effect: bot turns OFF · existing positions continue to TP
- Resolution: user tops up + manually reactivates bot
- Example: 3 bots · $3 due · reserve = $1.50
  → last created bot → EXPIRED
  → first 2 bots continue normally

### Why Different Behavior
- Performance fee = earned by platform from profits
  Bot staying ON generates more profits = more fees eventually
- Subscription fee = flat monthly charge
  Cannot justify keeping bot active if user won't pay flat fee
  User made conscious decision to not maintain reserve

## Smart Queue Recalculation Triggers (LOCKED)

Queue recalculates at start of EVERY 60-second cycle.
No manual trigger needed · always fresh.

### Events that affect next cycle score:
- User adds funds → wallet balance updates → next cycle uses new balance
- Position closes (TP) → capital freed → next cycle rescores
- DCA toggle ON/OFF → next cycle includes/excludes position
- New position opens → next cycle adds to queue
- User changes bot params → next cycle uses new params

### All changes take effect: next 60-second cycle
- Maximum delay: 60 seconds
- No manual refresh needed
- No restart needed
- Queue always reflects current state

## Security Hardening — Three Layers (LOCKED)

### Layer 1 — Fernet Key Rotation (Monthly)
- New FERNET_KEY generated 1st of every month
- All exchange API keys re-encrypted with new key
- Old key deleted from server after re-encryption
- Key version tracked in fernet_key_versions table
- Maximum breach window = 30 days
- Admin Telegram alert after each rotation

Rotation process (automated):
1. Generate new Fernet key
2. Fetch all encrypted keys from DB
3. Decrypt with old key
4. Re-encrypt with new key
5. Update DB
6. Delete old key from memory
7. Update FERNET_KEY in .env
8. Log rotation in fernet_key_versions

### Layer 2 — API Permission Validation
- Test call made when user saves API key
- Verifies withdrawal permission is DISABLED
- If withdrawal enabled → block save · show warning
- Test uses exchange's permission system directly
- Endpoint: POST /exchanges/validate-key
- Result logged in security_audit_log

Exchange minimum required permissions:
- Spot trading: READ + TRADE only
- Never: Withdrawal · Transfer · Sub-account

### Layer 3 — IP Whitelist Verification
- Server IP shown prominently when adding exchange
- User must whitelist Averion server IP on exchange
- After saving key → test call from our server
- If call succeeds → IP whitelist confirmed ✅
- If call fails → user prompted to whitelist first
- Exchanges requiring IP whitelist:
  · Binance: REQUIRED
  · OKX: REQUIRED
  · KuCoin: RECOMMENDED
  · Others: OPTIONAL but shown

### Combined Effect
- Layer 1: Leaked .env = useless after 30 days
- Layer 2: Stolen key = cannot withdraw funds
- Layer 3: Stolen key = only works from our IP
- All 3 together = customer API keys effectively protected
- Even insider threat = limited to 30-day window

## Performance Fee Timing (LOCKED)

Fee deducted IMMEDIATELY on every profitable trade close.
No monthly netting. No holdback. No escrow.

### Rule
- Position closes at profit → fee = profit × 20%
- Fee deducted from reserve immediately
- If reserve insufficient → fee recorded as debt
- Loss trades → $0 fee · no discussion · no exception

### Why immediate
- Simpler to implement and audit
- No complex monthly reconciliation
- Customer always knows exactly what they owe
- Profitable trade = we earned it · take it now

### Examples
- Win $50 → fee $10 → deducted immediately
- Win $1 → fee $0.20 → deducted immediately
- Lose $100 → fee $0 → nothing touched
- Win $200 then lose $1000 same month → fee = $40 (on the $200 win only)

## Research Account Separation (LOCKED)

### Two Admin Accounts
1. Admin account (Bader personal)
   - Login: admin@averionbot.com
   - Personal bots · no research bots
   - Normal admin dashboard access
   - Balance separate from research

2. Research account (automated)
   - Login: research@averionbot.com
   - ALL 144 research bots run here
   - Visible in admin dashboard Tab 4 only
   - No personal trading ever
   - is_research = TRUE on all positions/trades

### Why Separate
- Research data never mixes with personal data
- Reports are clean and independent
- Research balance = virtual only
- Personal balance = real money tracked separately
- Admin can view research from dashboard but never confused

### Setup
- Created automatically in init_db.py on Day 1
- Password set in .env: RESEARCH_ACCOUNT_PASSWORD
- launch_research_bots.py uses research account

## Manual Bot Queue Behavior (LOCKED)

- Manual bot shares queue with Smart DCA bots (same wallet)
- Manual positions compete equally by Loss% / USDT score
- Manual DCA option available per position
- User controls manual DCA timing directly
- No special priority for manual over smart
- Reason: shared wallet = shared queue = fair competition
- User can always use separate wallet to isolate manual bot

## Coin Classification Final Decisions (LOCKED)

### Volume-Weighted Spacing: REMOVED
Old: category_spacing = weighted average (BTC dominated at 87%)
New: each coin gets independent spacing from its own ATR data
Category = safety limits only (min/max bounds)

### Per-Coin Spacing Formula (LOCKED)
spacing = max(ATR_14 x 1.5, median_bounce x 0.85)
Clamped to category min/max
Independent per coin · never averaged across coins

### Regime-Aware TP Multiplier (LOCKED)
Bull regime: multiplier = 0.80 (ride momentum longer)
Bear regime: multiplier = 0.60 (take profit fast)
Sideways: multiplier = 0.70 (default)
Strong Bull: multiplier = 0.85
Strong Bear: multiplier = 0.55

Formula:
TP = weighted_avg_entry x (1 + median_recovery x regime_multiplier)
Clamped to category TP min/max

### Research Bots Use Classified Params (LOCKED)
Research bots use same classification as live bots
Reason: best signal = goes to TP with zero DCAs
Fewer DCAs = better signal quality = higher RARS
Classification sets correct TP target for fair signal comparison

### Server Load Assessment (LOCKED)
Per-coin spacing: one SQL UPDATE per coin per day at 03:30
Not a loop issue: runs in daily cron not in bot loop
Same server handles 288 bots easily

## Research Bot Dashboard — All Decisions (LOCKED)

### 1. Bot Naming Convention
Each research bot named exactly from JSON:
E1-1 · E1-2 · E1-12 (E1 has 12 variations)
E11-3 · E11-9 (E11 has 9 variations)
DB fields: name='E11-3' · method='E11' · variation='E11-3'
is_research = TRUE on all research bots
Auto-created by launch_research_bots.py on Day 1
Zero manual creation needed

### 2. Research Tab — Separate (LOCKED)
Added as Tab 7 in admin dashboard
NEVER overwrites existing tabs (1-6 unchanged)
Shows ONLY research bots (is_research = TRUE)
Completely separate from customer bots forever
Research bots never appear in customer bot tabs

### 3. Trade Count Control — Input + Confirm
Research Tab top section:
- Input box: user types number (e.g. 10)
- [Apply to All] button
- Confirmation popup before applying
- Updates all 252 research bots simultaneously
- No slider · typed number only · explicit confirm

### 4. Weekly Reporting — Already Locked
See: docs/AI_RESEARCH_SYSTEM_BRIEF_FINAL.md
Weekly Sunday markdown · GitHub push · Telegram alert

### 5. Research Tab Layout — Collapsed Rows
Level 1 (default): One row per METHOD
Columns: Method · Bots · Total Trades · Win% · Avg DCAs · P&L$
Sortable by any column

Level 2 (click to expand): One row per VARIATION
Columns: Variation · Trades · Win% · Avg DCAs · P&L$
Current champion marked with star ⭐

Level 3 (click variation): Detail panel slides open
Shows:
OPEN TRADES table:
- Coin · Opened date · Days open · Entry · Current · DCAs · P&L$ · P&L%
- Sortable by any column

CLOSED TRADES table:
- Coin · Entry · Exit · Days · DCAs · P&L$ · P&L%
- Sortable by any column

Summary bar:
- Avg holding days · Win rate · Avg DCAs · Total P&L · RARS · Regime

### 6. Custom Entry Builder (LOCKED)
Third entry option for customers (after Smart DCA · ASAP):
○ Smart DCA (current champion method)
○ ASAP (buy immediately no signal)
○ Custom Builder

Custom Builder:
- Up to 3 conditions (max)
- Each condition: [indicator] [operator] [value]
- All 3 must be true simultaneously for entry
- Historical test button: shows fires in last 30 days

Available indicators for custom entry:
RSI · VWAP distance · Bollinger Band %
Volume multiplier · EMA crossover
MACD signal · Z-Score · ATR multiplier
Fibonacci level · Stochastic RSI
ADX level · Supertrend direction
OBV direction · RSI Divergence
Funding Rate · Relative Strength vs BTC

Reason max 3 conditions:
More than 3 = signal fires too rarely
Customer gets frustrated with no entries
Quality vs frequency balance

Preview shown before saving:
"Entry when: RSI < 35 AND price 3% below VWAP AND volume > 1.5x"

## Admin Dashboard V2 — Final Structure (LOCKED)

9 tabs total · owner is also a user with own trades

Tab 1: Dashboard (home · alerts · platform overview · exchanges)
Tab 2: My Bots (bots + queue per wallet + history sub-tab)
Tab 3: My Copy (mirrors · copy bots)
Tab 4: Research (252 bots · champions · reports)
Tab 5: Users (customer management · 3-level dropdown)
Tab 6: Health (server · cron · fetch · performance · markdown export)
Tab 7: Trading (exchanges · classification · Smart DCA)
Tab 8: Controls (system controls · owner wallet · security)
Tab 9: System (account · settings · danger zone)

Key decisions:
- Fees shown as negative (customers owe owner)
- Each wallet = independent queue
- Bot view = 3 sub-tabs (Positions · Queue · Closed)
- History = all trades across all bots (separate sub-tab)
- All coins bot shows summary + paginated detail
- Suspend = no new trades · existing continue · not holding money
- Health report exportable as markdown for AI review
- Full research report from Day 1 available anytime

## Customer Dashboard — Final Structure (LOCKED)

Same tab structure as admin (consistent UX):
Tab 1: Dashboard (home · alerts · exchange overview · recent activity)
Tab 2: Bots (bots + queue per wallet + history sub-tab)
Tab 3: Settings (profile · exchanges · notifications · reserve · billing · security)

Key decisions:
- Mobile first · fits phone screen
- Same tab names as admin for consistency
- Bot edit: changes apply to NEW trades only
- Existing trades: keep original params forever
- Queue: per wallet · independent
- Bot detail: 3 sub-tabs (Positions · Queue · Closed)
- History: all closed trades only (no queue history)
- Custom entry builder: up to 3 conditions max
- Simulate tool: shows effect of adding/removing capital

## Notifications — Final (LOCKED)

One Telegram chat · @AverionBot
Long/Short = same format · only label differs
Profit in $ or coin based on bot setting

Types:
🟢 TRADE: opened · DCA/Sell fired · closed (toggle)
🔴 ALERT: reserve · API · ST · checkpoint (recommended ON)
🟢 INCOME: referral earned (toggle)
📊 REPORT: daily · weekly · monthly (toggle)
📧 EMAIL: security · deposit · reports (toggle)

All controls in Settings tab only.

## Admin Telegram — 3 Channels (LOCKED)

Channel 1: Alerts (urgent · needs action)
→ Reserve empty · API rejected · crashed · security · breaker

Channel 2: Activity (info · no action)
→ New user · deposits · fees · referral · research updates

Channel 3: System (technical · daily digest)
→ Cron summary · server health · CCXT · backups · rotation

Daily digest: sent every morning to Channel 3
Contains: cron results · platform stats · server health · alerts count

## Reporting System — Final (LOCKED)

Excel reports: REMOVED
Replaced with 3 structured markdown reports:

1. Daily Health Report (05:00 daily · GitHub)
  → Server · cron · loops · 30-day rolling data
  → [Copy] buttons per section in Health tab

2. Weekly Research Report (Sunday 05:00 · GitHub)
  → Already locked in research brief

3. Monthly Summary (1st of month 05:00 · GitHub)
  → Platform growth · financial · top coins

All reports:
→ Context header (server specs + normal ranges)
→ Attention section (problems first)
→ Notes section (blank · AI fills)
→ Pushed to GitHub automatically
→ Shareable via URL with any AI

## Pricing System — Final (LOCKED)

Free tier: unlimited exchanges · 5 bots · 100 open trades · 30 paper · $5 trial
Add-ons: extra bots + trade bundles (prices TBD · admin sets in DB)
Billing: one-time default · auto-renewal opt-in · expiry date shown
Performance fee: 20% immediate on profit · loss = $0
Referral: 2.5% of 20% fee · forever · registration only
Reserve wallet: minimum $10 · NOWPayments · TRC20/BEP20
Owner wallet: real TRC20 address · auto-transfer at $10 threshold
Paper trades: 30 max · auto-close after 90 days no live trade
Trade limit: 100 hard cap · bundles raise the limit

## Critical Bugs Fixed — Post Session 5 Review

### Bug 1: secret_enc not decrypted in reconcile_orders()
File: exchanges.py
Line: ~9376
Fix: 'secret': exchanges_module.decrypt(secret)
Was: 'secret': secret (raw cipher text!)
Impact: ALL exchange auth fails on startup

### Bug 2: import bcrypt missing in init_db.py
File: init_db.py
Fix: add 'import bcrypt' at top of file
Was: bcrypt.hashpw called but bcrypt never imported
Impact: Admin user creation crashes Day 1

### Bug 3: research_bots.json missing E15-E26 + E18b
File: setup/research_bots.json
Fix: E15-E26 + E18b already added this session
Verify: launch_research_bots.py reads updated JSON
Impact: Would create 144 bots instead of 261

### Bug 4: smart_dca_champions not seeded
File: init_db.py
Fix: Insert 3 seed rows on init:
     Bull → E10 as starting champion
     Bear → E10 as starting champion
     Sideways → E10 as starting champion
Impact: generate_metrics.py silently does nothing forever

### Bug 5: Excel cron step not updated
File: automation/daily_cron.sh
Fix: Replace generate_excel.py with 3 markdown reports:
     generate_health_report.py (daily)
     generate_weekly_report.py (weekly · Sunday only)
     generate_monthly_report.py (monthly · 1st only)
Impact: Cron tries to generate Excel that was removed

### Bug 6: market_regimes table missing 5-signal columns
File: setup/schema.sql
Fix: Add columns:
     realized_vol_30d DECIMAL(10,4)
     market_cap_30d_change DECIMAL(10,4)
     btc_200d_ma_position VARCHAR(10)
     altcoin_season_index INTEGER
     raw_score INTEGER
Was: Only stored btc_24h_change · btc_7d_change · market_volatility
Impact: Cannot audit or recalculate historical regimes

### Bug 7 (new): RARS Capital Efficiency not normalized
File: automation/generate_metrics.py
Fix: Store regime_tp_multiplier_at_entry in research_scores
     Normalize: capital_efficiency = raw_efficiency / regime_multiplier
Was: Capital efficiency penalizes bull-regime methods unfairly
Impact: Research picks wrong champion → wrong method in live trading

---

## New Decisions Locked (Post Review)

### E18b — Low ADX Ranging Market (9 bots)
Logic: ADX < threshold (ranging) + RSI oversold
= Mean reversion in sideways market
Opposite hypothesis to E18 (high ADX)
Both test different conditions · research decides winner

| Bot | ADX Max | RSI Max | Lookback |
|-----|---------|---------|---------|
| E18b-1 | 20 | 30 | 14h |
| E18b-2 | 20 | 35 | 14h |
| E18b-3 | 20 | 40 | 14h |
| E18b-4 | 25 | 30 | 14h |
| E18b-5 | 25 | 35 | 14h |
| E18b-6 | 25 | 40 | 14h |
| E18b-7 | 20 | 30 | 24h |
| E18b-8 | 25 | 35 | 24h |
| E18b-9 | 25 | 40 | 24h |

Total bots: 261 (252 + 9 E18b)

### Signal Status in Bot Detail View
Show live entry signal conditions when customer clicks bot:
Entry signal: Smart DCA E11-3
Last check: 47 seconds ago
Last entry: June 1 14:23
Conditions: [live status per condition]
NOT on main bot card · only inside detail view

### Password Reset
Customer: email reset link (15 min expiry)
Admin Phase 1: Telegram code only
Admin Phase 7+: Telegram + phone SMS

### RARS Normalization (Option A)
Store: regime_tp_multiplier_at_entry per trade
Normalize: capital_efficiency / regime_multiplier before scoring
Reason: Bull multiplier makes TP harder → longer close → unfair penalty
Result: Correct champion selected → more profit in live trading

### Onboarding Empty State (3 steps)
Step A: No exchange → "Connect your exchange" prompt
Step B: No bot → "Create your first bot" prompt
Step C: No reserve → "Top up reserve wallet" prompt
Each step dismissible · disappears when complete

## Bugs Fixed — Post Session 5 AI Review Batch 2

### Bug 8: Old Promotion Formula Deleted (LOCKED)
Old: WR^0.30 × AP^0.20 × RS^0.15 × DD^0.35 (multiplicative · DELETED)
New: RARS 35/30/20/15 additive (ONLY formula)
generate_metrics.py must implement RARS only

### Bug 9: PENDING_BUYBACK Race Condition Fix (LOCKED)
New columns in positions table:
pending_buyback_usdt_locked: amount reserved for buyback
pending_buyback_expires_at: timestamp when lock expires (5 min not 60s)
Rule: Long DCA queue SKIPS any USDT locked for pending buyback
Lock cleared when: limit order placed OR expires OR position closed

### Bug 10: Coin Removed Mid-Position (LOCKED)
Rule: Price fetch loop ALWAYS includes coins with open positions
Even if coin removed from tradeable universe
Even if coin delisted or below volume threshold
Price fetched until position closed · no exceptions
TP must always fire · capital never stuck

### Bug 11: Telegram Multi-Channel Language (LOCKED)
Customer = ONE direct chat with @AverionBot always
Delete all references to multiple customer channels
Only admin has 3 separate channels (Channel 1/2/3)

### Bug 12: Research Account Trade Limit Bypass (LOCKED)
New columns in users table:
is_research_account: TRUE for admin research bots
trade_limit_bypass: TRUE = no 100-trade cap
Research account: unlimited concurrent positions
Regular users: 100 hard cap always
Admin personal trading: same 100 cap as regular users

### Bug 13: Password Reset Flow (LOCKED)
Customer flow:
→ Login page: [Forgot Password?] link
→ Enter email address
→ System sends reset link via Resend email
→ Link valid 15 minutes only
→ Customer clicks → sets new password
→ All existing sessions revoked
→ Rate limit: max 5 attempts per IP per hour

Admin flow:
→ Telegram code sent to admin Telegram
→ Code valid 5 minutes only
→ Enter code → set new password
→ All admin sessions revoked

### Bug 14: Champion Challenger Tracking Columns (LOCKED)
New columns in smart_dca_champions:
challenger_method: current challenger method ID
challenger_rars: challenger current RARS score
challenger_weeks: consecutive weeks challenger has beaten champion
challenge_start_date: when challenger first beat champion
challenger_trades: trades challenger has in current period
Populated weekly by generate_metrics.py every Sunday

### Bug 15: Client Order ID Reconciliation (LOCKED)
Columns in trades table:
client_order_id: our generated ID (format: AVR-{bot_id}-{timestamp})
reconciled_at: when last reconciled with exchange
reconciliation_status: pending · matched · missing · extra
On startup: reconcile_orders() matches by client_order_id first
Fallback: match by price + amount + timestamp if ID not found

### Bug 16: Sequential Gate + DCA Checkpoint Precedence (LOCKED)
Rule: checkpoint ALWAYS wins over gate
If checkpoint active: gate ignored until checkpoint resolved
User must take checkpoint action first
Then gate logic resumes normally
Document clearly in bot creation wizard Step 4

### Gap 1: Security Audit Log (LOCKED)
Table: security_audit_log
Logs: login · logout · api_key_add · api_key_delete
     bot_create · bot_delete · position_manual_close
     password_change · wallet_change · admin_action
Visible in: Admin Tab 9 (System) → Access Log
Retention: 90 days

### Gap 2: CSP Headers (LOCKED)
Add to Nginx config:
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Phase 1: basic CSP · Phase 6: strict CSP (remove unsafe-inline)

### Gap 3: JWT Session Refresh (LOCKED)
30-day session tokens
Refresh: automatically on any authenticated request
If token within 7 days of expiry → issue new token
Old token: invalidated after new issued
Customer never sees expiry · seamless experience

### Gap 4: Registration Rate Limit (LOCKED)
Table: rate_limits tracks attempts per IP per endpoint
Registration: max 3 attempts per IP per hour
Password reset: max 5 attempts per IP per hour
Exceeded: return 429 Too Many Requests
Reset: window_start + 1 hour → counter resets

### Gap 5: Database Migration Strategy (LOCKED)
Table: schema_migrations tracks applied versions
Format: versioned SQL files: migrations/001_initial.sql
Each migration: forward only · no rollback
Before any schema change: add migration file
Apply: python3 run_migration.py 002
Never modify schema.sql directly in production

### Gap 6: Staging Environment (LOCKED)
No separate server needed
Staging = PAPER_MODE=true on Hetzner
Separate git branch: staging
Test all changes on staging branch first
Merge to main only after verification
Cron jobs run in staging too but flagged as test

### Gap 7: Referral Anti-Gaming (Phase 7)
Minimum hold period: 24 hours before fee counted
Same-device referral detection: IP + device fingerprint
Wash trading detection: same exchange account pattern
Implement before public launch (Phase 7)
Not needed for Phase 4-6 (limited users)

## Bot State Machine & Reserve Floor — Final (LOCKED)

TP: ALWAYS ON · no toggle · never shown · fires regardless of any condition
Trading toggle: customer controlled
DCA toggle: customer controlled

States:
Normal → floor hit → zero capital → resumed
Each bot has own independent floor + threshold
Auto-resume: ON by default

Set and forget: deposits funds → walks away → platform handles everything
Weekly reminder only if bots paused (not daily)

## Trade Limits — Final (LOCKED)

### Hard Cap Rule
Total 100 = Long + Short + Paper combined
One counter · everything counts

Paper sub-limit: 30 max within the 100
Paper cap: ALWAYS 30 · never changes · no exceptions
Bundles never raise paper limit

### Why Paper Sub-Limit of 30
New user opens 100 paper trades → tries real money → blocked
Frustrated · confused · leaves platform
30 paper max protects new users from this mistake
Paper trades are free · can close at any loss anytime
Non-experienced users may not know this

### Examples

Example 1:
Paper: 20 · Long: 50 · Short: 10 = 80/100
Can open: 20 more (live only)
Paper still has room: 10 more paper allowed

Example 2:
Paper: 30 · Long: 40 · Short: 0 = 70/100
Can open: 30 more (live only)
Cannot open more paper (at 30 sub-limit)

Example 3:
Paper: 30 · Long: 70 · Short: 0 = 100/100
Fully at cap · cannot open anything
Options: close positions OR buy bundle

### Dashboard Display
Total: 70/100
├─ Live: 40 (Long 35 · Short 5)
└─ Paper: 30/30 (at limit)
Can open: 30 more (live trades only)
[Add Bundle] to increase total cap

### Bundle Rules
Buy Bundle 200:
→ Total cap: 100 → 200
→ Paper sub-limit: still 30 (unchanged always)

Buy Bundle 500:
→ Total cap: 100 → 500
→ Paper sub-limit: still 30 (unchanged always)

### Admin / Research Account
is_research_account = TRUE → no cap · unlimited
is_research_account = FALSE → normal rules apply
Admin personal trading → same 100 cap as regular users

### Paper Auto-Close Rule (Already Locked)
After 90 days no live trade → all paper trades auto-close
Prevents forgotten paper trades consuming slots forever

## Public Launch — Final (LOCKED)

No fixed timeline · quality over speed
Personal use first → soft launch → public

Stripe: REMOVED · NOWPayments only forever
Support: owner only · Telegram + email
Marketing: organic · Reddit + X · no paid ads
Legal: Terms · Privacy · Risk Disclosure (AI writes)
Security checklist: 20+ items before first customer
GitHub: public now → private before first customer
Champion timeline: 3-6 months research → auto-switch
Server cost: test after Hetzner · share health report
Fernet key: split (Part A server · Part B Hetzner Secrets)
Monthly rotation: automatic · old key useless after

---

## DCA Parameter System — Complete Technical Spec (LOCKED)

### Weighted Rolling Window
Equal weights: 25/25/25/25
Last 7 days:  25%
Days 8-30:    25%
Days 31-60:   25%
Days 61-90:   25%

Why equal (not 50/30/20):
- No single period dominates
- 50% on last 30 days = too reactive to anomalies
- Stable · reliable · consistent
- Still adapts faster than unweighted 90-day

### Dynamic ATR Scalar
vol_scalar = min(3.0, max(1.2, coin_vol_30d / category_avg_vol))
NOT fixed 1.5 for all coins.
BTC low vol → scalar 1.2 (tighter · more entries)
RVN high vol → scalar 2.0+ (wider · protect capital)

### Regime TP Multipliers (SOFT · replaced old 0.60-0.85)
Strong Bull: 1.10
Bull:        1.05
Sideways:    1.00
Bear:        0.90
Strong Bear: 0.85
Reason: weighted window already adapts to bear.
Old 0.60 bear = TP too tight · left profit on table.

### Per-Coin Percentile Ranges
spacing_floor   = weighted 10th percentile of drops
spacing_ceiling = weighted 90th percentile of drops
tp_floor        = weighted 10th percentile of recoveries
tp_ceiling      = weighted 90th percentile of recoveries
Category limits = emergency backstop only (rarely triggers)

### Outlier Filter (3x IQR)
Applied before ANY percentile calculation:
q1 = 25th percentile
q3 = 75th percentile
iqr = q3 - q1
upper_fence = q3 + (3.0 × iqr)
Remove values above fence before statistics.
Flag coin: outlier_event_detected = TRUE

### Trailing Calculation
trailing = weighted 20th percentile of post-TP extensions
extra_move = (peak_after_TP - TP_price) / TP_price
Minimum floor: 0.1% absolute
15% daily change limit

### Size Multiplier Power Scaling
vol_ratio = coin_volatility / category_avg_volatility
adjusted  = category_base × (vol_ratio ^ 0.7)
size_mult = clamp(adjusted, category_min, category_max)
Power (^0.7) not linear: smoother · safer · bounded
10% daily change limit

### Spacing Full Formula
Step 1: ATR_14_daily from ohlcv_hourly grouped by day
Step 2: vol_scalar = min(3.0, max(1.2, coin_vol_30d / category_avg_vol))
Step 3: median_bounce = weighted median drops (25/25/25/25)
Step 4: spacing_raw = max(ATR_14_daily × vol_scalar, median_bounce)
Step 5: spacing_floor = weighted 10th percentile drops
        spacing_ceiling = weighted 90th percentile drops
Step 6: spacing = clamp(spacing_raw, floor, ceiling)
Step 7: spacing = clamp(spacing, yesterday×0.80, yesterday×1.20)
Step 8: spacing = clamp(spacing, category_min, category_max)

### TP Full Formula
Step 1: median_recovery = weighted median recoveries (25/25/25/25)
Step 2: tp_floor = weighted 10th percentile recoveries
        tp_ceiling = weighted 90th percentile recoveries
Step 3: tp_raw = median_recovery × regime_multiplier
Step 4: tp = clamp(tp_raw, tp_floor, tp_ceiling)
Step 5: tp = clamp(tp, yesterday×0.80, yesterday×1.20)
Step 6: tp = clamp(tp, category_min_tp, category_max_tp)
Applied from: weighted average entry price (not original entry)

### RARS Normalization (Phase 6)
Store: regime_tp_multiplier_at_entry per research trade
Normalize: capital_efficiency = raw_efficiency / regime_multiplier
Reason: Bull multiplier → longer close → unfair penalty on bull entries
Result: Correct champion selected → more profit in live trading

### Edge Cases
Never bouncing (downtrend):
  median_recovery <= 0 → use category default TP
  Mark: weak_recovery · admin alert

Instant recovery (tiny bounces):
  Spacing floor prevents too tight
  Minimum TP: 1.5% absolute floor

Extreme outlier (LUNA-style):
  3× IQR filter before all percentile calculations
  Flag: outlier_event_detected = TRUE

Coin removed from universe mid-position:
  Price fetch ALWAYS continues for coins with open positions
  TP must always fire · capital never stuck

No USDT pair (BTC-denominated):
  Convert ATR to USDT equivalent before calculation

---

## Entry Methods E15-E26 Full Grids (LOCKED)

### E15 — OBV Divergence (9 bots)
Logic: Price lower low + OBV higher low = smart money accumulating
| Bot | Lookback | RSI Max | Min Drop |
|-----|---------|---------|---------|
| E15-1 | 24h | 40 | 3% |
| E15-2 | 24h | 45 | 5% |
| E15-3 | 24h | 50 | 7% |
| E15-4 | 48h | 40 | 3% |
| E15-5 | 48h | 45 | 5% |
| E15-6 | 48h | 50 | 7% |
| E15-7 | 72h | 40 | 5% |
| E15-8 | 72h | 45 | 7% |
| E15-9 | 72h | 50 | 10% |
Fixed: Green close required · OBV rising 3+ candles

### E16 — RSI Divergence (9 bots)
Logic: Price lower low + RSI higher low = selling momentum weakening
| Bot | Lookback | RSI 2nd Low | Confirmation |
|-----|---------|------------|-------------|
| E16-1 | 24h | 35 | Green close |
| E16-2 | 24h | 40 | Green close |
| E16-3 | 24h | 45 | Green close |
| E16-4 | 48h | 35 | Green close |
| E16-5 | 48h | 40 | Green close |
| E16-6 | 48h | 45 | Green close |
| E16-7 | 72h | 35 | Break prior high |
| E16-8 | 72h | 40 | Break prior high |
| E16-9 | 72h | 45 | Break prior high |
Fixed: RSI period 14 · Min drop 3%

### E17 — Liquidity Sweep Reversal (9 bots)
Logic: Price breaks N-hour low (triggers stops) then reclaims = institutional absorption
| Bot | Lookback Low | Reclaim % | Close Position |
|-----|------------|---------|--------------|
| E17-1 | 12h | 0.25% | Upper 40% |
| E17-2 | 12h | 0.50% | Upper 50% |
| E17-3 | 12h | 1.00% | Upper 60% |
| E17-4 | 24h | 0.25% | Upper 40% |
| E17-5 | 24h | 0.50% | Upper 50% |
| E17-6 | 24h | 1.00% | Upper 60% |
| E17-7 | 48h | 0.25% | Upper 40% |
| E17-8 | 48h | 0.50% | Upper 50% |
| E17-9 | 48h | 1.00% | Upper 60% |
Fixed: Volume > 1.5x average

### E18 — ADX Trend Pullback (9 bots)
Logic: HIGH ADX (strong trend) + RSI oversold + above trend EMA
| Bot | ADX Min | RSI Max | Trend EMA |
|-----|---------|---------|----------|
| E18-1 | 20 | 35 | 100 |
| E18-2 | 20 | 40 | 100 |
| E18-3 | 20 | 45 | 100 |
| E18-4 | 25 | 35 | 150 |
| E18-5 | 25 | 40 | 150 |
| E18-6 | 25 | 45 | 150 |
| E18-7 | 30 | 35 | 200 |
| E18-8 | 30 | 40 | 200 |
| E18-9 | 30 | 45 | 200 |
Fixed: ADX period 14 · Price above trend EMA

### E19 — Fibonacci Retracement (9 bots)
Logic: Price pulls back to Fibonacci levels = self-fulfilling institutional orders
| Bot | Fib Level | Lookback | Confirmation |
|-----|-----------|---------|-------------|
| E19-1 | 38.2% | 48h | Green close |
| E19-2 | 50.0% | 48h | Green close |
| E19-3 | 61.8% | 48h | Green close |
| E19-4 | 78.6% | 48h | Green close |
| E19-5 | 38.2% | 96h | VWAP reclaim |
| E19-6 | 50.0% | 96h | VWAP reclaim |
| E19-7 | 61.8% | 96h | VWAP reclaim |
| E19-8 | 78.6% | 96h | VWAP reclaim |
| E19-9 | 61.8% | 168h | VWAP reclaim |
Fixed: Price above EMA200 (uptrend only)

### E20 — VPOC Volume Profile (9 bots)
Logic: Price returns to highest-volume price level = maximum liquidity support
| Bot | Profile Days | Buffer | RSI Filter |
|-----|------------|--------|-----------|
| E20-1 | 30d | 0% | None |
| E20-2 | 60d | 0% | None |
| E20-3 | 90d | 0% | None |
| E20-4 | 30d | 0.5% | RSI < 35 |
| E20-5 | 60d | 0.5% | RSI < 35 |
| E20-6 | 90d | 0.5% | RSI < 35 |
| E20-7 | 60d | Value Area Low | None |
| E20-8 | 90d | Value Area Low | RSI < 30 |
| E20-9 | 90d | VPOC - 1% | RSI < 40 |

### E21 — Fair Value Gap (9 bots)
Logic: 3-candle imbalance zone · price fills gap
| Bot | Timeframe | Fill Depth | Volume |
|-----|---------|-----------|--------|
| E21-1 | 1h | 25% | None |
| E21-2 | 1h | 50% | None |
| E21-3 | 1h | 100% | 1.2x |
| E21-4 | 4h | 25% | None |
| E21-5 | 4h | 50% | None |
| E21-6 | 4h | 100% | 1.5x |
| E21-7 | 4h | 50% | 2.0x |
| E21-8 | 12h | 50% | None |
| E21-9 | 12h | 100% | 1.2x |
Fixed: Price above EMA200 · Max gap age 7 days

### E22 — Hammer/Engulfing at Support (9 bots)
Logic: Pure price action candle pattern at support level
| Bot | Pattern | Wick Ratio | Support Proximity |
|-----|---------|-----------|-----------------|
| E22-1 | Hammer | 2.0x | 0.5% |
| E22-2 | Hammer | 2.5x | 0.5% |
| E22-3 | Hammer | 3.0x | 0.5% |
| E22-4 | Hammer | 2.0x | 1.0% |
| E22-5 | Hammer | 2.5x | 1.0% |
| E22-6 | Hammer | 3.0x | 1.0% |
| E22-7 | Engulfing | Full | 0.5% |
| E22-8 | Engulfing | Full | 1.0% |
| E22-9 | Engulfing | Full | 2.0% |
Fixed: Uses E12 support detection algorithm

### E23 — Relative Strength vs BTC (9 bots)
Logic: Coin outperforms BTC while both falling = hidden accumulation
| Bot | Lookback | Min Outperform | RSI Max |
|-----|---------|--------------|--------|
| E23-1 | 24h | +2% | 40 |
| E23-2 | 24h | +4% | 40 |
| E23-3 | 24h | +6% | 40 |
| E23-4 | 48h | +2% | 45 |
| E23-5 | 48h | +4% | 45 |
| E23-6 | 48h | +6% | 45 |
| E23-7 | 72h | +2% | 50 |
| E23-8 | 72h | +4% | 50 |
| E23-9 | 72h | +6% | 50 |
Calculation: coin_return_Nh - btc_return_Nh > threshold

### E24 — Funding Rate Extreme (9 bots)
Logic: Perpetual futures funding very negative = short squeeze imminent
| Bot | Funding Threshold | RSI | Lookback |
|-----|-----------------|-----|---------|
| E24-1 | -0.05% | 35 | Current |
| E24-2 | -0.10% | 35 | Current |
| E24-3 | -0.15% | 35 | Current |
| E24-4 | -0.05% | 40 | Current |
| E24-5 | -0.10% | 40 | Current |
| E24-6 | -0.15% | 40 | Current |
| E24-7 | -0.05% | 35 | 8h avg |
| E24-8 | -0.10% | 35 | 8h avg |
| E24-9 | -0.15% | 40 | 8h avg |
Data: CCXT fetchFundingRate() · perp markets only
Tag: data_sparse_expected for non-perp coins

### E25 — Supertrend + RSI (9 bots)
Logic: Supertrend bullish + RSI oversold = trend-confirmed pullback
| Bot | ATR Period | ATR Multiplier | RSI Max |
|-----|-----------|--------------|--------|
| E25-1 | 10 | 2.0 | 30 |
| E25-2 | 10 | 2.5 | 35 |
| E25-3 | 10 | 3.0 | 40 |
| E25-4 | 14 | 2.0 | 30 |
| E25-5 | 14 | 2.5 | 35 |
| E25-6 | 14 | 3.0 | 40 |
| E25-7 | 20 | 2.0 | 30 |
| E25-8 | 20 | 2.5 | 35 |
| E25-9 | 20 | 3.0 | 40 |
Fixed: Supertrend must be bullish (green) at entry

### E26 — Ichimoku Cloud Simplified (9 bots)
Logic: Kumo cloud only · price below cloud + future cloud bullish + RSI
Note: data_sparse_expected_TRUE (rare setup)
| Bot | Conversion | Base | RSI Max |
|-----|-----------|------|--------|
| E26-1 | 9 | 26 | 35 |
| E26-2 | 9 | 26 | 40 |
| E26-3 | 9 | 26 | 45 |
| E26-4 | 12 | 30 | 35 |
| E26-5 | 12 | 30 | 40 |
| E26-6 | 12 | 30 | 45 |
| E26-7 | 9 | 26 | 35 |
| E26-8 | 12 | 26 | 35 |
| E26-9 | 9 | 30 | 40 |
Fixed: Price below cloud + future cloud bullish · Kumo only

### Research Bot Totals (LOCKED)
Method bots: 256
Benchmarks: 5
Total: 261 bots
Short research: 261 bots × 5 coins (BTC·ETH·BNB·SOL·XRP)
3 separate Short regime champions (independent from Long)
is_research_account=TRUE → no trade limit ever

## New Decisions — Post Session 5 Customer & Owner Review (LOCKED)

### Customer Dashboard — Performance Stats (LOCKED)
Add to Tab 1 Dashboard (top section):
Total profit since joining: $847.20
This month: +$234 vs last month: +$189 (+24%)
Win rate trend: 67% → 71% (improving ✅)
Best coin ever: BTC +$380 (8 trades)
Worst coin ever: RVN -$23 (3 trades)
Motivational line: "Your bots have made you $847 since March"
Updated: every time a trade closes

### PWA + Widget (LOCKED)
PWA install: Phase 6 (already planned)
→ Install from browser · no app store
→ Home screen icon · push notifications
→ Works iOS + Android

Native home screen widget:
→ Phase 8+ only (if users request it)
→ Not worth complexity for Phase 1-7
→ Telegram notifications replace widget perfectly

### Monthly Health Report — Cost Per User (LOCKED)
Add to monthly summary report:
Server: €17.99/mo · Active users: 12
Cost per user: €1.50
Fees collected: $456 · Revenue per user: $38
Profit margin: [calculated]
Helps owner know when to upgrade server
Helps owner know platform economics

### Users Tab — Last Active Column (LOCKED)
Add to Users table:
Last Active column (after Status)
Shows: "2h ago" · "3 days ago" · "45 days ago"
Color coding:
🟢 Green: < 7 days (active)
🟡 Yellow: 7-30 days (quiet)
🔴 Red: > 30 days (at risk of churn)
Sortable by Last Active column

### Paper Trade Limit System (LOCKED)
Default paper limit: admin sets globally (not hardcoded)
Launch phase: admin sets 999 (effectively unlimited)
Growth phase: admin reduces as needed
Stable phase: admin sets to 30 or any number

Admin Controls tab:
Global paper limit: [999] [Save]
Applies to: new users only
Existing users: unaffected when global changes

Per user override (Users tab):
Paper: 47/999 [Set custom limit]
Custom limit overrides global for that user only
Use case: abusive user → set to 5
Use case: beta tester → keep at 999

Admin Users tab shows per user:
Paper trades used: 47/999
[Edit paper limit] button

### Public Results Page (LOCKED)
URL: averionbot.com/results
Default: HIDDEN (404 redirect to home)

Admin Controls tab toggle:
[Results page: HIDDEN ↔ VISIBLE]

When visible · per-stat toggles:
☑ Total trades: 12,847
☑ Platform win rate: 67%
☑ Average profit per trade: +3.2%
☑ Current champion: E11-3 (QFL Base Bounce)
☑ Champion RARS score: 0.745
☑ Weeks as champion: 8
☐ Active users (hide when small)
☐ Total registered users (hide when small)

Admin shows only good numbers at start.
More stats visible as platform grows.
No competitor does this → trust builder.
Auto-updated every Sunday from research report.

---

## Registration & Anti-Fraud System — Final (LOCKED)

### Registration Flow (LOCKED)
Step 1: Register
→ Username
→ Email
→ Password
→ Confirm password

Step 2: Verify email
→ Code sent to email
→ Enter code manually OR click link
→ Done · trading enabled immediately
→ No phone · no Telegram · no friction
→ Same as any normal platform

### Exchange UID Fingerprint (LOCKED · Silent)
When user connects exchange API:
→ UID captured automatically (invisible to user)
→ Stored in uid_fingerprint column
→ User never knows · never sees it
→ Duplicate exchange account → blocked silently

UID availability per exchange:
✅ Reliable: Binance · KuCoin · OKX · Bybit · Gate.io
⚠️ Uncertain: MEXC · Bitget (test on Hetzner Day 3)
If UID unavailable: store NULL · flag as unverified
Admin sees: UID verified count per user

### Admin Risk Detection (LOCKED)
Users tab shows per user:
ID | Username | Exchanges | UID verified | Trades | Last Active | Risk

Risk scoring (automatic):
🟢 Low: multiple exchanges · UID all verified
🟡 Medium: 1 exchange · UID uncertain
🔴 High: MEXC only · UID 0 · 100 trades · new account

Examples:
User A: 4 exchanges · UID 4/4 ✅ · 67 trades → 🟢 Serious trader
User B: 1 MEXC · UID 0/1 ⚠️ · 100 trades → 🔴 Watch
User C: 1 MEXC · UID 0/1 ⚠️ · 100 trades → 🔴 Watch

Admin suspicion triggers:
→ B + C: same IP? Same device? Same day?
→ Same trading pattern?
→ MEXC only + UID unverified + max trades

### Phone Verification — On Demand (LOCKED)
Admin triggers per suspicious user:
[Require Phone Verification] button in Users tab

User sees on next login:
"Verify your phone number to continue trading"
→ Enter phone number
→ Receive SMS code
→ Verify → trading resumes immediately

If user refuses:
→ Cannot open new trades until verified
→ Account stays active but frozen
→ Existing positions: TP always fires (never blocked)
→ Existing positions: DCA continues

Phone stored as hash (GDPR safe · never shown):
→ Same phone already exists → flag admin
→ B + C same phone = confirmed duplicate
→ Admin suspends duplicate account

### SMS Service Timeline (LOCKED)
Phase 1-6: admin-triggered manually only
→ No monthly subscription cost
→ Only when suspicious pattern detected
→ Expected: 5-10 cases maximum at small scale

Phase 7 (public launch · stable income):
→ Subscribe to Twilio or similar service
→ Cost: ~$0.01 per SMS
→ Only pay per use · no monthly minimum
→ Budget: $5-10/month at small scale

### Debt Cap System (LOCKED)
Maximum debt per user: $100
When debt reaches $100:
→ Pause ALL trading (new positions + DCA)
→ TP always fires (never blocked · ever)
→ Telegram alert: "Debt $100 reached · top up to resume"
→ Dashboard: large red banner with [Top Up Now]

Abandoned account with debt:
→ Account stays in DB with debt forever
→ Email reminder: day 30 · day 90 · day 180
→ After 180 days inactive → flag: ABANDONED_DEBT
→ After 2 years → write off · anonymize data
→ Small amounts not worth legal action

### Telegram (LOCKED · Optional Forever)
Telegram = optional · for notifications only
Never required · never mentioned as security
Connect for better notifications → user choice
If connected: Telegram phone hash stored as bonus layer
If not connected: email notifications only · no penalty

### Anti-Fraud Layers Summary (UPDATED)
Layer 1: Email verification at registration
Layer 2: Exchange UID fingerprint (silent · strongest)
Layer 3: Reserve wallet $10 minimum
Layer 4: IP + device fingerprint
Layer 5: Cross-exchange blacklist
Layer 6: Admin risk scoring (new)
Layer 7: Phone verification on demand (new)

---

## Short DCA — Complete Flow (LOCKED)

### Philosophy
Short DCA = mirror image of Long DCA
Long:  Buy → average DOWN on drops → sell high
Short: Sell → average UP on rises → buy low

### Entry
Bot sells initial coin amount at MARKET price
Example: sell 1000 RVN at $0.030 = $30 USDT collected

### Averaging (price rises = sell more)
If price RISES by spacing% → sell more coin
Each additional sell = at higher price
= Improves average sell price
Example:
Entry sell: $0.030
Price +10% → sell more at $0.033
Avg sell price: $0.031 (improved)

### TP (limit BUY below entry)
TP = limit buy order placed BELOW entry price
When price drops to TP → buy back ALL coin cheaper
Example: TP buy at $0.027
Profit = $0.031 avg sell - $0.027 buyback = +$0.004/coin

### Profit Currency (LOCKED · same as Long)
User chooses at bot creation:
USDT: profit kept as USDT
RVN: profit converted back to RVN

Both Long and Short support both currencies
Same toggle · same logic · no difference

### Bot Never Stops
Long runs out of USDT → keeps trying every 60s
Short runs out of coin → keeps trying every 60s
When funds available → resumes automatically
Never force-closes · never gives up
TP always fires regardless of balance

### Spacing (same formula as Long)
Short spacing = how much price rises between sells
Same ATR calculation · same classification
Same 25/25/25/25 weighted window
Same dynamic scalar · same percentile ranges
Category limits apply as emergency backstop

### Fee Deduction
When buyback fills (Short closes):
profit = total USDT collected - buyback cost
20% fee deducted immediately from reserve wallet
Loss close = $0 fee (never charged on losses)
Same system as Long · no difference

### Insufficient Coin During Averaging
If user runs out of coin:
→ Cannot execute averaging sell
→ Bot keeps trying every 60s
→ When coin available → averaging resumes
→ TP still fires on whatever was sold
→ Admin alert: "Short bot: insufficient coin balance"

---

## Copy Trade — Complete Spec (LOCKED)

### Setup
Admin connects MEXC User #13326:
→ Selects which of YOUR MEXC wallets to use
→ Sets YOUR fixed order size (e.g. $20)
→ All user bots = followed by default [ON]

### Normal Behavior (follow user exactly)
User opens trade → you open same coin immediately
User's DCA fires → your DCA fires (same spacing as user)
User's TP hits → your TP hits (same TP as user)
You mirror EVERYTHING the user does
Your order size = your fixed $ amount always
User changes params → applies to YOUR new trades only
Existing open copies → keep original params forever

### Exception: User Closes at LOSS (manual)
You do NOT follow the close
Your position becomes standalone Smart DCA
NOW uses YOUR coin classification:
→ Your spacing from own coin data
→ Your TP from own coin data
→ Your trailing from own coin data
→ Joins your MEXC queue
→ TP from YOUR avg cost
→ Treated as normal Smart DCA trade forever

### Simple Rule
Profit close → follow user ✅
Loss close → don't follow · switch to your classification ✅

### Per Bot Toggle
Each bot under copied exchange shows:
[Follow: ON ●] default = ON
→ OFF = don't copy new opens from this bot
→ Existing copies: stay open as standalone Smart DCA
→ Never force-closed

### Order Size Change
Admin changes $20 → $30:
→ New copies use $30
→ Existing open copies: keep original $20 forever

### No Funds Available
Skip copying until funds available
When funds available → resume copying new opens
Cannot copy past missed entries (no catch-up)

### Remove Copied Exchange
Admin removes MEXC copy entirely:
→ All copied positions → standalone Smart DCA
→ Join MEXC queue automatically
→ No forced closes
→ Platform handles everything
→ TP from YOUR avg cost
→ YOUR classification for spacing

### What Copies
✅ Coin (same coin as user)
✅ Direction (Long or Short)
✅ Entry timing (same time as user)
✅ DCA timing (same time as user)
✅ TP timing (same as user if profitable)
✅ Entry method changes (new trades only)

### What Does NOT Copy
❌ User's capital amount (you use your fixed $)
❌ User's profit currency (you use your setting)
❌ Loss closes (you stay open → Smart DCA)
❌ User's reserve balance

### Profit
When copy trade closes with profit:
20% fee on YOUR profit → from YOUR reserve wallet
Same fee system as all other trades

---

## Short DCA — Updates & Corrections (LOCKED)

### All Exchanges Simultaneously (LOCKED · updated)
Short DCA launches on ALL 7 exchanges at once
Previous note "MEXC first" = OUTDATED · DELETED
Same as Long DCA implementation
One codebase · all exchanges · Phase 5

### Limit Order Check Frequency (LOCKED · updated)
Previous: hourly cron check for missing limit orders
Updated: check EVERY 60 SECONDS for PENDING_BUYBACK
Reason: 1 hour gap = price can hit TP and recover
= user misses profit entirely

Implementation:
Bot loop every 60s checks:
If position has PENDING_BUYBACK = TRUE:
→ Verify limit buy order still active on exchange
→ If missing: replace immediately
→ Do NOT wait for hourly cron

Hourly cron: still runs as backup verification
60s check: primary protection

### Spacing = Same Formula as Long (LOCKED)
Short spacing uses identical formula to Long:
Level 1: activation_price × (1 + DCA%)
Level 2+: last_sell_price × (1 + DCA% × multiplier^level)

Reason: coin volatility same in both directions
ATR measures both up and down equally
Consistent · predictable · no special handling

### Short Research Bots (LOCKED · Phase 5)
Same 261 methods as Long
But coin universe = 5 coins only:
BTC · ETH · BNB · SOL · XRP
Research account pre-holds all 5 coins
3 separate Short regime champions
Independent from Long champions
Added to research_bots.json when Phase 5 begins

### Profit Currency (LOCKED · both directions)
Long profit: USDT or base coin (user picks)
Short profit: USDT or base coin (user picks)
Both directions = same toggle · same logic
No difference between Long and Short

### Bot Never Stops (LOCKED · both directions)
Long runs out of USDT → keeps trying every 60s
Short runs out of coin → keeps trying every 60s
When funds available → resumes automatically
Never force-closes · never gives up
TP always fires regardless of balance

### Short DCA Complete Flow Summary
1. User holds coin on exchange
2. Bot entry: MARKET sell initial amount
3. Price rises → bot sells more (MARKET) at spacing intervals
4. Each sell: recalculate avg sell price + new TP target
5. TP target = avg_sell_price × (1 - TP%)
6. Place/update LIMIT buy order at TP target
7. Exchange reserves USDT for buyback
8. Price drops to TP → limit buy fills
9. Profit = total USDT collected - buyback cost
10. 20% fee on profit immediately
11. Position closed · user gets coin back + profit

---

## Short DCA Parameter System — Final (LOCKED)

### Philosophy
Short DCA = complete mirror of Long DCA
Identical system · opposite direction measurement

### Regime Multipliers (REVERSED from Long)
Long:  Strong Bull 1.10 · Bull 1.05 · Sideways 1.00 · Bear 0.90 · Strong Bear 0.85
Short: Strong Bull 0.85 · Bull 0.90 · Sideways 1.00 · Bear 1.05 · Strong Bear 1.10

Reason: Short profits when price drops
Bear = Short's best regime (ride longer)
Bull = Short's worst regime (exit fast)

### Spacing (per-coin independent)
Measured from coin's OWN RISE history
(not drop history like Long)
Same formula: ATR × dynamic scalar
Same 25/25/25/25 weighted window
Same 10th-90th percentile ranges
Same 20% daily change limit
Same dynamic ATR scalar (1.2-3.0)

### TP (per-coin independent)
Measured from coin's reversal after rise
Regime multiplier REVERSED (see above)
Same daily 20% change limit
Same floor/ceiling percentile ranges

### Trailing
Same formula as Long
20th percentile of post-TP extensions
Same limits and floors

### Size Multiplier
Same volatility-based formula
Same power scaling (^0.7)
Same category limits

### Classification
Same 5 categories (Mega/Large/Mid/Small/Micro)
Same emergency limits per category
Same cap protection (+10% up · immediate down)
Same confidence system (0-30 · 30-90 · 90+ days)

### Smart DCA Champions (3 separate Short champions)
Bull Short Champion (separate from Long)
Bear Short Champion (separate from Long)
Sideways Short Champion (separate from Long)
Same RARS formula · same 3-tier promotion
Same circuit breaker (40% drawdown)
Independent auto-switching

### Research System
261 Short research bots
Coin universe: 5 coins only (BTC · ETH · BNB · SOL · XRP)
Research account pre-holds all 5 coins
Same 27 methods tested for Short behavior
Results independent from Long research

### One Difference Only
Long spacing = from coin's DROP history
Short spacing = from coin's RISE history
Everything else: identical

---

## Session Final Decisions (LOCKED)

### 1. Account Cancellation Flow
Settings → Danger Zone → [Close Account]

Warning shown:
"You have X open positions across Y exchanges"
No email confirmation required

3 options:
A: [Close All Positions + Delete Account]
   → Market sells ALL positions immediately
   → 20% fee on any profits
   → Account deleted after all closed

B: [Keep Positions Open + Delete Account]
   → Bots stop opening new trades
   → Existing positions: TP still fires always
   → Reserve keeps running until empty
   → Account deleted after ALL positions closed naturally
   → May take weeks/months

C: [Cancel] ← default

After deletion:
→ All bots deactivated
→ API keys removed from DB
→ Personal data anonymized (GDPR)
→ Trade history kept forever (financial records)
→ Reserve wallet balance: NON-REFUNDABLE
→ Debt: stays in DB forever
→ Same exchange: blocked (UID fingerprint)

### 2. History Tab — By Trade + By Coin (LOCKED)
Two toggle views:
[Trades] ← default · existing behavior
[By Coin] ← new view

By Coin view:
Coin | Trades | Win% | Avg DCAs | Net Profit$ | P&L% | Avg Days
Sortable by any column
Same filters as Trades view (exchange · date · direction)
Summary bar: totals across all coins
No new tables needed · pure SQL aggregation

### 3. FAILURE_SCENARIOS.md (LOCKED)
Created: docs/FAILURE_SCENARIOS.md
Covers all failure scenarios + recovery steps
Share with AI when investigating issues
See file for full content

### 4. Scale Upgrade Path (LOCKED)
Server alone not sufficient at large scale.
Full stack upgrade required at milestones:
100 users: CX33 + pgBouncer
500 users: CX53 + dedicated DB + read replicas
2000 users: multiple app servers + load balancer
10000+: full cloud infrastructure
See FAILURE_SCENARIOS.md for full scale path

### 5. Short DCA 60s Limit Order Check (LOCKED)
PENDING_BUYBACK checked EVERY 60s in bot loop
NOT hourly · every single loop cycle
If limit buy missing → replace immediately
Most critical protection for Short DCA

### 6. Landing Page Structure (LOCKED · content later)
Section 1: Hero ("funds stay yours · pay only when you win")
Section 2: 3 trust cards (non-custodial · 20% on profit · set&forget)
Section 3: How it works (3 steps)
Section 4: Smart DCA — NO parameters shown
  "We test hundreds of strategies on real data daily.
   Best performer becomes your Smart DCA automatically.
   No tuning needed. Data decides."
Section 5: Features grid (7 exchanges · Long+Short · alerts etc)
Section 6: Pricing (free + add-ons)
Section 7: FAQ
Section 8: CTA
Full content: separate session

### PostgreSQL Connection Pooling (LOCKED)
pgBouncer installed on Day 2 (hetzner_day2.sh)
Pool settings:
max_client_conn = 200
default_pool_size = 20
pool_mode = transaction
App connects to pgBouncer port 6432
pgBouncer manages real DB connections
Cost: free · Ubuntu package

---

## Phase Roadmap — Updated Final (LOCKED)

### Short DCA = NOT a separate phase (LOCKED)
Short DCA is identical system to Long DCA.
Mirror image · same code · same logic · same day.
Launches TOGETHER with Long DCA on Day 3.
No separate implementation phase needed.

### Day 3 Research Bot Launch (UPDATED)
261 Long research bots (E1-E26 + E18b + benchmarks)
261 Short research bots (same 27 methods · 5 coins)
Total Day 3: 522 research bots simultaneously

Short research coins: BTC · ETH · BNB · SOL · XRP
Research account pre-holds all 5 coins before Day 3.
3 Short champions (independent from Long champions).

Server recommendation:
Start on CX33 (€17.99/mo · 4 vCPU · 8GB)
522 bots = significant load on CX23
Better to start right than upgrade under pressure.

Monitor 24 hours after launch:
→ Loop < 30s: stable ✅
→ Loop 30-50s: investigate
→ Loop > 50s: investigate immediately

### Limit Orders = Already Built (Day 1)
Optional per bot in wizard Step 3.
Not a separate phase.
Available from Day 1 for both Long + Short.

### Sequential Gates = Already Built (Day 1)
In wizard Step 4.
Not a separate phase.
Available from Day 1.

### Phase 5 — Redefined (LOCKED)
Phase 5 = UI/feature improvements after
30+ days stable paper trading.

Includes:
→ Copy trade system (admin copies user)
→ Public results page (averionbot.com/results)
→ Performance by coin view (History tab)
→ Bot health score display
→ "Why did my bot buy?" panel
→ Advanced sequential gate UI improvements
→ Strategy marketplace foundation (Phase 8)

NOT includes (already built):
→ Short DCA (done · Day 1)
→ Limit orders (done · Day 1)
→ Sequential gates (done · Day 1)

### Phase Summary (FINAL)
Phase 4: Hetzner setup (Days 1-3)
Phase 4.5: Personal live trading (Day 45+)
Phase 5: UI features + copy trade (Day 60+)
Phase 6: First customers (Month 6+)
Phase 7: Public launch (Month 6-12)
Phase 8: Marketplace (Year 2)

### Remove All "MEXC First for Short" References
Old note "Short DCA = MEXC first · then KuCoin" = DELETED
All exchanges simultaneously from Day 3.
Same as Long DCA.
No exchange priority for Short.

### Paper Research for Short (LOCKED)
Short research bots run from Day 3.
Same paper trading system as Long.
Admin research account holds 5 coins.
RARS scoring identical formula.
Regime multipliers REVERSED for Short.
Results after 50+ trades per method.
Short champion auto-switches independently.

---

## Short DCA Research — Virtual Coin Balance (LOCKED)

### Problem
Short DCA requires holding coin to sell.
Paper mode uses virtual USDT (unlimited).
Cannot "paper hold" real BTC or ETH.
No real coin purchase needed.

### Solution: Option A — Virtual Coin Balance
Research account has two virtual balances:

Long research:
virtual_usdt_balance = unlimited (already works)

Short research:
virtual_coin_balances = {
 BTC: 10.0 (virtual · auto-refills)
 ETH: 100.0 (virtual · auto-refills)
 BNB: 500.0 (virtual · auto-refills)
 SOL: 1000.0 (virtual · auto-refills)
 XRP: 100000.0 (virtual · auto-refills)
}

### How It Works
Short research bot sells:
→ Deducts from virtual_coin_balances
→ MARKET sell simulated (no real exchange order)
→ Records price at time of signal
→ If virtual balance empty → refills automatically
→ Never touches real exchange
→ Never touches real money

Long research bot buys:
→ Uses virtual_usdt_balance
→ Already works this way ✅

Both sides fully simulated.
Consistent · clean · no real money needed.

### No Pre-Buy Required
Day 2 checklist: NO coin pre-buy needed.
Research account = fully virtual both directions.
Zero real money for research.

### Schema Addition
Table: research_virtual_balances
Fields:
 research_account_id INTEGER
 coin VARCHAR(20) (BTC · ETH · BNB · SOL · XRP)
 virtual_balance DECIMAL(20,8)
 auto_refill BOOLEAN DEFAULT TRUE
 refill_amount DECIMAL(20,8)
 last_refilled TIMESTAMP

Auto-refill trigger:
When virtual_balance < 10% of refill_amount:
→ Refill to full amount automatically
→ Log refill event in research_trades table
→ Does not affect RARS scoring
→ Ensures research never stops

### Customer Short DCA (DIFFERENT · REAL)
Customer Short bots:
→ Must hold REAL coin on exchange
→ Bot checks real balance before every sell
→ If insufficient: Telegram alert · skip · retry
→ No virtual balance · real exchange only

Research Short bots:
→ Virtual coin balance only
→ Never touches real exchange
→ Fully simulated

These are completely separate systems.

---

## Short Research Bot Count — Final (LOCKED)

### Structure
261 methods × 5 coins = 1,305 Short bot instances
Results COMBINED per method across all 5 coins
One RARS score per method (not per coin)
3 Short champions (Bull · Bear · Sideways)
Independent from Long champions

### Total Day 3
Long research:  261 bot instances (across 300+ coins)
Short research: 1,305 bot instances (261 × 5 coins)
Grand total:    1,566 bot instances

### Staged Launch (LOCKED)
Day 3 morning: launch 261 Long bots first
Day 3 afternoon: if loop < 30s → launch 1,305 Short bots
Day 4: assess loop time → upgrade server if needed

### Server Recommendation
Start on CX33 from Day 1 (€17.99/mo · 4 vCPU · 8GB)
CX23 borderline for 1,566 bots
CX33 comfortable · cheap insurance
CX43 only if loop > 30s consistently after CX33

### Open Trades vs Bot Instances
1,566 bots ≠ 1,566 open trades
Open trades = DB records only (not heavy on server)
Server load = signal checking + price fetching + DB queries
Not all bots fire simultaneously
Realistic open positions: 10-20% of bots at any time
