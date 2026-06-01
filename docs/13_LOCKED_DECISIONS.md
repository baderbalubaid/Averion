# Locked Decisions

> These decisions are FINAL. Do not re-suggest, re-discuss, or modify without Bader explicitly saying "discuss this decision". AI must respect all decisions below.

---

## Trading Logic

- DCA spacing calculated from LAST BUY PRICE — never average cost
- Market orders ONLY — no limit orders ever — no exceptions
- Trailing safety (Smart DCA only): if TP% - Trail% < 1% → direct market TP
- NO maximum DCA levels — smart queue handles capital allocation forever
- Bot NEVER stops running — detects new funds within 60 seconds
- Open positions update IMMEDIATELY on reclassification (Option B)
- One pair per bot — no duplicate coin on same bot — cross-bot is fine
- Paper stays paper FOREVER — live stays live — NO conversion ever
- Short DCA = spot only — user must already hold the coin — min exchange order size required
- Profit coin = user chooses USDT or base coin — works for both Long and Short
- All slippage handling uses market orders only — no limit orders

## Slippage Handling
- Check order book depth before every DCA
- If available quantity at target price >= $1 minimum → buy at target price
- If available quantity < $1 minimum → buy $1 market order (max slippage = $1)
- Never chase price more than $1 above target
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
- Timer resets when ANY live position opens

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
- Switch back to PRIVATE when averion.app launches publicly
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

## Entry Method Promotion Criteria (Point 7 — Pending AI Review)

- Promotion score = Win Rate x Avg Profit x Recovery Speed / Max Drawdown
- Promote to Smart DCA default IF:
  - Minimum 100 trades recorded
  - Tested across 3+ market regimes (bull · bear · sideways)
  - Score beats E10 control group
  - Score beats Simple DCA benchmark
  - 30 day cooldown passed
- Delete IF:
  - 3 consecutive quarterly reviews failed
  - Win rate < 40% consistently
  - Underperforms E10 control group
- NOTE: Share this formula with AIs for validation before implementing
- NOTE: Get recommendations from ChatGPT + Gemini on scoring weights

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

- 3 separate channels per customer:
  - Trades: every buy · sell · DCA · TP (mute-friendly)
  - Alerts: reserve low · bot stopped · ST flag · urgent (never mute)
  - Reports: daily per exchange · weekly · monthly
- Customer connects in Settings tab → Notifications section
- Enter Telegram Chat ID → bot sends verification code → confirmed
- Each channel has separate toggle ON/OFF
- Customer controls which channels they receive

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

- User creates named virtual wallets per exchange
- Example: Long Test 1 · Short BTC · RVN Wallet
- Each wallet: name · currency · capital amount or All
- Bot links to one wallet (changeable anytime)
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
- Tested across 3+ market regimes
- Score beats E10 control group
- Score beats Simple DCA benchmark
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
- ALL Long DCA bots on same exchange → HOLD new DCAs
- Hold lasts until limit buy order confirmed by exchange (~2 seconds)
- Then Long DCA resumes normally
- Prevents queue grabbing Short funds during placement delay

Priority Order (same exchange · same wallet):
1. Short DCA buyback (always first)
2. TP exits (free capital immediately)
3. Long DCA queue (normal scoring)

## Reserve Wallet Debt System (LOCKED)

- Bot NEVER stops when reserve = $0
- Position closes at TP normally regardless of reserve balance
- Fee recorded as debt in DB if reserve insufficient
- Debt shown clearly in dashboard with [Top Up Now] button
- When user tops up: debt deducted first · remaining = new balance
- Telegram: debt cleared notification sent
- Debt accumulates until reserve funded
- No blocking · no stopping · no forced actions ever

Debt Data Retention:
- Active unpaid debt: kept forever until paid
- Paid debt history: kept FOREVER
- Reason: financial records · tax · dispute resolution
- Never deleted regardless of account status

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
- Weekly Sunday cron: attempt to sell all dust combined
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
- pip install ccxt safe upgrade (test then apply)
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
- 107 research bots launched
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
- Long DCA checks flag at start of each cycle
- If PENDING_BUYBACK = TRUE → skip this cycle
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
Phase 7 public launch: add FastAPI middleware
- 60 requests/minute per token
- Easy to add · leave for Phase 6 preparation

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
- Implement when averion.app domain is ready (Day 2)
- Sender email: noreply@averion.app

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
