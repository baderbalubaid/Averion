## CLAUDE FIRST ACTION — Read These Files First

> Every new Claude session must fetch these files immediately before responding.

- https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/00_START_HERE.md
- https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/13_LOCKED_DECISIONS.md
- https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/03_TRADING_SYSTEM.md
- https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/04_RISK_AND_SAFETY.md
- https://raw.githubusercontent.com/baderbalubaid/Averion/main/docs/05_SMART_DCA_ENGINE.md
- https://raw.githubusercontent.com/baderbalubaid/Averion/main/setup/schema.sql

# Averion — Start Here

## What Is Averion
Public automated crypto DCA trading platform.
Runs 24/7 on Hetzner cloud server.
Built for public launch with 20% performance fee model.
Users keep funds on their own exchange — Averion never holds assets.

## Current Status
- Phase 1 ✅ Phase 2 ✅ Phase 3 ✅ Phase 3.5 ✅
- Items 1-26 ✅ ALL REPLIT ITEMS COMPLETE
- All core Python code written and pushed to GitHub
- All frontend pages complete
- Waiting for Hetzner server (ID verification pending)

## Code Written (Ready for Hetzner)
- database.py — PostgreSQL · 1015 lines · 57 functions
- api.py — FastAPI · 877 lines · 30+ endpoints
- main.py — Startup sequence · PostgreSQL + Redis wait
- bot_loop.py — Trading engine · smart queue · TP · DCA
- exchanges.py — CCXT wrapper · all 7 exchanges · Fernet decrypt
- telegram.py — Notifications · alerts · reports · verification
- auth.py — Login · session · brute force · registration
- index.html — Homepage · marketing · pricing
- login.html — Sign in · forgot password · verification
- register.html — Sign up · password strength · email check
- dashboard.html — Customer trading dashboard
- admin.html — Admin control panel · 1316 lines

## Credentials
- GitHub: github.com/baderbalubaid/Averion
- Token: ASK_BADER_FOR_TOKEN
- Replit Dashboard: https://bbd72f98-d728-46fe-81c6-af97d0011150-00-1c2g4v036wde1.sisko.replit.dev/dashboard
- Hetzner: CX23 · Helsinki · Ubuntu 24.04 · €3.99/mo · ID verification pending

## User Note
Bader is NOT a coder.
All coding done via Replit terminal commands only.
Claude must provide exact copy-paste commands.
One command at a time. Verify each result.
Never ask user to edit files manually.
Build everything public-ready from Day 1 — not personal then upgrade.

## Core Philosophy
Survivability first · Controlled recovery second · Profit third
Build once · Build right · Public platform from Day 1

## Reading Order For New Claude
1. 00_START_HERE.md (this file)
2. 13_LOCKED_DECISIONS.md (all locked rules)
3. 16_TODO_HETZNER.md (next steps on server)
4. 03_TRADING_SYSTEM.md (how bot trades)
5. 04_RISK_AND_SAFETY.md (protection systems)
6. 05_SMART_DCA_ENGINE.md (smart engine)
7. 06_BUSINESS_MODEL.md (fees and payments)
8. Remaining files as needed

## 18 Rules Never To Break
1. DCA spacing from LAST BUY PRICE — not average cost
2. Market orders ONLY — exception: Short DCA buyback uses limit order to reserve funds
3. 20% fee on REALIZED profits only — loss months = $0
4. User funds ALWAYS on their exchange — Averion never holds
5. Paper stays paper FOREVER — live stays live — no conversion
6. Settings tab = account info ONLY — bot config in wizard
7. Cap protection: +10% max upward per day — full drop immediately
8. Classification automated daily — CoinGecko + CMC averaged
9. NO max DCA levels — smart queue handles capital forever
10. Bot NEVER stops — put money and forget it
11. Reclassification affects NEW positions only — existing keep original params
12. Smart DCA = fully automated — customers see results only
13. Trailing safety Smart DCA: TP%-Trail%<1% → direct market TP
14. One pair per bot — no duplicate coin on same bot
15. Paper max 30 of 100 — auto-close if no live trade 90 days
16. Reserve wallet = fee pre-funding ONLY — not trading capital
17. Exchange data for volume/OHLCV · CoinGecko+CMC for market cap
18. All code changes pushed to GitHub before ending any session

## File Structure
/docs
├── 00_START_HERE.md
├── 01_PROJECT_OVERVIEW.md
├── 02_BRANDING_AND_VISION.md
├── 03_TRADING_SYSTEM.md
├── 04_RISK_AND_SAFETY.md
├── 05_SMART_DCA_ENGINE.md
├── 06_BUSINESS_MODEL.md
├── 07_DASHBOARD_AND_UI.md
├── 08_BOT_CREATION_WIZARD.md
├── 09_INFRASTRUCTURE.md
├── 10_DATABASE_AND_API.md
├── 11_ADMIN_SYSTEM.md
├── 12_PHASE_ROADMAP.md
├── 13_LOCKED_DECISIONS.md
├── 14_AI_REVIEWS_AND_RESOLUTIONS.md
├── 15_TODO_REPLIT.md (complete — archive only)
└── 16_TODO_HETZNER.md (active — next steps)

/setup
├── schema.sql (651 lines · 28 tables)
├── hetzner_day1.sh (security hardened)
├── hetzner_day2.sh
├── DAY1_CHECKLIST.md
├── env.example
├── init_db.py
├── research_bots.json (107 bots)
└── launch_research_bots.py

/automation
├── daily_cron.sh
├── health_check.sh
├── fetch_coingecko.py
├── fetch_cmc.py
├── classify_coins.py
├── fetch_ohlcv.py
├── daily_aggregation.py
├── generate_metrics.py
├── generate_excel.py (9 sheets)
└── generate_diagnostics.py (auto-analysis)
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
- Implement when averionbot.com domain is ready (Day 2)
- Sender email: noreply@averionbot.com

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
# TODO — Hetzner Items

> Everything that requires the actual server.
> Do NOT attempt on Replit — server only.
> All commands run via SSH on Hetzner.
> Follow DAY1_CHECKLIST.md for exact sequence.

---

## Server Details
- Provider: Hetzner Cloud
- Plan: CX23 (4GB RAM · 2 vCPU · 40GB disk)
- Location: Helsinki, Finland
- OS: Ubuntu 24.04
- Cost: €3.99/month
- Status: Ordered · ID verification pending

---

## What Is Already Ready (Coded on Replit)

All code written · pushed to GitHub · ready to deploy:

| File | Status | Description |
|------|--------|-------------|
| database.py | ✅ Ready | PostgreSQL · 1015 lines · 57 functions |
| api.py | ✅ Ready | FastAPI · 877 lines · 30+ endpoints |
| main.py | ✅ Ready | Startup sequence · DB wait · reconciliation |
| bot_loop.py | ✅ Ready | Trading engine · smart queue · TP · DCA |
| exchanges.py | ✅ Ready | CCXT wrapper · 7 exchanges · encryption |
| telegram.py | ✅ Ready | Notifications · alerts · reports |
| auth.py | ✅ Ready | Login · session · brute force protection |
| index.html | ✅ Ready | Homepage · marketing |
| login.html | ✅ Ready | Sign in · forgot password |
| register.html | ✅ Ready | Sign up · password validation |
| dashboard.html | ✅ Ready | Customer trading dashboard |
| admin.html | ✅ Ready | Admin control panel |
| schema.sql | ✅ Ready | 651 lines · 28 tables |
| hetzner_day1.sh | ✅ Ready | Security hardened setup script |
| hetzner_day2.sh | ✅ Ready | Domain + HTTPS setup |
| DAY1_CHECKLIST.md | ✅ Ready | Step by step checklist |
| research_bots.json | ✅ Ready | 107 paper bots configured |
| launch_research_bots.py | ✅ Ready | Launch all 107 bots |
| daily_cron.sh | ✅ Ready | All automation scheduled |
| health_check.sh | ✅ Ready | Hourly monitoring |
| fetch_coingecko.py | ✅ Ready | CoinGecko market caps |
| fetch_cmc.py | ✅ Ready | CoinMarketCap market caps |
| classify_coins.py | ✅ Ready | Classification engine |
| generate_excel.py | ✅ Ready | 9-sheet Excel reports |
| generate_diagnostics.py | ✅ Ready | Auto-analysis markdown |

---

## Day 1 — Server Setup

> Run: bash setup/hetzner_day1.sh
> Full details in setup/DAY1_CHECKLIST.md

Covers automatically:
- System update + auto security updates
- PostgreSQL + Redis + Nginx + Fail2ban + Chrony
- SSH hardening (port 2847 · no root · keys only)
- UFW firewall (default deny)
- Clone GitHub repo
- Install Python packages
- Create database + run schema
- PM2 setup + startup
- Cron jobs installed
- File permissions

Manual steps after script:
- Fill in .env file
- Run init_db.py (create admin user)
- Add GitHub Actions secrets
- Setup UptimeRobot monitoring

---

## Day 2 — Domain & HTTPS

> Run: bash setup/hetzner_day2.sh

- Buy averionbot.com domain
- Point DNS A record to server IP
- Wait DNS propagation (1-24 hours)
- Run Day 2 script (Nginx + HTTPS + deploy keys)
- Setup Resend for email (resend.com · free 3,000/month)
- Test live $1 order on MEXC

---

## Day 3+ — Paper Trading

- 107 research bots running simultaneously
- Smart DCA entry methods testing (paper only)
- OHLCV data building hourly
- Classification running daily at 04:30
- Excel reports generated daily at 05:00
- Diagnostics auto-pushed to GitHub hourly
- Monitor admin dashboard daily
- Check Telegram alerts (never mute)

---

## Day 30+ — Parameter Optimization

- Download Excel from /reports/ folder
- Upload to Claude: analyze research bot rankings
- Share with ChatGPT for second opinion
- Apply best parameters
- Restart bot with optimized settings

---

## Day 45+ — Live Trading

- Set PAPER_MODE=false in .env
- Verify red LIVE banner in dashboard
- Place $1 test order on MEXC
- Verify order on exchange website
- Scale gradually with more capital

---

## Hetzner Items Status

| # | Task | Status |
|---|------|--------|
| 27 | Server creation + security | ⏳ Waiting for server |
| 28 | Clone GitHub + folder structure | ✅ Script ready |
| 29 | Create .env with all variables | ✅ env.example ready |
| 30 | PM2 start + startup + save | ✅ Script ready |
| 31 | Buy averionbot.com + DNS | ⏳ Day 2 |
| 32 | Nginx + HTTPS certificate | ✅ Script ready |
| 33 | Secret admin URL via .env | ✅ In api.py |
| 34 | Fernet API key encryption | ✅ In exchanges.py |
| 35 | GitHub Actions auto-deploy | ✅ deploy.yml ready |
| 36 | UptimeRobot monitoring | ⏳ Day 1 manual step |
| 37 | Telegram bot · one chat | ✅ In telegram.py |
| 38 | Cron jobs installed + tested | ✅ daily_cron.sh ready |
| 39 | OHLCV hourly fetch | ✅ fetch_ohlcv.py ready |
| 40 | Daily aggregation script | ✅ daily_aggregation.py ready |
| 41 | Diagnostics → GitHub daily | ✅ generate_diagnostics.py |
| 42 | Admin dashboard | ✅ admin.html ready |
| 43 | Excel daily report | ✅ generate_excel.py ready |
| 44 | Server capacity measurement | ⏳ Day 1-5 |
| 45 | Test live $1 order on MEXC | ⏳ Day 2 |
| 46 | Component toggles in admin | ✅ In admin.html |

---

## Daily Cron Schedule (LOCKED)



---

## Database Architecture (LOCKED)

Three layers:
- Redis: live prices in RAM · 60s refresh
- PostgreSQL: all data · 28 tables · proper indexes
- Archive: positions older than 1 year

---

## Server Scaling Plan (LOCKED)

- Start: CX23 €3.99/mo
- Measure loop time at 10→20→50→100→200 trades
- If loop > 30s → upgrade
- CX33: €7.49/mo · CX43: €16.49/mo · CX53: €32.99/mo

---

## Phase 5 Items (After Live Stable)

- Short DCA implementation
- Limit orders for entry and DCA
- Sequential trade gates
- Virtual wallet UI
- Full bot creation wizard
- Public user registration
- NOWPayments integration
- Split dashboard into separate files
# Trading System

> How Averion executes trades.
> All rules here are LOCKED unless explicitly discussed with Bader.

---

## Core Philosophy
- Survivability first
- Controlled recovery second
- Profit third
- Bot NEVER stops — put money and forget it

---

## Trading Modes

### Long DCA
- Price drops → buy more → lower average cost → sell at TP
- User does not need to hold coin first
- Bot opens position immediately on signal

### Short DCA
- User MUST already hold the coin on exchange
- Price rises → sell portions → raise average sell price
- Price drops back → buy all back cheaper
- Only sell if quantity >= exchange minimum order size
- No borrowing · no margin · no leverage · pure spot only

---

## Order Types
- Market orders ONLY — always — no exceptions ever
- No limit orders — no stale orders — guaranteed execution
- Guaranteed execution > perfect price — always

---

## DCA Logic

### Spacing Rule (LOCKED)
- Trigger = percentage drop from LAST BUY PRICE
- Never from average cost
- Never a fixed price threshold
- Always percentage-based check every 60 seconds

### Widening Geometry
- Each level spacing = previous spacing × SPACING_MULTIPLIER (default 1.4)
- Level 1: 7.0% drop
- Level 2: 7% × 1.4 = 9.8% drop
- Level 3: 9.8% × 1.4 = 13.7% drop
- Level 4: 13.7% × 1.4 = 19.2% drop
- Continues indefinitely — no max levels

### Size Escalation
- Each level size = previous size × SIZE_MULTIPLIER (default 1.5)
- Coin base multiplier from category (Mega=1.10x · Large=1.20x · Mid=1.35x · Small=1.50x · Micro=1.65x)
- Per level escalation: L1=1.0x · L2=1.2x · L3=1.4x · L4=1.6x · L5+=2.0x hard cap

---

## Take Profit System

### Trailing TP
- Arms when price reaches TP% above average cost
- Follows price up (locks X% below new peak always)
- Fires market sell when price pulls back TRAIL% from peak
- 100% position exit in one market order — no partial exits

### Trailing Safety Rule (Smart DCA Only)
- If TP% - Trail% < 1% → skip trailing → direct market sell at TP
- Prevents selling at breakeven or loss after fees

### Example
- Position avg cost = $1.00 · TP = 5% · Trail = 2%
- Price hits $1.05 → trailing ARMS
- Price rises to $1.10 → trailing locks at $1.078
- Price drops to $1.078 → MARKET SELL fires ✅

---

## Slippage Handling (LOCKED)

All orders are market orders. Before every DCA:

1. Check order book depth at target price
2. If available >= $1 minimum → buy at target price ✅
3. If available < $1 minimum → buy $1 market order
4. Maximum slippage exposure = $1 only
5. Never chase more than $1 above target
6. Always executes something — never stuck waiting
7. Recalculate avg cost from actual fill
8. Next DCA from new last buy price

---

## ST Flag — Exchange Suspended Trading (LOCKED)

- Exchange marks coin ST → auto sell immediately (market order)
- Do not open new positions on ST coins
- When ST cleared → resume normally
- Telegram alert when ST detected and cleared
- Checked via CCXT on all 7 exchanges every hour
- This is the ONLY forced close — user controls everything else
- Dead coins without ST flag → nothing we can do · holds position

---

## Profit Coin

- User chooses at bot creation: USDT or base coin
- Works for both Long and Short trades
- Long + USDT: sell all coin → receive USDT
- Long + base coin: sell enough to recover invested USDT · keep profit as coin
- Short + USDT: buy back less coin than sold · difference stays as USDT
- Short + base coin: buy back same USDT value · at lower price = more coin

---

## Current config.py Parameters

| Variable | Value | Description |
|----------|-------|-------------|
| PAPER_MODE | .env file | Never in config.py |
| BASE_ORDER_USDT | 1.0 | First buy amount |
| DCA_PERCENT | 7.0 | % drop from last buy |
| SPACING_MULTIPLIER | 1.4 | Spacing widens each level |
| SIZE_MULTIPLIER | 1.5 | Size increases each level |
| TAKE_PROFIT_PERCENT | 5.0 | % above avg cost to arm TP |
| TRAILING_PERCENT | 2.0 | % pullback from peak to sell |
| AUTO_COINS | True | Auto-fetch all USDT pairs |
| MAX_COINS | 100 | Replit only — remove on Hetzner |
| CHECK_INTERVAL | 60 | Seconds between price checks |

---

## Supported Exchanges (via CCXT)
1. MEXC (live now on Replit)
2. Binance
3. KuCoin
4. OKX
5. Gate.io
6. Bybit
7. Bitget

## TP Recalculation Timing (LOCKED)

- TP target recalculates after EVERY buy automatically
- Formula: TP_target = avg_cost x (1 + TP%)
- Recalculates after: entry buy, every auto DCA, every Add Funds
- TP target is NEVER a fixed price
- Always based on current weighted average cost
- Add Funds shows preview before executing: quantity, new avg cost, new TP target
# Risk and Safety

> How Averion protects capital and ensures stability.
> All rules here are LOCKED unless explicitly discussed with Bader.

---

## Safety Philosophy
- Survivability first · Controlled recovery second · Profit third
- Bot never forces decisions on user — user always in control
- Only exception = ST flag from exchange (forced sell)
- Smart queue is the primary protection system

---

## Smart DCA Queue

### Formula (LOCKED)
Score = Loss% divided by USDT required for next DCA
Higher score = more recovery per dollar = funded first

### Example
- Position A: -20% loss · needs $15.00 → Score = 1.33
- Position B: -15% loss · needs $5.00  → Score = 3.00 ← funded first ✅

### Rules
- ONE DCA per cycle — predictable and auditable
- When TP fires → freed capital → IMMEDIATE rescan
- No maximum DCA levels — queue handles capital forever
- Queue naturally prevents duplicate DCAs
- Last buy price always updates after every buy
- Next trigger always moves — cannot fire twice
- Single sequential loop — no race conditions possible

### Crash Protection
- Smart queue IS the crash protection
- Capital depletes gradually — never dumps all at once
- Natural brake through capital limitation
- No special crash detection needed
- ST flag handles true emergencies only

---

## Never Stuck Principle (LOCKED)

Bot NEVER completely stops. Always doing something.

| Scenario | What Happens |
|----------|-------------|
| No funds for DCA | Score all → execute best covered → skip rest → retry 60s |
| TP fires | Freed capital → immediate rescan → no 60s wait |
| User adds funds | Detected within 60 seconds → queue rescores |
| Below reserve floor | New entries pause · DCA continues · TP continues |
| Exchange disconnects | PM2 restarts → reconnects → queue resumes |
| API rate limit | Slow calls → wait → retry → never crashes |

---

## Reserve Floor and Auto-Resume

- Minimum USDT always untouched — set per bot at creation
- When floor hit → snapshot saved → Trading OFF forced · DCA ON continues
- Resume Threshold must be higher than floor (prevents flickering)
- Auto-Resume ON → restores snapshot when threshold cleared
- Auto-Resume OFF → user resumes manually
- Bot keeps running during floor period — only new entries blocked

---

## Two Bot Toggles (Independent)

| Trading | DCA | Result |
|---------|-----|--------|
| ON | ON | Normal — opens new + averages existing |
| OFF | ON | Ride only — existing reach TP · no new positions |
| ON | OFF | Open new but no averaging (unusual) |
| OFF | OFF | Full stop — positions frozen |

Most common: Trading OFF + DCA ON (ride only mode)

---

## Trade Limits

- Total limit = 100 CONCURRENT open trades maximum (paper + live combined) — separate from monthly trade bundle
- Paper maximum = 30 of the 100
- Live maximum = 100 minus paper trades used
- At paper limit → blocked with message
- At total limit → new positions blocked · existing continue
- Counter in topbar: Trades: 67/100 (Paper: 25/30 · Live: 42)

---

## Paper Trade Rules (LOCKED)

- Paper stays paper FOREVER — live stays live — NO conversion
- Paper = identical server load as live trade
- Auto-close ALL paper trades if ZERO live trades for 90 days
- Day 83 warning Telegram · Day 89 final warning · Day 90 auto-close
- Timer resets when ANY live position opens
- Prevents server abuse by inactive users

---

## Exchange Admin Toggles

### Global Toggle
- Single master switch in admin panel
- OFF → stops new positions on ALL exchanges
- Bot keeps running · DCA continues · TP exits continue
- Dashboard shows maintenance message

### Per Exchange Toggle
- Individual ON/OFF per exchange
- Custom note per exchange (e.g. KuCoin API maintenance)
- Other exchanges continue normally

---

## Bot Rules

### Max Trades Per Bot
- Default = 0 (must set before launching)
- Warning shown if left at 0
- When full → no new entries · when 1 closes → opens next
- Still counts toward customer 100-trade total

### One Pair Per Bot
- One open position per coin per bot — enforced automatically
- Same coin on different bot = fine ✅
- Dashboard blocks duplicate attempt with message

---

## ST Flag Detection (LOCKED)

- Checked via CCXT on all 7 exchanges every hour
- ST detected → auto sell immediately (market order)
- Do not open new positions on ST coins
- When ST cleared → resume normally
- Telegram alert on detection and clearance
- Dead coins without ST → nothing we can do · position holds

---

## Security

- PAPER_MODE in .env — never in config.py
- Default PAPER_MODE = true always (safe by default)
- 10 second countdown warning when switching to LIVE
- Red banner across full topbar in LIVE mode
- Fernet encryption for API keys stored in DB
- IP whitelist for admin panel
- CORS — non-averionbot.com domains blocked
- Withdrawal permissions NEVER enabled on API keys

---

## Recovery Buy System

- REMOVED — handled by smart queue + Add Funds
- Smart queue naturally prioritizes stuck positions
- User uses Add Funds for manual intervention
# Smart DCA Engine

> The brain of Averion.
> Auto-classification · 10 entry methods · research system · equations.

---

## Philosophy
- Survivability first · Controlled recovery second · Profit third
- Platform gets smarter every year automatically
- Data decides winners — not opinions

---

## Five Market Cap Categories

| Category | Market Cap | Examples | Default Spacing | Default TP |
|----------|-----------|---------|----------------|-----------|
| Mega Cap | >$100B | BTC · ETH | 4-5% | 2-3% |
| Large Cap | $10B-$100B | BNB · SOL · XRP | 6-7% | 3-5% |
| Mid Cap | $1B-$10B | AVAX · LINK · INJ | 8-10% | 5-7% |
| Small Cap | $100M-$1B | RVN · HBAR · CELO | 10-15% | 6-10% |
| Micro Cap | <$100M | Unknown/new coins | 15-25% | 8-15% |

Customers see category name ONLY.
All boundaries and parameters = admin only — never shown to customers.

---

## Admin-Only Parameter Limits

| Category | Spacing Min/Max | Size Mult | TP% | Trail% |
|----------|----------------|-----------|-----|--------|
| Mega Cap | 2% — 8% | 1.1x — 1.8x | 1% — 5% | 0.5% — 2% |
| Large Cap | 5% — 12% | 1.2x — 2.2x | 2% — 7% | 1% — 3% |
| Mid Cap | 7% — 18% | 1.3x — 2.8x | 4% — 10% | 1.5% — 4% |
| Small Cap | 10% — 25% | 1.5x — 3.5x | 5% — 15% | 2% — 6% |
| Micro Cap | 15% — 40% | 2x — 5x | 8% — 20% | 3% — 8% |

---

## Smart DCA Calculations

### What It Calculates Automatically
- Reads 90 days of hourly OHLCV data per coin per exchange
- Calculates optimal spacing using ATR_14 + median bounce threshold
- Calculates size multiplier from category base + per-level escalation
- Calculates TP from weighted average entry + median recovery
- Volume-weighted category parameters
- Updates all parameters daily at 3am

### Spacing Formula (LOCKED)
- spacing = max(ATR_14 x 1.5, median_bounce_threshold x 0.85)
- Clamped between category min and max

### Example — BTC (Mega Cap)
- ATR daily = 1.8% → ATR x 1.5 = 2.7%
- Median drop before bounce = 3.1% → x 0.85 = 2.6%
- max(2.7%, 2.6%) = 2.7% → within Mega Cap range ✅

### Example — RVN (Small Cap)
- ATR daily = 4.2% → ATR x 1.5 = 6.3%
- Median drop before bounce = 8.4% → x 0.85 = 7.1%
- max(6.3%, 7.1%) = 7.1% → below Small Cap floor 10% → clamped to 10% ✅

### TP Formula
- TP_target = weighted_avg_entry_price x (1 + median_recovery% x 0.70)
- Always from YOUR actual average cost — not original entry

### Size Multiplier
- Coin base: Mega=1.10x · Large=1.20x · Mid=1.35x · Small=1.50x · Micro=1.65x
- Per level: L1=1.0x · L2=1.2x · L3=1.4x · L4=1.6x · L5+=2.0x hard cap
- Example Small Cap L3: $1.00 x 1.50 x 1.4 = $2.10 per DCA buy

### Always Use MEDIAN Not MEAN
- Sample: 2% · 3% · 4% · 5% · 40%
- Mean = 10.8% (distorted by flash crash)
- Median = 4% (actual typical behavior) ✅

---

## Volume-Weighted Category Parameters

Formula:
Category_Spacing = Sum(coin_spacing x coin_24h_volume) / Sum(all volumes in category)

### Example — Mega Cap
| Coin | Spacing | 24h Volume | Weight | Contribution |
|------|---------|-----------|--------|-------------|
| BTC | 2.7% | $28B | 87.0% | 2.349% |
| ETH | 3.1% | $4B | 12.5% | 0.388% |
| BNB | 3.4% | $200M | 0.5% | 0.017% |
| Result | — | $32.2B | 100% | 2.754% |

Updates daily at 3am as volumes shift.

---

## Auto-Classification Engine

### Data Sources (LOCKED)
- Exchange data via CCXT: coin list + volume + OHLCV
- CoinGecko: market cap ONLY for classification
- Never mixed in same calculation

### Daily 3am Process
1. Fetch market cap from CoinGecko (rate-limited · batched)
2. Apply cap protection formula
3. Compare against category boundaries
4. If boundary crossed → reclassify immediately
5. Apply new parameters to NEW positions only (existing positions keep original parameters — see 13_LOCKED_DECISIONS.md)
6. Log in coin_history table
7. Telegram alert if any coin reclassified

### CoinGecko Failure Fallback
- Use last recorded market cap from coin_history
- Skip reclassification that day
- Telegram alert: CoinGecko failed — using last recorded caps
- Retry next 3am automatically

### New Coin Tiered Confidence
| History | Approach | Badge |
|---------|---------|-------|
| < 30 days | Category defaults + penalty | 🔴 New |
| 30-90 days | 70% defaults + 30% coin stats | 🟡 Learning |
| > 90 days | Fully adaptive — coin's own data | 🟢 Calibrated |

---

## Cap Protection System (LOCKED)

Original idea by Bader. No other platform does this.

### Formula
- Upward: recorded_cap = min(real_cap, previous x 1.10) — max +10% per day
- Downward: recorded_cap = real_cap — full drop immediately

### Why It Works
- Fake pump: $100M → $500M overnight → recorded as $110M only
- Coin stays Small Cap → conservative parameters maintained
- Real growth: takes 25+ consecutive days to cross category boundary
- Fake pumps cannot sustain 25 days → naturally filtered

---

## 10 Entry Methods

All run simultaneously in paper mode.
Same coins · same DCA params · only entry signal differs.
3-12 months data decides winner.
Worst deleted · best becomes Smart DCA default.

### 5 Benchmark Bots (always running)
- BTC Buy & Hold — pure market exposure
- ETH Buy & Hold — pure market exposure
- Simple DCA — ASAP entry no signal
- Random Entry DCA — control group
- Static Spacing DCA — tests if widening adds value

### E1 — VWAP + RSI Deviation (Current Baseline)
- RSI < 35 (oversold)
- VWAP distance > 3% below
- ATR > 1.5x 30-day average (volatility spike)
- Bounce probability > 60%
- ALL FOUR required simultaneously

### E2 — Panic Exhaustion
- Previous candle pierced below lower Bollinger Band
- Current candle closes back inside band
- Volume > 2x 24h average
- Current candle closes green

### E3 — Volume Climax
- Volume > 4x SMA(Volume, 72)
- Close < SMA(Close, 24)
- Candle range > 2.5x ATR · close in upper 50%

### E4 — Time-Cycle Window
- Sunday UTC 22:00-23:00 only
- Close < SMA(Close, 48)

### E5 — Multi-Timeframe Alignment
- Close > EMA(Close, 168) — bullish macro
- Close < EMA(Close, 24) — micro pullback
- RSI(14) < 45
- Close > Close[1] — first green candle

### E6 — Z-Score Statistical
- Z = (Close - Rolling_Mean_168h) / Rolling_StdDev_168h
- Entry when Z < -2.5

### E7 — Volatility Squeeze
- Bollinger Bands inside Keltner Channels >= 12 hours
- Current close > Upper Bollinger Band
- Volume > SMA(Volume, 24)

### E8 — Swing Structure Shift
- Lower low within past 48 hours confirmed
- Last swing high identified (high > 3 candles before AND after)
- Close > last swing high
- Close > Trailing VWAP(24)

### E9 — Sequential Candle Decay
- 6 consecutive red candles (lower closes)
- 7th candle: green AND volume > avg of prior 6

### E10 — Pure Drop Threshold (Control Group)
- Price drops X% from recent 24h high → enter
- No indicators — pure price drop only
- Most important benchmark — measures if signals add value

---

## Research System

### What Gets Stored Per Trade
- Entry method + version
- Full market context (BTC trend · regime · volatility)
- All signal values at entry
- DCA progression
- Exit details + profit

### Parameter Versioning
- Every parameter change creates new version
- Old versions kept for comparison
- Never mix results between versions
- 30-day cooldown enforced after any change

### Monthly Review Workflow
1. Generate signed research URL (1 click in admin)
2. Share URL with Claude → get analysis
3. Share same URL with ChatGPT → second opinion
4. Compare recommendations
5. Approve changes in admin panel
6. 30-day cooldown starts automatically

### Three-Speed Evaluation
- Daily: automatic health check → Telegram alert if flagged
- Monthly: 5 minutes → share URL → approve changes
- Quarterly: 10 minutes → delete worst · promote winners

## Research Bot Grid (LOCKED — ChatGPT Validated)

Total: 107 paper bots (102 method bots + 5 benchmarks)
Period: 6 months · no mid-period adjustments
Scaling: start 10 trades/bot → 20 → 30 gradually

### Bot Count Per Method
- E1 VWAP+RSI: 12 bots (RSI · VWAP · ATR · Bounce variations)
- E2 Panic Exhaustion: 9 bots (Volume · BB · Recovery variations)
- E3 Volume Climax: 12 bots (Volume multiple · Range · Close position)
- E4 Time-Cycle: 9 bots (Window duration · SMA length)
- E5 Multi-Timeframe: 12 bots (Macro EMA · Pullback EMA · RSI)
- E6 Z-Score: 9 bots (Z trigger · Lookback period)
- E7 Volatility Squeeze: 9 bots (Squeeze duration · Volume filter)
- E8 Swing Structure: 9 bots (Detection width · VWAP length)
- E9 Sequential Candle: 9 bots (Red candle count · Reversal volume)
- E10 Pure Drop: 12 bots (Drop threshold · Lookback high)

### 5 Benchmark Bots (always running)
- BTC Buy and Hold
- ETH Buy and Hold
- Simple DCA (ASAP entry)
- Random Entry DCA
- Static Spacing DCA

### Full Parameter Grid
Stored in: docs/05_SMART_DCA_ENGINE.md
Validated by ChatGPT May 2026
Each bot tests unique parameter hypothesis
Mathematical progression — no random values

## Detailed Parameter Grid Per Method

### E1 — VWAP + RSI (12 bots)
| Bot | RSI | VWAP | ATR | Bounce |
|-----|-----|------|-----|--------|
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

### E2 — Panic Exhaustion (9 bots)
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

### E3 — Volume Climax (12 bots)
| Bot | Volume | Range vs ATR | Close Position |
|-----|--------|-------------|---------------|
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

### E4 — Time-Cycle Window (9 bots)
| Bot | Window | SMA Length |
|-----|--------|-----------|
| E4-1 | 1h | 24 |
| E4-2 | 1h | 48 |
| E4-3 | 1h | 72 |
| E4-4 | 2h | 24 |
| E4-5 | 2h | 48 |
| E4-6 | 2h | 72 |
| E4-7 | 4h | 24 |
| E4-8 | 4h | 48 |
| E4-9 | 4h | 72 |

### E5 — Multi-Timeframe (12 bots)
| Bot | Macro EMA | Pullback EMA | RSI |
|-----|-----------|-------------|-----|
| E5-1 | 144 | 12 | 35 |
| E5-2 | 144 | 24 | 40 |
| E5-3 | 144 | 36 | 45 |
| E5-4 | 168 | 12 | 35 |
| E5-5 | 168 | 24 | 40 |
| E5-6 | 168 | 36 | 45 |
| E5-7 | 200 | 12 | 35 |
| E5-8 | 200 | 24 | 40 |
| E5-9 | 200 | 36 | 45 |
| E5-10 | 168 | 24 | 35 |
| E5-11 | 168 | 24 | 45 |
| E5-12 | 200 | 36 | 40 |

### E6 — Z-Score Statistical (9 bots)
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

### E7 — Volatility Squeeze (9 bots)
| Bot | Squeeze Duration | Volume Filter |
|-----|-----------------|--------------|
| E7-1 | 8h | 1.0x |
| E7-2 | 12h | 1.0x |
| E7-3 | 24h | 1.0x |
| E7-4 | 8h | 1.5x |
| E7-5 | 12h | 1.5x |
| E7-6 | 24h | 1.5x |
| E7-7 | 8h | 2.0x |
| E7-8 | 12h | 2.0x |
| E7-9 | 24h | 2.0x |

### E8 — Swing Structure Shift (9 bots)
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

### E9 — Sequential Candle Decay (9 bots)
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

### E10 — Pure Drop Threshold (12 bots)
| Bot | Drop % | Lookback High |
|-----|--------|--------------|
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
# Business Model

> How Averion makes money.
> All rules here are LOCKED unless explicitly discussed with Bader.

---

## Performance Fee

- Rate = 20% of realized profits only
- Realized = fully closed positions only
- Open positions = NOT counted ever
- Loss months = $0 fee — no charge — no rollover
- No high water mark — every month starts fresh
- Fee deducted automatically from reserve wallet per winning trade

---

## Fee Examples

| Month | Realized P&L | Fee 20% | Result |
|-------|-------------|---------|--------|
| January | +$500 | $100 | Deducted from reserve ✅ |
| February | -$200 | $0 | No charge — loss month ✅ |
| March | +$300 | $60 | Deducted from reserve ✅ |
| April | $0 | $0 | No closed trades — no charge ✅ |
| May | +$1,200 | $240 | Deducted from reserve ✅ |

---

## Account Types

| Type | Fee | Reserve Needed | Notes |
|------|-----|---------------|-------|
| Regular customer | 20% | Yes | Standard |
| 0% account | 0% | No | Relatives · selected by admin |
| Admin account | 0% | No | All income to owner wallet |

---

## Reserve Wallet System (LOCKED)

### Concept
User deposits USDT into reserve wallet.
Bot trades using exchange funds — reserve not touched for trading.
After each winning trade → 20% fee auto-deducted from reserve.
True set and forget — no monthly invoices.

### How It Works
1. User deposits $10 USDT to their reserve wallet
2. Bot trades normally using exchange funds
3. Winning trade closes — profit $1.00 — fee $0.20
4. $0.20 auto-deducted from reserve → balance $9.80
5. Loss trade closes → $0 deducted → reserve untouched
6. Reserve reaches $0 → new positions pause
7. User tops up → bot resumes within 60 seconds

### Reserve Alerts
- Balance < $5.00 → ⚠️ Telegram warning
- Balance < $2.00 → 🔴 Telegram critical
- Balance = $0 → ❌ New positions paused · Telegram alert
- After top-up → ✅ Bot resumed automatically

### Networks
- TRC20 (Tron) recommended — cheapest ~$1 per transaction
- BEP20 (BSC) alternative — ~$0.50 per transaction
- ERC20 NOT supported — too expensive ($10-30 per transaction)

### Minimum Top-Up
- $10 minimum — prevents micro-deposits
- $5 free trial credit for new users (real trading · no card needed)

---

## NOWPayments Integration (LOCKED)

- Gateway: NOWPayments (0.5% fee per deposit)
- Unique address per user — no memo confusion
- Funds auto-forward to owner USDT wallet (non-custodial mode)
- Webhook notification = instant credit to user balance
- No manual action needed — fully automatic
- Start Phase 7 with NOWPayments → switch to HD wallet when scaling

---

## Owner Wallet — Fee Collection

### Transfer Rules (LOCKED)
- Fees accumulate in DB — not transferred daily
- Auto-transfer when accumulated >= threshold
- Default threshold = $10 (admin adjustable in panel)
- Month-end force transfer regardless of threshold
- Transfer via TRC20 (cheapest network fees)
- [Transfer Now] button in admin panel for manual transfer

### Admin Panel — Owner Wallet Section
- Your wallet address TRC20 + BEP20 (editable)
- Transfer threshold (adjustable anytime)
- Pending balance display
- Transfer history log
- [Transfer Now] button

---

## Referral System (LOCKED)

### How It Works
- Rate = 3% of the 20% performance fee → referrer reserve wallet
- Duration = forever — no time limit
- Referred user still pays full 20% — no discount ever

### Math Example
- Ahmed makes $1,000 profit
- Ahmed pays $200 fee (20%)
- Khalid (referrer) gets $6.00 (3% of $200)
- Owner gets $194.00 (97% of $200)

### Rules
- Code entered at registration ONLY — cannot add or change after
- Regular customers always pay 20% — referral invisible to them
- Self-referral blocked by anti-fraud system
- Loss months = $0 referral income (correct)
- 0% accounts = $0 fee = $0 referral income
- Referrer deleted → referred user reverts to normal 20% to owner

---

## Anti-Fraud System — 5 Layers

| Layer | Method | Catches |
|-------|--------|---------|
| 1 | Email + Phone KYC | Duplicate identities |
| 2 | Exchange API UID fingerprint | Same exchange account |
| 3 | Stripe payment method | Same card/bank |
| 4 | IP + Device fingerprint | Same device (admin review) |
| 5 | Cross-exchange blacklist | All exchanges blocked |

Layer 2 most powerful: Exchange UID never changes even with new API keys.

---

## Future Monetization

- Phase 8: Strategy Marketplace
- Signal providers listed with verified track record
- One-click subscribe → webhook auto-connected
- Averion takes 10-15% subscription fee + 20% performance fee
- Provider vetting: >55% win rate · >6 months history · <30% drawdown
# Dashboard and UI

> Complete dashboard design · all tabs · responsive layout.

---

## Architecture

- Single file: dashboard.html (on Replit)
- Split into separate tab files on Hetzner Day 1
- Served by FastAPI on port 8080
- Chart.js for capital chart
- Inter font from Google Fonts
- No external CSS frameworks

---

## Responsive Layout

| Screen | Layout |
|--------|--------|
| Desktop >= 1024px | Full sidebar 220px + content area |
| Tablet 768-1023px | Icon-only sidebar 60px + content |
| Mobile < 768px | No sidebar · bottom nav 4 tabs |

100% automatic CSS media queries — no JavaScript toggle.

---

## Sidebar (Desktop/Tablet)

### Desktop (220px)
- Logo mark + AVERION text + BETA badge
- Nav links with icons + labels
- Section labels (Overview · Analytics · System)
- User avatar + name + plan at bottom

### Tablet (60px icon only)
- Logo mark only
- Icons only — no labels
- User avatar only

### Nav Links
- Home (active state: indigo background + border)
- Bots (with count badge)
- History
- Settings

---

## Topbar

- Height: 56px desktop · 50px mobile
- Left: page title
- Right: PAPER chip · BTC price ticker · notification bell · user icon
- LIVE mode: full red banner replaces topbar
- PAPER chip hidden on mobile

---

## Bottom Nav (Mobile Only)

- 4 tabs: Home · Bots · History · Settings
- Active tab: indigo color
- Icons + labels
- Safe area padding for iPhone notch

---

## Home Tab

### 5 Hero Stat Cards
| Card | Value | Subtitle |
|------|-------|---------|
| Total Capital | Sum all exchanges USDT | across X exchanges |
| Last 24h P&L | Unrealized change | +/- % colored |
| Total Profit | All-time realized | all time · all exchanges |
| Fees Due | 20% of month profits | Pay Now button if >$0 |
| Active Trades | Open count | Paper: X/30 · Live: Y |

### Fees Banner
- Shows only when fees > $0
- Amber background · Pay Now button (Phase 7 Stripe)

### Exchange Cards Grid
- 2 columns desktop · 1 column mobile
- Each card: logo · name · value · 24h P&L · 3 mini stats · coin tags
- Tap card → Exchange Detail screen
- 3-dot menu: Test Connection · Edit API Keys · Rename · Delete
- Add Exchange card (dashed border) always last

---

## Exchange Detail Screen

- Back button → Home
- Exchange name in header
- 3-dot menu (Test · Edit · Rename · Delete)
- 4 stat cards: Capital · Profit · Open Trades · 24h P&L
- Interactive capital chart (Chart.js)
  - Green line if growing · Red if declining
  - Hover shows date + exact value
  - 7D / 30D / All range buttons
- Bots section below chart

---

## Bots Tab (NEW v4.6 Flat List — LOCKED)

### Layout
- NOT grouped by exchange
- Flat list — one row per bot
- Exchange shown as colored badge per row

### Top Bar
- Title: Bots + subtitle (X bots · Y running)
- Search input
- Create Bot button

### Filter Bar
- Status filter (All · Running · Stopped · Live · Paper)
- Exchange filter (All · MEXC · Binance etc)
- Sort filter (P&L · Trades · Name)

### Table Columns
- BOT: indicator dot + name + exchange name
- EXCH: colored badge [M][B][K][O][G][By][Bg]
- TRADES: count in blue
- P&L: dollar + percentage colored
- MODE: LIVE or PAPER badge
- CONTROLS: T toggle + DCA toggle inline
- Actions: 3-dot menu

### Exchange Badge Colors
| Badge | Exchange | Color |
|-------|---------|-------|
| [M] | MEXC | Blue #38BDF8 |
| [B] | Binance | Amber #F59E0B |
| [K] | KuCoin | Green #10D98A |
| [O] | OKX | White #E2E8F0 |
| [G] | Gate.io | Blue lighter |
| [By] | Bybit | Orange #FB923C |
| [Bg] | Bitget | Purple #A78BFA |

### Two Toggles (inline per row)
- T = Trading (opens new positions)
- DCA = DCA averaging (existing positions)
- Green ON · Gray OFF · independent

### Kebab Menu
- Edit bot settings
- Duplicate bot (wizard pre-filled)
- Delete bot

### Bot Detail (Level 2)
- Back to Bots button
- 4 stats: Open · Invested · P&L$ · P&L%
- Stop/Start bot button
- Search + filter bar
- Positions table with all columns

---

## History Tab

### 6 Hero Cards
- Closed Trades · Total Profit · Win Rate
- Avg Hold · Fees 20% · Net Profit

### Filters
- Exchange dropdown
- Coin dropdown
- Date presets: Today · 7d · 30d · All
- Custom date range (from/to)
- Column picker (show/hide any column)

### Table Columns
Coin · Exchange · Entry Date · Exit Date · Entry Price ·
Avg Cost · Exit Price · DCA# · P&L% · P&L$ ·
Hold Time · Exit Reason · Fee 20% · Net Profit

---

## Settings Tab

Account info ONLY — bot config lives in wizard.

### Sections
- Profile: email · phone
- Security: 2FA toggle · change password · active sessions
- Exchanges: link to Home tab management
- Notifications: 3 Telegram IDs · alert type toggles
- Reserve Wallet: balance · top-up · deduction history · referral income
- Help: documentation · feature request · contact support

---

## Dashboard Comment Markers (Item 26)

To be added after Item 24:
- Every section marked clearly
- Makes terminal editing safe
- Preparation for Hetzner file split

Example:

## Customer Dashboard — Home Tab (LOCKED)

### Design Philosophy
- Fits one phone screen · no scrolling for critical info
- Most important info visible immediately on open
- Clean · minimal · actionable

### Layout

#### TOP — 4 Quick Stat Cards
| Open Positions | Profit Today | Fees Today | Reserve Wallet |
|----------------|--------------|------------|----------------|
| 23             | +$47.20      | $9.44      | $50.00         |

- Profit today = realized profits only
- Fees today = performance fees deducted today
- Reserve wallet = current balance · tap to top up

#### SECTION 2 — Active Alerts
- Same attention log as Bots tab
- Only shows when something needs attention
- Empty = shows "✅ All systems normal"
- Tap alert → goes to relevant screen

#### SECTION 3 — Exchange Capital (compact)
One line per exchange:
- MEXC    $234.50  [3 bots · 12 positions]
- KuCoin  $567.20  [5 bots · 11 positions]
- Total   $801.70

- Tap exchange row → goes to Bots tab filtered by exchange
- Shows only exchanges user has added
- Shows capital deployed + active bots + open positions

#### SECTION 4 — Recent Activity
Last 5 closed positions:
- Coin · profit/loss · time ago · result icon
- RVN  +$4.20  2h ago  ✅
- BTC  +$12.50  5h ago  ✅
- ETH  -$2.10  8h ago  ❌
- Tap any row → goes to position detail screen

### Mobile First
- Designed for phone screen primarily
- 4 cards fit in 2×2 grid on small screen
- All sections stack vertically
- Large tap targets · no tiny buttons

## Customer Dashboard — History Tab (LOCKED)

### Summary Bar (top)
- Total closed positions · Win rate % · Total profit · Total fees paid

### Filters
- Date: [All] [This Month] [Last Month] [Custom date range]
- Coin: [All Coins ▼] searchable dropdown
- Exchange: [All Exchanges ▼]
- Result: [All] [Wins Only] [Losses Only]

### Table Columns (in order)
1. Coin
2. Exchange
3. Direction (Long/Short)
4. Entry Date
5. Exit Date
6. Hold Time (hours/days)
7. Total Invested
8. Gross Profit
9. Exchange Fees
10. Performance Fee (20%)
11. Net Profit
12. ROI %
13. Exit Reason (TP · Manual · ST flag)
14. DCA Levels Used
15. Entry Method
16. Bot Name

### Row Behavior
- Green row = profitable trade
- Red row = loss trade
- Tap row → opens Position Detail Screen
  (full DCA history · all individual orders)

### Bottom Actions
- [📥 Export CSV] → download for tax records
- Pagination: 50 rows per page

### Position Detail Screen (from tap)
- Position ID · Coin · Exchange · Bot name
- Entry method used
- Progress bar: Entry → DCA levels → Exit
- Full DCA history table:
  Level · Date · Price · Amount · Quantity
- Summary: total invested · avg cost · exit price
- All fees breakdown
- Final net profit

## Customer Dashboard — Settings Tab (LOCKED)

### Section 1 — Profile
- Email · phone · change password
- Account created date · referral code

### Section 2 — Exchanges
- List of connected exchanges
- Per exchange row:
  Name · Status · Last connected
  [Test Connection] [Edit] [Delete]
- Test Connection button:
  → Fetches balance from exchange
  → Shows: ✅ Connected · Balance: $234.50
  → Or: ❌ Invalid key / IP not whitelisted / Wrong passphrase
- [+ Add Exchange] button
- Exchange form: Name · API Key · Secret · 
  Passphrase (if required) · IP whitelist confirmed ☑

### Section 3 — Notifications
- Connect status: @AverionBot ✅ [Disconnect]
- If not connected: [Connect Telegram] button
- Toggles (each independent ON/OFF):
  Trade notifications · Alert notifications
  Daily report · Weekly report · Monthly report

### Section 4 — Reserve Wallet
- Current balance · Fee debt (red if any)
- Last 10 deposit history
- [Top Up] button → NOWPayments flow
- No withdrawal option · funds used for trading only

### Section 5 — Subscription & Billing

Free plan always included:
- 5 bots · 100 trades/month · forever

Per Bot billing:
- Each bot has own expiry date
- Table: Bot Name · Expires · Auto-renew · Action
- [Renew] button per bot
- [Auto-renew ON/OFF] toggle per bot
- Auto-renew: deducts from reserve 3 days before expiry
- One-time: user renews manually
- Telegram reminder 3 days before expiry either way
- [+ Add Bot Slot $1/month]

Per Trade Bundle:
- Current bundle: trades used · remaining · expiry
- Auto-renew toggle per bundle
- [+ Buy Bundle]: 200=$3 · 500=$5 · 1000=$8 · Unlimited=$15/mo
- Bundles stack: current used first · new starts after

### Section 6 — Security
- Last login: date · IP · device
- Active sessions list
- [Log Out All Devices] button
# Bot Creation Wizard

> 7-step wizard for creating new bots.
> Accessed from Bots tab + Create Bot button.

---

## Overview

- 7 steps total
- Back button available at any step
- Warnings shown in amber
- Errors shown in red (cannot launch until fixed)

---

## Step 1 — Basic Setup

| Field | Type | Notes |
|-------|------|-------|
| Bot Name | Text input | User defined |
| Exchange | Dropdown | Pre-filled from selected exchange |
| Direction | Radio | Long or Short |

### Short DCA Requirements
- User must already hold the coin on exchange
- Bot checks holdings before opening position
- Only sells if quantity >= exchange minimum order size

---

## Step 2 — Trading Method

| Method | Description |
|--------|-------------|
| Smart DCA | Fully automated · recommended default |
| ASAP | Opens immediately on any qualifying coin |
| Mean-Reversion | RSI + VWAP + ATR + bounce probability |
| TradingView | External signal via webhook |

### Smart DCA
- Coin selection: All / Top X by volume / Custom list
- All parameters automated from 90-day data

### Mean-Reversion
- Auto — qualifying coins only
- All 4 conditions must be true simultaneously

---

## Step 3 — Order Settings

| Field | Default | Notes |
|-------|---------|-------|
| Base Order ($) | 1.00 | Validated against exchange minimum |
| Quote Currency | USDT or BTC | Selected at bot creation · cannot change |
| Entry Order Type | Market | Market or Limit · user selects |
| DCA Order Type | Market | Market or Limit · user selects |

### Order Type Rules
- Market entry + Market DCA: standard behavior
- Limit entry: places limit buy at current price · waits for fill
- Limit DCA: places limit buy at DCA trigger price · next level only
- Trailing TP: auto-hidden when Limit DCA selected (not compatible)
- Can switch Market/Limit ON/OFF anytime · even mid-trade
- Limit ON: bot places limit order on exchange immediately
- Limit OFF: cancels all pending limit orders · USDT returned to wallet

### Limit DCA Partial Fill Behavior
- $10 DCA · $2 fills → avg cost + TP recalculate
- $7.50 more fills → avg cost + TP recalculate again
- $0.50 remaining < minimum order → added to next DCA level
- TP fires → pending limit cancelled → USDT freed automatically

---

## Step 4 — DCA Settings

### Smart DCA
- All automated · no manual input needed
- Category auto-detected from coin market cap
- Confidence level shown per coin

### Manual Methods (ASAP · Mean-Reversion · TradingView)
| Field | Notes |
|-------|-------|
| DCA Trigger % | % drop from last buy price to fire DCA |
| Spacing Multiplier | Each level widens by this factor |
| Size Multiplier | Each level size increases by this factor |

### Trade Volume Settings
| Field | Default | Notes |
|-------|---------|-------|
| Trades per Bot | 1 | Max concurrent open trades from this bot |
| Trades per Coin | 1 | How many times same coin repeats in this bot |

### Sequential Trade Gates
Controls when next trade on same coin opens:

| Gate | Default | Notes |
|------|---------|-------|
| DCA Trigger Gate | OFF | Opens next trade when current hits DCA level |
| Timer Gate | OFF | Opens next trade after X hours from last opened |
| Timer Hours | 5 | Hours to wait before opening next trade |

Gate rules:
- Both OFF: only 1 trade per coin (default)
- DCA trigger ON: next trade opens when current position hits DCA
- Timer ON: next trade opens after X hours from last opened trade
- Both ON: whichever comes first opens next trade
- Last opened trade = always the gate reference
- When reference closes → previous becomes reference → sequence continues
- Can switch ON/OFF anytime · even mid-trade

Example:
Trades per bot: 20 · Trades per coin: 3 · Gate: both (DCA + 5h)
→ Bot opens max 20 trades total across all coins
→ Any single coin max 3 concurrent trades
→ Each coin's trades open sequentially via gate
→ All trades use same bot parameters

---

## Step 5 — Profit Settings

### Smart DCA
- TP Mode: Auto (recommended) or Manual
- If Manual: warning shown if TP% - Trail% < 1%
- Trailing safety enforced automatically
- Trailing TP hidden if Limit DCA selected

### Manual Methods
| Field | Default | Notes |
|-------|---------|-------|
| Take Profit % | 5.0 | % above avg cost to arm trailing |
| Trailing % | 2.0 | % pullback from peak to sell |

Note: Trailing % field hidden when Limit DCA mode ON

### Profit Currency
- USDT: sell all coin → receive USDT
- Base coin: keep profit as the coin itself
- Works for both Long and Short

---

## Step 6 — Safety Settings

| Field | Default | Notes |
|-------|---------|-------|
| Reserve Floor ($) | 50.00 | Minimum USDT always untouched |
| Resume Threshold ($) | 75.00 | Must be higher than floor |
| Auto-Resume | ON | Restores bot automatically |
| Min Daily Volume ($) | 100,000 | Skips illiquid coins |

---

## Step 7 — Review and Launch

- Full summary of all settings shown
- Amber warnings (e.g. low balance)
- Red errors (cannot launch until fixed)
- Coin confidence breakdown: New X · Learning Y · Calibrated Z
- Minimum order size warnings per coin:
  ✅ Will trade · ⚠️ Needs more funds · ❌ Cannot trade
- Back button to any previous step
- Launch Bot button

### Pre-Launch Checks
- Exchange connected and API valid
- Sufficient balance for at least 1 base order
- Reserve floor < resume threshold
- At least 1 coin qualifies for this bot
- If trades per coin > 1: gate settings configured

---

## Duplicate Bot Feature

- Available in Bots tab kebab menu
- Opens wizard with all settings pre-filled
- User can modify any step before launching
- Creates completely new independent bot
- Does not affect original bot

---

## Bot Lifecycle After Launch

1. Bot starts scanning qualifying coins
2. Entry signal detected → opens position
3. Position enters smart queue
4. DCA fires when price drops X% from last buy
5. Sequential gate triggers next trade if configured
6. Trailing TP arms when price rises Y% above avg
   (skipped if Limit DCA mode ON)
7. Market or limit sell fires based on order type
8. Capital freed → queue rescans immediately
9. Bot continues forever until stopped manually
# Infrastructure

> How Averion runs on the server.
> Hetzner setup · maintenance · monitoring · Telegram.

---

## Server

| Item | Detail |
|------|--------|
| Provider | Hetzner Cloud |
| Plan | CX23 |
| Location | Helsinki, Finland |
| OS | Ubuntu 24.04 |
| RAM | 4GB |
| CPU | 2 vCPU |
| Disk | 40GB |
| Cost | €3.99/month |
| Status | Ordered · ID verification pending (~10 days) |

---

## Current Setup (Replit)

- Dashboard URL: https://bbd72f98-d728-46fe-81c6-af97d0011150-00-1c2g4v036wde1.sisko.replit.dev/dashboard
- Bot runs via Replit always-on
- MAX_COINS = 100 (Replit memory limit only)
- Remove MAX_COINS limit on Hetzner

---

## Automated Schedule (LOCKED)

### Every 60 Seconds
- Live prices fetched
- DCA triggers checked
- TP exits checked
- Smart queue executed

### Every Hour
- Health check (CPU · RAM · Disk · PM2 · trades count)
- OHLCV fetch all coins
- ATR recalculate
- Volatility spike guard
- ST flag check on all exchanges
- Alert if any threshold breached

### Daily 3am (Staggered — LOCKED)

#### 03:00 — Infrastructure
- pip install ccxt --upgrade
- pm2 restart averion
- DB backup → /backups/averion_YYYY-MM-DD.db
- Keep last 7 days only

#### 03:30 — Data & Classification
- CoinGecko scan → market cap fetch
- Cap protection formula applied
- Classify/reclassify all coins
- Parameter recalculation (ATR + median bounce)
- Volume-weighted category update

#### 04:00 — Reporting
- Balance snapshot → balance_history table
- metrics/latest.json → pushed to GitHub
- Excel report generation (4 sheets)
- Telegram daily report → Reports channel

#### 04:30 — Sunday Only
- Log cleanup (files >30 days old)
- Disk check (alert if >70%)
- DB VACUUM + ANALYZE
- Weekly Telegram report

### Monthly 1st 5am
- Full system report
- Category performance summary
- Fee summary
- Backup verification

---

## Health Check Thresholds

| Metric | Warning | Critical |
|--------|---------|---------|
| CPU | >80% | >95% |
| RAM | >80% | >95% |
| Disk | >70% | >85% |
| PM2 | Not running | — |
| Bot silent | >5 minutes | — |

All alerts → Telegram Alerts channel immediately

---

## 3 Telegram Channels (LOCKED)

| Channel | Content | Volume Setting |
|---------|---------|---------------|
| Trades | Every buy · sell · DCA · TP | MUTE — check weekly |
| Alerts | Server down · errors · crashes · ST flag · floor hit | MAX VOLUME — NEVER MUTE |
| Reports | Daily · weekly · monthly reports | Normal — morning coffee |

### Config in .env
---

## PM2 Process Manager

- pm2 start main.py --name averion
- pm2 startup → auto-restart on reboot
- pm2 save → saves process list
- pm2 logs averion → view live logs
- pm2 restart averion → manual restart

---

## Daily Telegram Report Example
---

## Maintenance Time Expectations

| Task | Time | Notes |
|------|------|-------|
| Daily check | 30 seconds | Read Telegram Reports |
| Weekly check | 2 minutes | Admin health dashboard |
| Monthly review | 5 minutes | Share research URL → Claude analyzes |
| Code deploy | 30 seconds | git push → auto-deploys |
| API emergency | 15-30 min | SSH → pm2 logs → pip upgrade → restart |

---

## Hetzner Day 1 Checklist
See 16_TODO_HETZNER.md for full step-by-step commands.

---

## Professional Folder Structure (Hetzner Only)
Note: On Replit — keep single file structure (simpler).
Split to professional structure on Hetzner Day 1 only.
# Database and API

> Database schema · API endpoints · technical backend structure.

---

## Database

- PostgreSQL from Day 1 (see 16_TODO_HETZNER.md)
- WAL allows reads while writing — no blocking
- Located at: averion.db (Replit) · /home/averion/Averion/averion.db (Hetzner)
- Backup daily at 3am → /backups/averion_YYYY-MM-DD.db
- Keep last 7 days of backups only
- Already using PostgreSQL from Day 1 on Hetzner

---

## Current Tables (Phase 1-3)

### positions
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique position ID |
| coin | TEXT | e.g. RVN/USDT |
| status | TEXT | open · closed |
| avg_cost | REAL | Weighted average buy price |
| quantity | REAL | Total coin quantity held |
| total_invested | REAL | Total USDT invested |
| dca_count | INTEGER | Number of DCA buys made |
| last_buy_price | REAL | Price of most recent buy |
| tp_armed | BOOLEAN | Trailing TP activated |
| queued | BOOLEAN | In smart queue |
| peak_price | REAL | Highest price seen since TP armed |
| opened_at | DATETIME | When position first opened |
| closed_at | DATETIME | When position closed |

### trades
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique trade ID |
| position_id | INTEGER | Links to positions table |
| coin | TEXT | e.g. RVN/USDT |
| side | TEXT | buy · sell |
| price | REAL | Execution price |
| quantity | REAL | Coin quantity |
| usdt_amount | REAL | USDT value |
| reason | TEXT | entry · dca · tp · manual |
| paper | BOOLEAN | Paper or live trade |
| timestamp | DATETIME | When executed |

### balance_history
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique ID |
| exchange | TEXT | Exchange name |
| value_usdt | REAL | Total balance in USDT |
| recorded_at | DATETIME | Snapshot timestamp |

---

## New Tables (Phase 4-5)

### ohlcv_hourly
- coin · exchange · timestamp · open · high · low · close · volume
- atr_14 · volatility
- 90-day rolling window — oldest deleted as new arrives
- ~28M rows estimated (1,870 coins x 7 exchanges x 90d x 24h)

### coin_history
- coin · real_cap · recorded_cap · category
- volume_24h · confidence_days · recorded_at
- Stores classification history forever

### strategy_versions
- method · version · parameters_json
- date_created · parent_version · cooldown_until

### review_decisions
- date · method · version · change · reasoning
- evidence · hypothesis · confidence
- approved_by · outcome_status

### bots
- id · exchange_id · name · method
- trading_on · dca_on · reserve_floor · resume_threshold
- auto_resume · profit_coin · max_trades · settings_json

### exchanges
- id · user_id · exchange · custom_name
- api_key_enc · secret_enc · uid_fingerprint · active

### reserve_wallets
- id · user_id · balance_usdt
- total_deposited · total_deducted · last_updated

### referrals
- id · referrer_user_id · referred_user_id
- created_at · total_earned

### owner_balance
- accumulated_fees_usdt · last_transfer_date
- last_transfer_amount · total_transferred_all_time

---

## API Endpoints — Current (Phase 3)

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | /dashboard | Serve dashboard.html |
| GET | /status | Bot status + BTC price |
| GET | /positions | Open positions with live P&L |
| GET | /trades | Last 50 trades |
| GET | /history | Closed positions + realized P&L |
| GET | /balance-history | Capital chart data |
| GET | /config | Current config.py values |
| POST | /config | Update config from dashboard |
| POST | /start | Start bot loop |
| POST | /stop | Stop bot loop |
| POST | /positions/{id}/close | Close position (market sell) |
| POST | /positions/{id}/add | Add funds to position |
| POST | /record-balance | Save daily balance snapshot |

---

## API Endpoints — Planned (Phase 5-7)

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | /webhooks/tradingview | TradingView open signals |
| GET/POST | /bots | Create · read · update · delete bots |
| GET/POST | /exchanges | Manage exchange connections |
| GET | /research/api/v1/summary | All methods ranked (read-only) |
| GET | /research/api/v1/method/{id} | Single method full history |
| GET | /research/share/{token} | Temporary signed research URL |
| GET | /{ADMIN_PATH} | Admin panel (secret URL from .env) |
| POST | /stripe/webhook | Stripe billing events (Phase 7) |
| GET | /health | Health check endpoint |

---

## Security

- API keys encrypted with Fernet before storing in DB
- Admin URL stored in .env only — never in code
- CORS — non-averionbot.com domains blocked
- Rate limiting per user on all endpoints
- Research API: read-only GET only — no mutations
- Signed URLs: 7-day expiry for research sharing
- Withdrawal permissions NEVER enabled on exchange API keys

---

## Exchange Connection Flow

1. User enters API key + secret in Add Exchange modal
2. System tests connection via CCXT
3. If valid → encrypt with Fernet → store in DB
4. UID fingerprint captured for anti-fraud Layer 2
5. Exchange appears in Home tab exchange cards
6. Bot can now trade on this exchange

---

## Data Flow Per 60-Second Cycle

1. Fetch live prices for all coins (CCXT)
2. Check each open position:
   a. Has price dropped X% from last buy? → DCA queue
   b. Has price reached TP target? → Arm trailing
   c. Is trailing armed and price pulled back? → Market sell
3. Execute smart queue (one DCA per cycle)
4. Update all P&L calculations
5. Check ST flags on all exchanges
6. Save any new trades to DB
7. Sleep until next cycle

## Virtual Wallet Tables (Phase 5)

### virtual_wallets
- id · user_id · exchange_id
- name (user defined e.g. Long Test 1)
- currency (USDT · RVN · BTC etc)
- allocation_type (fixed · all)
- allocation_amount (fixed amount · null if all)
- current_balance
- created_at · updated_at

### wallet_bot_assignments
- id · wallet_id · bot_id
- assigned_at
- unassigned_at (null if still active)

### wallet_transactions
- id · wallet_id · position_id
- type (deposit · dca_debit · tp_credit · fee_debit)
- amount · balance_after
- created_at

### How bots share capital
- Same wallet = shared balance + shared queue
- Different wallet = isolated balance + isolated queue
- wallet_transactions tracks every movement
- Full audit trail per wallet per bot

## Updated Schema — New Columns and Tables (Phase 4-5)

### positions table — new columns needed
- wallet_id: links position to virtual wallet
- standby_amount: remaining USDT in standby (0 if none)
- standby_price: target price to trigger standby buy
- standby_timeout_at: when standby expires
- dust_amount: remaining coin balance below minimum order
- dust_currency: which coin is dust
- is_manual: boolean — manual bot position or smart bot

### exchanges table — new columns needed
- paused_at: timestamp when exchange paused
- pause_reason: API_KEY_INVALID · RATE_LIMIT · MANUAL · DELISTED
- pause_type: temporary · permanent
- reconnect_attempts: count of reconnection tries

### New Table: fee_debt
- id · user_id · exchange_id
- position_id (which trade generated the debt)
- amount_usdt (fee owed)
- trade_profit (profit that generated this fee)
- created_at
- paid_at (null if unpaid)
- paid_from_deposit_id (links to reserve deposit)

### New Table: standby_orders
- id · position_id · bot_id · wallet_id
- standby_amount (USDT remaining to buy)
- target_price (DCA level price to trigger)
- dca_level (which level this standby is for)
- timeout_at (when standby expires)
- created_at · triggered_at · expired_at
- status: active · triggered · expired · cancelled

### Redis Key Structure
- prices:{exchange}:{coin} → current price (TTL: 90s)
- prices:updated_at → last fetch timestamp
- st_flags:{exchange}:{coin} → ST status (TTL: 90min)
- bot:running → boolean (TTL: 120s heartbeat)
# Admin System

> Admin panel · all 5 tabs · controls · security.
> Completely separate from user dashboard.

---

## Access

- Secret URL stored in .env only — never in code — never on GitHub
- Format: averionbot.com/ops-XXXX (random string set in .env)
- Security layers: Secret URL + Password + IP whitelist + 2FA + 5-fail lockout
- Admin accounts: no fee · no reserve wallet needed

---

## Tab 1 — Platform Overview

- Total users · active bots · total open/closed trades
- Platform profit this month
- Outstanding fees · who owes what
- Server resource summary
- Referral payout summary
- New user signups this week/month

---

## Tab 2 — Server Health

| Metric | Display |
|--------|---------|
| CPU % | Live + 24h chart |
| RAM % | Live + 24h chart |
| Disk % | Live + trend |
| Uptime | Days · hours · minutes |
| Bot heartbeat | Last loop timestamp |
| PM2 status | Running · stopped · error |
| DB size | Current + growth rate |
| Last backup | Timestamp + file size |
| CCXT version | Current installed version |
| Exchange API status | All 7 exchanges green/red |
| Trades per user | Average load distribution |
| Loop time | How long each 60s cycle takes |
| Estimated capacity | Max trades before performance degrades |

---

## Tab 3 — Users

### User List Columns
- Email · phone · join date · plan · last active
- Trade count: 67/100 (Paper: 25/30 · Live: 42)
- Reserve wallet balance
- Referral code · users referred · monthly income
- Fee override setting
- Trade limit override
- Suspend toggle

### Per User Actions
- View full trade history
- Set fee override (0% · 10% · 20% custom)
- Set trade limit override
- Set referral rate override
- Add free trial credit
- Suspend account (existing positions continue to TP)
- Delete account (anonymize + purge)

---

## Tab 4 — Smart Mode Limits

### Per Category Settings
- Min/max spacing (admin adjustable anytime)
- Min/max size multiplier
- Min/max TP%
- Min/max trail%

### Performance Display
- Win rate per category
- Average hold time
- Average profit per trade
- Volume weights per coin
- Coin confidence levels breakdown

### All Automated
- Admin reviews results only
- No manual parameter setting
- System calculates within admin-set bounds

---

## Tab 5 — System Controls

### Exchange Toggles
- Global ON/OFF switch (all exchanges)
- Per exchange ON/OFF + custom maintenance note
- Customer dashboard shows maintenance message when OFF

### Bot Controls
- Force restart all bots
- Force DB backup now
- Emergency stop all (kills all positions — use carefully)

### Owner Wallet Management
- Pending accumulated fees display
- Transfer threshold setting (default $10 · adjustable)
- Month-end force transfer setting
- Transfer history log
- [Transfer Now] button — manual transfer anytime
- Owner wallet addresses (TRC20 + BEP20) — editable

### Resource Monitor
- Per-trade CPU/RAM cost
- Max capacity estimate
- Performance trend chart

---

## Admin Telegram Alerts

Admin receives ALL alerts in Alerts channel:
- Any user reserve wallet empty
- Any ST flag detected
- Server health threshold breached
- Bot crashed or restarted
- Failed DB backup
- CoinGecko API failure
- Exchange API error
- Any coin reclassified

---

## Security Details

| Layer | Method |
|-------|--------|
| 1 | Secret URL (random string in .env) |
| 2 | Password authentication |
| 3 | IP whitelist (Hetzner static IP only) |
| 4 | 2FA via Telegram |
| 5 | 5 failed attempts → lockout + alert |

Never share admin URL.
Never hardcode admin URL in any file.
Only in .env which is gitignored.

## Admin Dashboard — Final Design (LOCKED)

### Design Philosophy
- Telegram handles real-time alerts instantly
- Dashboard = morning 60-second review
- Most critical info visible without scrolling
- Server health collapsed by default (Telegram alerts if critical)
- Everything changeable — layout never hardcoded

### Single Page + Tabs Structure

#### TOP BAR (always visible · never scrolls)
One line shows everything is fine or not:
🟢 BOT RUNNING · Cycle 4521 · 1.8s ago
🔴 BOT STOPPED · Last seen 14 minutes ago

#### SECTION 1 — Active Alerts
Only shows when something needs attention
Empty = everything fine (show: "✅ All systems normal")
Examples:
- 🔴 Exchange MEXC paused — User #3 [View]
- 🔴 Bot crashed at 14:23 — auto-restarted [Logs]
- 🟡 User #5 reserve low — $2.30 [View]
- 🟡 API key expiring — User #7 in 3 days [View]
- 🟢 CCXT upgraded 4.5.56 → 4.5.57

#### SECTION 2 — Yesterday Summary
- Trades closed · Fees collected · New users
- Owner wallet balance · [Transfer to Wallet] button

#### SECTION 3 — Cron Status
Compact row — click to expand + re-run:
03:00 ✅ · 03:30 ✅ · 04:00 ❌ · 04:30 ⚠️ · 05:00 —
Click any step → expand → [Re-run] [Logs] [Copy]

#### SECTION 4 — Server Health (collapsed by default)
CPU · RAM · Disk · Uptime
Expand only when needed
Telegram already alerts if threshold crossed
[▼ Show Server Health]

### Tabs (for detail)

Tab 1 — Users
- Table: ID · email · bots · open trades
  · profit · fees · reserve · consumption · status
- Sortable by any column
- Search by email or ID
- Click row → expand:
  · Exchanges + status
  · Active bots
  · Recent trades
  · Server consumption % estimate

Tab 2 — Cron Logs
- Full log per step with [Copy] button
- Re-run any step independently
- Historical runs (last 7 days)

Tab 3 — Platform Stats
- Total users · bots · positions
- Total capital under management
- Total profit all time
- Total fees · owner wallet
- Simple charts: profit · fees · growth

Tab 4 — Coin Categories
- 5 categories with settings
- Edit spacing · multiplier · min · max inline
- Last classification timestamp
- Recent reclassifications

Tab 5 — Controls
- Component toggles (CoinGecko · CMC · Telegram etc)
- Emergency: [STOP ALL LIVE TRADING]
- Emergency: [PAUSE NEW POSITIONS]
- [RESTART BOT]
- Backup status · CCXT version

### Key Principles
- Alerts section empty = platform healthy
- Server health = Telegram's job · not dashboard's
- Everything built in separate components
- Layout changeable without touching logic
- [Copy] on every log · every error
- No hardcoded values · all from DB/Redis
# Phase Roadmap

> Averion development phases from proof of life to marketplace.

---

## Phase 1 — Proof of Life ✅ COMPLETE
**Goal:** Connect and place first paper buy

- MEXC via CCXT ✅
- Live BTC price ✅
- Paper buy console ✅
- Code on GitHub ✅

---

## Phase 2 — Paper Bot ✅ COMPLETE
**Goal:** Full DCA engine running 100 coins

- SQLite + WAL ✅
- DCA from LAST BUY PRICE ✅
- Widening spacing ✅
- Trailing TP ✅
- 100 coins MEXC ✅

---

## Phase 3 — Dashboard ✅ COMPLETE
**Goal:** Production web app accessible from any device

- 13 API endpoints ✅
- Home tab: 5 stats + fees + exchange cards ✅
- Exchange Detail: chart + bots ✅
- Bots tab L1+L2: positions + search + filters ✅
- History tab: 6 stats + fees 20% + net + date range ✅
- Settings tab: account info only ✅
- Auto responsive CSS ✅
- Saudi Arabia timezone ✅

---

## Phase 3.5 — Prep Files ✅ COMPLETE
**Goal:** Hetzner ready before server arrives

- requirements.txt ✅
- .env.example ✅
- .gitignore ✅
- README.md ✅
- automation/daily_cron.sh ✅
- automation/weekly_cron.sh ✅
- /docs folder with markdown documentation ✅

---

## Phase 4 — Live Trading ⏳ NEXT
**Goal:** First real order on Hetzner server

### Replit remaining (before Hetzner):
- Item 24: Bots tab flat list redesign
- Item 25: Updated documentation
- Item 26: Dashboard comment markers

### Hetzner Day 1:
- Server setup + security baseline
- Clone GitHub + folder structure
- Create .env file
- pm2 start + startup + save
- Cron jobs installed and tested
- UptimeRobot monitoring
- 3 Telegram channels configured
- GitHub Actions auto-deploy

### Hetzner Day 2:
- Buy averionbot.com domain
- Nginx reverse proxy
- Let's Encrypt HTTPS
- Test live $1 MEXC order (PAPER_MODE=false)

### Days 3-16:
- Paper trading 24/7
- All 10 entry methods collecting data
- Excel reports generated daily
- Monitor health checks

### Day 17+:
- Upload Excel to Claude → optimize parameters
- Live trading with validated parameters

---

## Phase 5 — Smart Systems
**Goal:** Full adaptive platform

- Smart DCA queue (Loss% ÷ USDT scoring)
- 10 entry methods running simultaneously
- Research system + MoM + decision history
- Auto-classification engine
- Cap protection system
- Volume-weighted parameters
- Bot creation wizard (7 steps)
- Trade limits system
- Reserve wallet system
- Referral system 3%
- Two bot toggles (Trading + DCA)
- Reserve floor + auto-resume
- Recovery buy system REMOVED
- TradingView webhook

---

## Phase 5.5 — Backtesting
**Goal:** Validate Smart DCA equations

- Grid search coefficients
- Out-of-sample testing
- Walk-forward validation
- MDD optimization
- Per-category tuning

---

## Phase 6 — Full Platform
**Goal:** Multi-user production

- PostgreSQL (migrate from SQLite)
- JWT authentication
- All 7 exchanges fully integrated
- Short trading enabled
- PWA installable
- Docker containerization
- Admin panel full feature set

---

## Phase 7 — Public Launch
**Goal:** Paying subscribers

- Reserve wallet live (NOWPayments)
- Referral system live
- Anti-fraud 5 layers
- Stripe for fiat payments
- KYC/AML basics
- Terms of service
- Risk disclosures

---

## Phase 8 — Marketplace
**Goal:** Strategy providers in dashboard

- Signal provider listing
- Vetting system (win rate · history · drawdown)
- One-click subscribe
- Webhook auto-connected
- Averion takes 10-15% subscription + 20% performance fee

---

## Timeline Estimate

| Phase | Milestone | When |
|-------|-----------|------|
| 4 | Hetzner live | ~10 days (ID verification) |
| 5 | Smart systems | Month 3 |
| 5.5 | Backtesting | Month 6 |
| 6 | Multi-user | Month 9 |
| 7 | Public launch | Month 12 |
| 8 | Marketplace | Year 2 |
# AI Reviews and Resolutions

> External AI feedback on Averion v4.6 spec.
> Our responses and final decisions.
> Do NOT re-raise resolved points.

---

## Review Date: May 2026
## AIs: DeepSeek · Gemini · ChatGPT · Grok · Perplexity

---

## Point 1 — GitHub Token in PDF
**Raised by:** All AIs
**Concern:** Live token exposed in PDF is security risk.
**Resolution:** ACKNOWLEDGED — keeping token in docs temporarily.
Token needed for new Claude to auto-fetch code.
Will remove when averionbot.com launches publicly.
**Status:** ✅ Resolved — intentional decision

---

## Point 2 — Dead Coin Scenario
**Raised by:** ChatGPT · Grok
**Concern:** No max DCA levels means bot throws money at dead coins forever.
**Resolution:** LOCKED
- ST flag from exchange = ONLY forced close
- If exchange marks coin ST → auto sell immediately via CCXT
- Dead coins without ST flag = nothing we can do (position holds)
- Smart queue handles capital priority naturally
- User always controls their own exit
- Works on all 7 exchanges via CCXT
**Status:** ✅ Resolved — ST flag is the solution

---

## Point 3 — Reclassification Mid-Ladder
**Raised by:** Gemini
**Concern:** Reclassification could trigger phantom DCA buy at 3am.
**Resolution:** NOT A BUG
- Our trigger = percentage drop from last buy price (not fixed threshold)
- Price already dropped MORE than new spacing = DCA fires correctly at better price
- Market order at current price = always best available
- Smart queue rescores after every buy
- Gemini misunderstood our percentage-based trigger logic
**Status:** ✅ Resolved — not a bug in Averion

---

## Point 4 — Slippage on Microcaps
**Raised by:** Gemini · ChatGPT · Grok
**Concern:** Market orders on thin order books = massive slippage.
**Resolution:** LOCKED — new slippage handling rule:
1. DCA triggers → check order book depth
2. If available at target price >= $1 minimum → buy at target price
3. If available < $1 minimum → buy $1 market order
4. Maximum slippage exposure = $1 only
5. Never chase more than $1 above target
6. Always executes something — never stuck
7. ALL orders are market orders always
**Status:** ✅ Resolved — $1 max slippage rule locked

---

## Point 5 — State Machine Definition
**Raised by:** ChatGPT
**Concern:** No formal state machine = race conditions and bugs.
**Resolution:** NOT NEEDED for Averion
- Last buy price updates after every buy → next trigger always moves
- Cannot fire twice — percentage trigger naturally prevents duplicates
- Single sequential loop → no race conditions possible
- Smart queue rescores automatically after every action
- ChatGPT assumed complex multi-threaded system
- Averion uses single sequential loop — much simpler
**Status:** ✅ Resolved — not needed

---

## Point 6 — 3am Cron Staggering
**Raised by:** Gemini
**Concern:** All maintenance at 3am = massive I/O spike = DB lock risk.
**Resolution:** LOCKED — new staggered schedule:
- Every hour: health check + OHLCV + ATR
- 03:00 Infrastructure: CCXT upgrade · restart · backup
- 03:30 Data & Classification: CoinGecko · classify · recalculate · volume-weighted
- 04:00 Reporting: snapshot · metrics · Excel · Telegram report
- 04:30 Sunday only: cleanup · disk · DB VACUUM · weekly report
**Status:** ✅ Resolved — schedule locked

---

## Point 7 — PAPER_MODE as Environment Variable
**Raised by:** DeepSeek
**Concern:** PAPER_MODE in config.py = accidental live trading risk.
**Resolution:** LOCKED
- PAPER_MODE moves to .env file (never in config.py)
- Default = true always (safe by default)
- 10 second countdown warning when switching to LIVE mode
- Red banner across full topbar in LIVE mode
- No conflict with customer paper trades (90-day auto-close handles that)
**Status:** ✅ Resolved — locked

---

## Point 8 — Reserve Wallet Blockchain Listener
**Raised by:** Gemini
**Concern:** No mechanism defined for detecting user deposits.
**Resolution:** LOCKED — use NOWPayments gateway
- 0.5% fee per deposit
- Unique address per user (no memo confusion)
- Funds auto-forward to owner USDT wallet
- TRC20 recommended (cheapest ~$1 network fee)
- $10 minimum top-up
- $5 free trial credit for new users
- Phase 7 start with NOWPayments → switch to HD wallet when scaling
**Status:** ✅ Resolved — NOWPayments locked for Phase 7

---

## Point 9 — Short DCA Mechanics
**Raised by:** ChatGPT · Perplexity
**Concern:** Short on spot exchanges undefined · may require margin.
**Resolution:** LOCKED
- Pure spot only — no margin · no borrowing · no leverage
- User must already hold the coin on exchange
- Only sell if quantity >= exchange minimum order size
- Profit coin = USDT or base coin — works for both Long and Short
- Works on all spot exchanges via CCXT
**Status:** ✅ Resolved — spot only locked

---

## Point 10 — Crash Detection
**Raised by:** All AIs
**Concern:** No crash detection defined (X% in Y minutes undefined).
**Resolution:** NOT NEEDED
- Smart queue IS the crash protection
- Queue executes ONE DCA at a time
- Capital depletes gradually — never dumps all at once
- Natural brake through capital limitation
- ST flag handles true emergencies
- Queue + capital limit = sufficient protection
- No special crash detection feature needed
**Status:** ✅ Resolved — smart queue handles it

---

## Points Deliberately Rejected

| Point | Reason |
|-------|--------|
| Add max DCA levels | Conflicts with Never Stuck philosophy |
| Use limit orders | Conflicts with market orders philosophy |
| Add high water mark | Intentional simplicity — monthly fresh start |
| 60s interval too slow | Intentional — DCA swing not scalping |
| One DCA per cycle too slow | Intentional — predictable over speed |
| PostgreSQL now | Phase 6 — not needed for MVP |
| Full AML/KYC now | Phase 7 — premature |
| Prometheus/Grafana | Not needed for personal bot |
| Geographic redundancy | Way too early |
| Referral 7-day change | Intentional lock — prevents abuse |

---

## Key Lesson From Reviews

When spec clearly explains:
- Percentage-based trigger (not fixed threshold)
- Last buy price always updates after every buy
- Single sequential loop (not multi-threaded)
- Smart queue scoring logic

AIs give relevant recommendations instead of wrong ones.
Clear spec = better AI advice.
This is why markdown documentation exists.
# Project Overview

> What Averion is, who it is for, and what makes it different.

---

## What Is Averion

Averion is a personal automated crypto spot trading platform.
Runs 24/7 on Hetzner cloud server (~€3.99/month).
Accessible from any device via secure web dashboard.
Built to replace 3commas with no per-position limits.
Designed from day one for future public launch.

---

## Core Concept

Buy low · average lower · sell at profit.
Fully automated · no daily intervention needed.
Put money in · forget it · collect profits.

---

## Who It Is For

### Phase 1-4 (Now)
- Bader only — personal trading
- Paper mode first · live after Hetzner

### Phase 6-7 (Future)
- Public subscribers paying 20% performance fee
- Anyone wanting automated DCA without monthly subscriptions

---

## Main Goals

| Goal | Detail |
|------|--------|
| Replace 3commas | Full control · own server · no limits |
| No monthly fee | Users pay only when they profit |
| Set and forget | Bot never stops · detects funds in 60s |
| Survivability | Never blows up · survives crashes |
| Self-improving | 10 entry methods compete · best wins |
| Fair pricing | 20% of profits only · loss months = $0 |

---

## Supported Exchanges (via CCXT)

| Exchange | Status |
|----------|--------|
| MEXC | ✅ Live now on Replit |
| Binance | Phase 6 |
| KuCoin | Phase 6 |
| OKX | Phase 6 |
| Gate.io | Phase 6 |
| Bybit | Phase 6 |
| Bitget | Phase 6 |

---

## Core Features

### Trading
- Long DCA — buy dips · sell at profit
- Short DCA — sell rises · buy back cheaper
- Trailing take profit — follows price up
- Smart DCA queue — best recovery first
- Market orders only — guaranteed execution
- Unlimited DCA levels — never stuck

### Intelligence
- 10 entry methods competing simultaneously
- Auto-classification into 5 market cap categories
- Cap protection against fake pumps
- Volume-weighted parameters per category
- 90-day rolling data window per coin
- Self-improving research system

### Business
- 20% performance fee on profits only
- Reserve wallet pre-funding (NOWPayments)
- Referral system 3% forever
- Free $5 trial credit for new users

### Operations
- PWA — works on any browser including iPhone Face ID
- 3 Telegram channels (Trades · Alerts · Reports)
- Automated daily maintenance at 3am
- GitHub Actions auto-deploy
- UptimeRobot external monitoring

---

## What Makes Averion Different

| Feature | 3commas | Averion |
|---------|---------|---------|
| Monthly fee | Yes $29-99 | No |
| Performance fee | No | 20% profits only |
| Position limits | Yes | No limits |
| Server control | No | Full control |
| Self-improving | No | Yes (10 methods) |
| Market cap aware | No | Yes (5 categories) |
| Cap protection | No | Yes (original idea) |
| Never stuck | No | Yes |
| Cost | $29-99/month | €3.99/month server |

---

## Long-Term Vision

Platform gets smarter every year.
10 entry methods compete → worst deleted → best survives.
Intelligence compounds over time automatically.
Eventually becomes a marketplace where signal providers
list their strategies for subscribers to use.
# Branding and Vision

> Averion identity · design language · positioning.

---

## Identity

| Item | Detail |
|------|--------|
| App Name | Averion |
| Tagline | Intelligent DCA Trading · Automate. Adapt. Grow. |
| Domain | averionbot.com (buy on Hetzner Day 2) |
| GitHub | github.com/baderbalubaid/Averion |

---

## Logo
- DCA ladder bars inside A triangle
- Gold arc + silver legs + blue bars
- CONFIRMED — do not change

---

## Typography
- Font: Inter (Google Fonts)
- Weights used: 900 · 800 · 700 · 600 · 500 · 400
- Letter spacing: tight for headings · normal for body

---

## Color System

| Color | Hex | Usage |
|-------|-----|-------|
| Indigo | #6366F1 | Accent · buttons · active states |
| Green | #10D98A | Profit · active · ON toggles · success |
| Amber | #F59E0B | Fees · warnings · stuck positions |
| Red | #F4645F | Loss · critical · danger · destructive |
| Blue | #38BDF8 | Info · MEXC badge · positions count |
| Purple | #A78BFA | DCA count · TP Armed · Bitget badge |
| Orange | #FB923C | Bybit badge |
| Teal | #14B8A6 | Phase 3.5 · secondary accent |

### Backgrounds
| Name | Hex | Usage |
|------|-----|-------|
| Page | #07070F | Main background |
| Card | #0E0E1C | Cards · sidebar · topbar |
| Card2 | #141428 | Deeper cards · inputs |
| Card3 | #1E1E3A | Table headers · hover |
| Border | #1E1E35 | All borders |
| Border2 | #252540 | Stronger borders |

### Text
| Name | Hex | Usage |
|------|-----|-------|
| Primary | #F0F0FF | Main text |
| Secondary | #8888AA | Muted text |
| Tertiary | #55556A | Very muted · labels |

---

## Design Philosophy

### Style Reference
- Linear · Vercel · Stripe · TradingView
- Minimal · clean · premium · professional
- Dark theme only — no light mode

### What Averion IS
- Trustworthy financial tool
- Clean and precise
- Premium but accessible
- Confidence-inspiring

### What Averion is NOT
- No neon colors
- No glow effects
- No gambling casino feel
- No flashy animations
- No cluttered UI

---

## UI Components

### Cards
- Background: #0E0E1C
- Border: 1px solid #1E1E35
- Border radius: 16px
- Top gradient accent line per card type
- Hover: translateY(-1px) slight lift

### Buttons
- Primary: #6366F1 background · white text
- Success: #10D98A background · dark text
- Danger: #F4645F background · white text
- Ghost: #141428 background · border · muted text
- Border radius: 9px
- Active: scale(0.98) slight press

### Badges
- Active: green tint background · green text · green border
- Stuck: amber tint · amber text · amber border
- Critical: red tint · red text · red border
- Queued: blue tint · blue text · blue border
- TP Armed: purple tint · purple text · purple border
- Closed: gray tint · gray text · gray border

---

## Responsive Layout

| Screen | Layout |
|--------|--------|
| Desktop (≥1024px) | Full sidebar 220px + content |
| Tablet (768-1023px) | Icon-only sidebar 60px + content |
| Mobile (<768px) | No sidebar · bottom nav 4 tabs |

100% automatic CSS — no JavaScript toggle needed

---

## Positioning

### vs 3commas
- No monthly subscription
- Own server full control
- No position limits
- Self-improving intelligence

### vs Binance Grid Bot
- Multi-exchange
- Market cap aware
- Research system
- Performance fee only

### vs Manual Trading
- 24/7 automated
- No emotion
- Consistent execution
- Never misses a DCA

---

## Future Brand Extensions
- averionbot.com — main platform
- docs.averionbot.com — documentation
- status.averionbot.com — uptime page
- api.averionbot.com — developer API
-- Averion PostgreSQL Schema
-- Run this on Hetzner Day 1
-- Command: psql -U averion -d averion < schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════
-- USERS
-- ═══════════════════════════════
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    referral_code VARCHAR(20) UNIQUE,
    referred_by INTEGER REFERENCES users(id),
    fee_override DECIMAL(5,2) DEFAULT 20.00,
    is_admin BOOLEAN DEFAULT FALSE,
    is_zero_fee BOOLEAN DEFAULT FALSE,
    is_suspended BOOLEAN DEFAULT FALSE,
    free_trial_credit DECIMAL(10,2) DEFAULT 5.00,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP
);

-- ═══════════════════════════════
-- EXCHANGES
-- ═══════════════════════════════
CREATE TABLE exchanges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange VARCHAR(50) NOT NULL,
    custom_name VARCHAR(100),
    api_key_enc TEXT NOT NULL,
    secret_enc TEXT NOT NULL,
    uid_fingerprint VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    paused_at TIMESTAMP,
    pause_reason VARCHAR(50),
    pause_type VARCHAR(20),
    reconnect_attempts INTEGER DEFAULT 0,
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- VIRTUAL WALLETS
-- ═══════════════════════════════
CREATE TABLE virtual_wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    name VARCHAR(100) NOT NULL,
    currency VARCHAR(20) DEFAULT 'USDT',
    allocation_type VARCHAR(10) DEFAULT 'fixed',
    allocation_amount DECIMAL(20,8),
    current_balance DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- BOTS
-- ═══════════════════════════════
CREATE TABLE bots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    name VARCHAR(100) NOT NULL,
    method VARCHAR(50) DEFAULT 'smart',
    direction VARCHAR(10) DEFAULT 'long',
    trading_on BOOLEAN DEFAULT TRUE,
    dca_on BOOLEAN DEFAULT TRUE,
    base_order DECIMAL(20,8) DEFAULT 1.00,
    dca_percent DECIMAL(5,2) DEFAULT 7.00,
    spacing_multiplier DECIMAL(5,2) DEFAULT 1.4,
    size_multiplier DECIMAL(5,2) DEFAULT 1.5,
    take_profit_percent DECIMAL(5,2) DEFAULT 5.00,
    trailing_percent DECIMAL(5,2) DEFAULT 2.00,
    profit_coin VARCHAR(20) DEFAULT 'USDT',
    reserve_floor DECIMAL(20,8) DEFAULT 50.00,
    resume_threshold DECIMAL(20,8) DEFAULT 75.00,
    auto_resume BOOLEAN DEFAULT TRUE,
    max_trades INTEGER DEFAULT 0,
    dca_checkpoint INTEGER DEFAULT 0,
    is_paper BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'active',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- POSITIONS
-- ═══════════════════════════════
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id),
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    coin VARCHAR(20) NOT NULL,
    direction VARCHAR(10) DEFAULT 'long',
    status VARCHAR(20) DEFAULT 'open',
    avg_cost DECIMAL(20,8),
    avg_sell_price DECIMAL(20,8),
    quantity DECIMAL(20,8) DEFAULT 0,
    total_invested DECIMAL(20,8) DEFAULT 0,
    total_sold_usdt DECIMAL(20,8) DEFAULT 0,
    dca_count INTEGER DEFAULT 0,
    last_buy_price DECIMAL(20,8),
    last_sell_price DECIMAL(20,8),
    tp_armed BOOLEAN DEFAULT FALSE,
    peak_price DECIMAL(20,8),
    queued BOOLEAN DEFAULT FALSE,
    standby_amount DECIMAL(20,8) DEFAULT 0,
    standby_price DECIMAL(20,8),
    standby_timeout_at TIMESTAMP,
    dust_amount DECIMAL(20,8) DEFAULT 0,
    dust_currency VARCHAR(20),
    is_manual BOOLEAN DEFAULT FALSE,
    is_paper BOOLEAN DEFAULT TRUE,
    category VARCHAR(20),
    entry_method VARCHAR(20),
    opened_at TIMESTAMP DEFAULT NOW(),
    closed_at TIMESTAMP,
    close_reason VARCHAR(50),
    short_buyback_order_id VARCHAR(100),
    short_buyback_reserved_usdt DECIMAL(20,8) DEFAULT 0,
    pending_buyback BOOLEAN DEFAULT FALSE
);

-- ═══════════════════════════════
-- TRADES
-- ═══════════════════════════════
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    bot_id INTEGER REFERENCES bots(id),
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    coin VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    usdt_amount DECIMAL(20,8) NOT NULL,
    exchange_fee DECIMAL(20,8) DEFAULT 0,
    fee_currency VARCHAR(20),
    reason VARCHAR(50),
    order_type VARCHAR(20) DEFAULT 'market',
    exchange_order_id VARCHAR(100),
    is_paper BOOLEAN DEFAULT TRUE,
    dca_level INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- STANDBY ORDERS
-- ═══════════════════════════════
CREATE TABLE standby_orders (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    bot_id INTEGER REFERENCES bots(id),
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    standby_amount DECIMAL(20,8) NOT NULL,
    target_price DECIMAL(20,8) NOT NULL,
    dca_level INTEGER NOT NULL,
    timeout_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    triggered_at TIMESTAMP,
    expired_at TIMESTAMP
);

-- ═══════════════════════════════
-- RESERVE WALLETS
-- ═══════════════════════════════
CREATE TABLE reserve_wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    balance_usdt DECIMAL(20,8) DEFAULT 0,
    total_deposited DECIMAL(20,8) DEFAULT 0,
    total_deducted DECIMAL(20,8) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- RESERVE DEPOSITS
-- ═══════════════════════════════
CREATE TABLE reserve_deposits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    nowpayments_id VARCHAR(100) UNIQUE,
    amount_sent DECIMAL(20,8),
    amount_received DECIMAL(20,8),
    network VARCHAR(20),
    tx_hash VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    credited_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- FEE DEBT
-- ═══════════════════════════════
CREATE TABLE fee_debt (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    position_id INTEGER REFERENCES positions(id),
    amount_usdt DECIMAL(20,8) NOT NULL,
    trade_profit DECIMAL(20,8),
    paid_at TIMESTAMP,
    paid_from_deposit_id INTEGER REFERENCES reserve_deposits(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- BALANCE HISTORY
-- ═══════════════════════════════
CREATE TABLE balance_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    value_usdt DECIMAL(20,8),
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- COIN HISTORY (Classification)
-- ═══════════════════════════════
CREATE TABLE coin_history (
    id SERIAL PRIMARY KEY,
    coin VARCHAR(20) NOT NULL,
    exchange VARCHAR(50),
    real_cap DECIMAL(30,2),
    recorded_cap DECIMAL(30,2),
    category VARCHAR(20),
    volume_24h DECIMAL(30,2),
    confidence_days INTEGER DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- OHLCV HOURLY
-- ═══════════════════════════════
CREATE TABLE ohlcv_hourly (
    id SERIAL PRIMARY KEY,
    coin VARCHAR(20) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20,8),
    high DECIMAL(20,8),
    low DECIMAL(20,8),
    close DECIMAL(20,8),
    volume DECIMAL(30,8),
    atr_14 DECIMAL(20,8),
    UNIQUE(coin, exchange, timestamp)
);

-- ═══════════════════════════════
-- OWNER BALANCE
-- ═══════════════════════════════
CREATE TABLE owner_balance (
    id SERIAL PRIMARY KEY,
    accumulated_fees_usdt DECIMAL(20,8) DEFAULT 0,
    last_transfer_date TIMESTAMP,
    last_transfer_amount DECIMAL(20,8),
    total_transferred DECIMAL(20,8) DEFAULT 0
);

-- ═══════════════════════════════
-- REFERRALS
-- ═══════════════════════════════
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_user_id INTEGER REFERENCES users(id),
    referred_user_id INTEGER REFERENCES users(id) UNIQUE,
    total_earned DECIMAL(20,8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- WALLET BOT ASSIGNMENTS
-- ═══════════════════════════════
CREATE TABLE wallet_bot_assignments (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    bot_id INTEGER REFERENCES bots(id),
    assigned_at TIMESTAMP DEFAULT NOW(),
    unassigned_at TIMESTAMP
);

-- ═══════════════════════════════
-- WALLET TRANSACTIONS
-- ═══════════════════════════════
CREATE TABLE wallet_transactions (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES virtual_wallets(id),
    position_id INTEGER REFERENCES positions(id),
    type VARCHAR(30) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    balance_after DECIMAL(20,8),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- INDEXES (Performance)
-- ═══════════════════════════════
CREATE INDEX idx_positions_exchange_status ON positions(exchange_id, status);
CREATE INDEX idx_positions_user_status ON positions(user_id, status);
CREATE INDEX idx_positions_coin_last_buy ON positions(coin, last_buy_price);
CREATE INDEX idx_positions_bot ON positions(bot_id);
CREATE INDEX idx_trades_position ON trades(position_id);
CREATE INDEX idx_trades_user_closed ON trades(user_id, timestamp);
CREATE INDEX idx_balance_history_exchange ON balance_history(exchange_id, recorded_at);
CREATE INDEX idx_ohlcv_coin_exchange_time ON ohlcv_hourly(coin, exchange, timestamp);
CREATE INDEX idx_coin_history_coin ON coin_history(coin, recorded_at);
CREATE INDEX idx_standby_status ON standby_orders(status, target_price);

-- ═══════════════════════════════
-- INITIAL DATA
-- ═══════════════════════════════
INSERT INTO owner_balance (accumulated_fees_usdt, total_transferred)
VALUES (0, 0);

SELECT 'Averion database schema created successfully!' AS result;

-- ═══════════════════════════════
-- TELEGRAM SETTINGS
-- ═══════════════════════════════
CREATE TABLE user_telegram (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    chat_id VARCHAR(100),
    verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(20),
    trade_alerts BOOLEAN DEFAULT TRUE,
    report_alerts BOOLEAN DEFAULT TRUE,
    alert_alerts BOOLEAN DEFAULT TRUE,
    connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- ATTENTION LOG
-- ═══════════════════════════════
CREATE TABLE attention_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    bot_id INTEGER REFERENCES bots(id),
    position_id INTEGER REFERENCES positions(id),
    severity VARCHAR(10) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    message TEXT,
    action_taken VARCHAR(50),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- NOTIFICATION QUEUE
-- ═══════════════════════════════
CREATE TABLE notification_queue (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    chat_id VARCHAR(100),
    message TEXT NOT NULL,
    message_type VARCHAR(30),
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- POSITIONS ARCHIVE
-- ═══════════════════════════════
CREATE TABLE positions_archive (
    LIKE positions INCLUDING ALL
);

-- ═══════════════════════════════
-- STRATEGY VERSIONS
-- ═══════════════════════════════
CREATE TABLE strategy_versions (
    id SERIAL PRIMARY KEY,
    method VARCHAR(20) NOT NULL,
    version INTEGER NOT NULL,
    parameters_json JSONB,
    date_created TIMESTAMP DEFAULT NOW(),
    parent_version INTEGER,
    cooldown_until TIMESTAMP,
    created_by INTEGER REFERENCES users(id)
);

-- ═══════════════════════════════
-- RESEARCH SCORES
-- ═══════════════════════════════
CREATE TABLE research_scores (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER REFERENCES bots(id),
    method VARCHAR(20),
    bot_config_id VARCHAR(20),
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    avg_profit DECIMAL(20,8),
    avg_loss DECIMAL(20,8),
    total_profit DECIMAL(20,8),
    max_drawdown DECIMAL(20,8),
    avg_hold_hours DECIMAL(10,2),
    recovery_speed DECIMAL(10,2),
    promotion_score DECIMAL(10,6),
    rank INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    last_calculated TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- BOT SLOTS AND BUNDLES
-- ═══════════════════════════════
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    free_bot_slots INTEGER DEFAULT 5,
    paid_bot_slots INTEGER DEFAULT 0,
    free_trade_bundle INTEGER DEFAULT 100,
    paid_trade_bundle INTEGER DEFAULT 0,
    trades_used_this_month INTEGER DEFAULT 0,
    bundle_type VARCHAR(20) DEFAULT 'free',
    next_billing_date DATE,
    last_deduction_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════
-- ADDITIONAL INDEXES
-- ═══════════════════════════════
CREATE INDEX idx_attention_log_user ON attention_log(user_id, resolved);
CREATE INDEX idx_notification_queue_sent ON notification_queue(sent, created_at);
CREATE INDEX idx_research_scores_method ON research_scores(method, promotion_score);
CREATE INDEX idx_strategy_versions_method ON strategy_versions(method, version);

SELECT 'Schema update complete — all tables created!' AS result;

-- ═══════════════════════════════
-- SCHEMA UPDATES — Additional Columns
-- ═══════════════════════════════

-- DCA Checkpoint fields for bots
ALTER TABLE bots ADD COLUMN IF NOT EXISTS dca_checkpoint_level INTEGER DEFAULT 0;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS dca_checkpoint_on BOOLEAN DEFAULT FALSE;

-- DCA Checkpoint tracking for positions
ALTER TABLE positions ADD COLUMN IF NOT EXISTS checkpoint_reached BOOLEAN DEFAULT FALSE;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS checkpoint_reached_at TIMESTAMP;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS checkpoint_level_reached INTEGER DEFAULT 0;

-- Virtual wallet standby reserved amount
ALTER TABLE virtual_wallets ADD COLUMN IF NOT EXISTS standby_reserved DECIMAL(20,8) DEFAULT 0;

-- API key expiry tracking
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS key_expires_at TIMESTAMP;
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS last_alert_sent_at TIMESTAMP;
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS alert_count INTEGER DEFAULT 0;

-- Bot slot tracking per user
ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trade_alerts_on BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS report_alerts_on BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS alert_alerts_on BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bot_slots_total INTEGER DEFAULT 5;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trades_used_this_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS next_billing_date DATE;

SELECT 'Schema updates applied successfully!' AS result;

-- Base coin support
ALTER TABLE bots ADD COLUMN IF NOT EXISTS base_coin VARCHAR(10) DEFAULT 'USDT';

-- Position detail enhancements
ALTER TABLE trades ADD COLUMN IF NOT EXISTS dca_level_price DECIMAL(20,8);
ALTER TABLE trades ADD COLUMN IF NOT EXISTS running_avg_cost DECIMAL(20,8);
ALTER TABLE trades ADD COLUMN IF NOT EXISTS running_quantity DECIMAL(20,8);
ALTER TABLE trades ADD COLUMN IF NOT EXISTS running_total_invested DECIMAL(20,8);

SELECT 'Base coin and position detail columns added!' AS result;

-- ═══════════════════════════════
-- CRITICAL FIXES — v5 Review
-- ═══════════════════════════════

-- Exchange passphrase (KuCoin · OKX · Bitget)
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS passphrase_enc TEXT;
ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS ip_whitelist_confirmed BOOLEAN DEFAULT FALSE;

-- Research bot market regime tracking
ALTER TABLE research_scores ADD COLUMN IF NOT EXISTS regimes_tested JSONB DEFAULT '[]';
ALTER TABLE research_scores ADD COLUMN IF NOT EXISTS bundle_period VARCHAR(7);

-- Subscription billing history
CREATE TABLE IF NOT EXISTS subscription_billing (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    billing_date DATE NOT NULL,
    bot_fee DECIMAL(20,8) DEFAULT 0,
    bundle_fee DECIMAL(20,8) DEFAULT 0,
    total_fee DECIMAL(20,8) DEFAULT 0,
    reserve_before DECIMAL(20,8),
    reserve_after DECIMAL(20,8),
    bots_affected JSONB,
    status VARCHAR(20) DEFAULT 'paid',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Exchange coin limits tracking
CREATE TABLE IF NOT EXISTS exchange_coin_limits (
    id SERIAL PRIMARY KEY,
    exchange_id INTEGER REFERENCES exchanges(id),
    coin VARCHAR(20) NOT NULL,
    min_order_size DECIMAL(20,8),
    min_notional DECIMAL(20,8),
    status VARCHAR(20) DEFAULT 'active',
    status_reason TEXT,
    last_checked TIMESTAMP DEFAULT NOW(),
    UNIQUE(exchange_id, coin)
);

-- Short buyback order history
CREATE TABLE IF NOT EXISTS short_buyback_orders (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    exchange_order_id VARCHAR(100) UNIQUE,
    limit_price DECIMAL(20,8),
    quantity DECIMAL(20,8),
    usdt_reserved DECIMAL(20,8),
    status VARCHAR(20) DEFAULT 'pending',
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Additional indexes
CREATE INDEX IF NOT EXISTS idx_subscription_billing_user ON subscription_billing(user_id, billing_date);
CREATE INDEX IF NOT EXISTS idx_exchange_coin_limits ON exchange_coin_limits(exchange_id, coin);
CREATE INDEX IF NOT EXISTS idx_short_buyback_position ON short_buyback_orders(position_id, status);
CREATE INDEX IF NOT EXISTS idx_reserve_deposits_nowpayments ON reserve_deposits(nowpayments_id, status);

SELECT 'v5 critical fixes applied!' AS result;

-- Auto-renew support for bots and bundles
ALTER TABLE bots ADD COLUMN IF NOT EXISTS auto_renew BOOLEAN DEFAULT FALSE;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS renewal_type VARCHAR(20) DEFAULT 'one-time';

-- Trade bundle tracking per user
CREATE TABLE IF NOT EXISTS trade_bundles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    bundle_type VARCHAR(20) NOT NULL,
    trades_total INTEGER NOT NULL,
    trades_used INTEGER DEFAULT 0,
    price_usdt DECIMAL(10,2),
    auto_renew BOOLEAN DEFAULT FALSE,
    renewal_type VARCHAR(20) DEFAULT 'one-time',
    purchased_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS idx_trade_bundles_user ON trade_bundles(user_id, status);

SELECT 'Auto-renew and bundle tables added!' AS result;

-- ═══════════════════════════════
-- MULTI-TRADE GATE SYSTEM + LIMIT ORDERS
-- ═══════════════════════════════

-- Bot level settings
ALTER TABLE bots ADD COLUMN IF NOT EXISTS trades_per_bot INTEGER DEFAULT 1;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS trades_per_coin INTEGER DEFAULT 1;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS gate_dca_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS gate_timer_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS gate_timer_hours INTEGER DEFAULT 5;
ALTER TABLE bots ADD COLUMN IF NOT EXISTS order_entry_type VARCHAR(10) DEFAULT 'market';
ALTER TABLE bots ADD COLUMN IF NOT EXISTS order_dca_type VARCHAR(10) DEFAULT 'market';

-- Position level tracking
ALTER TABLE positions ADD COLUMN IF NOT EXISTS sequence_number INTEGER DEFAULT 1;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS is_gate_reference BOOLEAN DEFAULT FALSE;
ALTER TABLE positions ADD COLUMN IF NOT EXISTS coin_trade_number INTEGER DEFAULT 1;

SELECT 'Multi-trade gate and limit order columns added!' AS result;

-- Gate reference tracking
ALTER TABLE positions ADD COLUMN IF NOT EXISTS base_coin VARCHAR(10) DEFAULT 'USDT';
ALTER TABLE positions ADD COLUMN IF NOT EXISTS gate_reference_since TIMESTAMP;

-- Pending limit orders
CREATE TABLE IF NOT EXISTS pending_limit_orders (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(id),
    bot_id INTEGER REFERENCES bots(id),
    exchange_id INTEGER REFERENCES exchanges(id),
    order_type VARCHAR(20) NOT NULL,
    exchange_order_id VARCHAR(100) UNIQUE,
    original_quantity DECIMAL(20,8) NOT NULL,
    filled_quantity DECIMAL(20,8) DEFAULT 0,
    remaining_quantity DECIMAL(20,8),
    limit_price DECIMAL(20,8) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    placed_at TIMESTAMP DEFAULT NOW(),
    filled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    last_checked TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pending_limit_orders_status ON pending_limit_orders(status, exchange_id);
CREATE INDEX IF NOT EXISTS idx_pending_limit_orders_position ON pending_limit_orders(position_id);

SELECT 'Final v6 fixes applied!' AS result;

-- ═══════════════════════════════
-- SECURITY AUDIT LOG
-- ═══════════════════════════════
CREATE TABLE IF NOT EXISTS security_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_security_audit_user ON security_audit_log(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_security_audit_event ON security_audit_log(event_type, created_at);

-- Session management columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS session_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS session_expires_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code VARCHAR(10);
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_expires_at TIMESTAMP;

SELECT 'Security tables added!' AS result;
#!/bin/bash
# Averion — Hetzner Day 1 Setup Script
# Run as root: bash hetzner_day1.sh
# Time: ~20 minutes
# SECURITY HARDENED VERSION

set -e
echo "🚀 Starting Averion Day 1 Setup..."
echo "⚠️  Run this as root on fresh Ubuntu 24.04"

# ═══════════════════════════════
# VARIABLES — EDIT BEFORE RUNNING
# ═══════════════════════════════
SSH_PORT=2847
AVERION_USER=averion
DB_PASSWORD=$(openssl rand -hex 16)
echo "Generated DB password stored in /tmp/averion_setup_vars"

# ═══════════════════════════════
# STEP 1 — System Update
# ═══════════════════════════════
echo "📦 Step 1: Updating system..."
apt update && apt upgrade -y
apt install -y unattended-upgrades
dpkg-reconfigure -f noninteractive unattended-upgrades
echo "✅ System updated + auto security updates enabled"

# ═══════════════════════════════
# STEP 2 — Install Dependencies
# ═══════════════════════════════
echo "📦 Step 2: Installing dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-client \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    chrony \
    git \
    ufw \
    curl \
    nano \
    logwatch \
    nodejs \
    npm
echo "✅ Dependencies installed"

# ═══════════════════════════════
# STEP 3 — Create Non-Root User
# ═══════════════════════════════
echo "👤 Step 3: Creating averion user..."
useradd -m -s /bin/bash $AVERION_USER 2>/dev/null || echo "User already exists"
usermod -aG sudo $AVERION_USER
echo "✅ User $AVERION_USER created"

# ═══════════════════════════════
# STEP 4 — SSH Hardening
# ═══════════════════════════════
echo "🔒 Step 4: Hardening SSH..."

# Backup original config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Apply security settings
cat > /etc/ssh/sshd_config << SSHCONF
# Averion Security Hardened SSH Config
Port $SSH_PORT
Protocol 2

# Authentication
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30

# Security
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2

# Allow only averion user
AllowUsers $AVERION_USER
SSHCONF

echo "⚠️  IMPORTANT: Add your SSH public key before restarting SSH!"
echo "Run: mkdir -p /home/$AVERION_USER/.ssh"
echo "Run: echo 'YOUR_PUBLIC_KEY' >> /home/$AVERION_USER/.ssh/authorized_keys"
echo "Run: chmod 700 /home/$AVERION_USER/.ssh"
echo "Run: chmod 600 /home/$AVERION_USER/.ssh/authorized_keys"
echo "Run: chown -R $AVERION_USER:$AVERION_USER /home/$AVERION_USER/.ssh"
echo ""
read -p "Have you added your SSH key? (yes/no): " SSH_CONFIRMED
if [ "$SSH_CONFIRMED" != "yes" ]; then
    echo "❌ Aborted — add SSH key first!"
    cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
    exit 1
fi

systemctl restart sshd
echo "✅ SSH hardened — port $SSH_PORT · root login disabled · password auth disabled"

# ═══════════════════════════════
# STEP 5 — Firewall (UFW)
# ═══════════════════════════════
echo "🔥 Step 5: Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow $SSH_PORT/tcp comment 'SSH custom port'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8080/tcp comment 'Averion dashboard'
ufw --force enable
echo "✅ UFW firewall configured"

# ═══════════════════════════════
# STEP 6 — Fail2ban
# ═══════════════════════════════
echo "🛡️ Step 6: Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

cat > /etc/fail2ban/jail.local << F2B
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
destemail = root@localhost
action = %(action_mw)s

[sshd]
enabled = true
port = $SSH_PORT
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true

[nginx-botsearch]
enabled = true
F2B

systemctl restart fail2ban
echo "✅ Fail2ban configured"

# ═══════════════════════════════
# STEP 7 — Clock Sync
# ═══════════════════════════════
echo "🕐 Step 7: Setting up clock sync..."
systemctl enable chrony
systemctl start chrony
chronyc makestep
echo "✅ Chrony NTP sync active"

# ═══════════════════════════════
# STEP 8 — PostgreSQL Setup
# ═══════════════════════════════
echo "🗄️ Step 8: Setting up PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5
until pg_isready -U averion -h localhost; do
    echo "PostgreSQL not ready yet · waiting..."
    sleep 3
done
echo "✅ PostgreSQL is ready"
sudo -u postgres psql -c "CREATE USER $AVERION_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User exists"
sudo -u postgres psql -c "CREATE DATABASE averion OWNER $AVERION_USER;" 2>/dev/null || echo "DB exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE averion TO $AVERION_USER;"

# Secure PostgreSQL
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
# Allow password authentication from localhost
PG_VERSION=$(ls /etc/postgresql/)
echo "host    averion         averion         127.0.0.1/32            scram-sha-256" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf
echo "host    averion         averion         ::1/128                 scram-sha-256" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf
systemctl restart postgresql
echo "✅ PostgreSQL configured · localhost only · password auth enabled"

# ═══════════════════════════════
# STEP 9 — Redis Setup
# ═══════════════════════════════
echo "📮 Step 9: Setting up Redis..."
# Bind Redis to localhost only
sed -i 's/^bind 127.0.0.1 -::1/bind 127.0.0.1/' /etc/redis/redis.conf
REDIS_PASS=$(openssl rand -hex 16)
sed -i "s/^# requirepass foobared/requirepass $REDIS_PASS/" /etc/redis/redis.conf
echo "REDIS_PASSWORD=$REDIS_PASS" >> /tmp/averion_setup_vars
systemctl enable redis-server
systemctl start redis-server
echo "✅ Redis running · localhost only"

# ═══════════════════════════════
# STEP 10 — Clone Repository
# ═══════════════════════════════
echo "📥 Step 10: Cloning repository..."
cd /home/$AVERION_USER
sudo -u $AVERION_USER git clone https://github.com/baderbalubaid/Averion.git
echo "✅ Repository cloned"

# ═══════════════════════════════
# STEP 11 — Python Dependencies
# ═══════════════════════════════
echo "🐍 Step 11: Installing Python packages..."
pip install -r /home/$AVERION_USER/Averion/requirements.txt --break-system-packages
echo "✅ Python packages installed"

# ═══════════════════════════════
# STEP 12 — Database Schema
# ═══════════════════════════════
echo "🗄️ Step 12: Creating database tables..."
sudo -u $AVERION_USER psql -d averion -h localhost < /home/$AVERION_USER/Averion/setup/schema.sql
echo "✅ Database tables created"

# ═══════════════════════════════
# STEP 13 — PM2 Setup (as averion user)
# ═══════════════════════════════
echo "⚙️ Step 13: Setting up PM2..."
npm install -g pm2
sudo -u $AVERION_USER pm2 start /home/$AVERION_USER/Averion/main.py \
    --name averion \
    --interpreter python3
# PM2 startup — correct approach
env PATH=$PATH:/usr/bin pm2 startup systemd -u $AVERION_USER --hp /home/$AVERION_USER
su - $AVERION_USER -c 'pm2 save'
echo "✅ PM2 configured as $AVERION_USER user"

# ═══════════════════════════════
# STEP 14 — Cron Jobs
# ═══════════════════════════════
echo "⏰ Step 14: Installing cron jobs..."
(crontab -u $AVERION_USER -l 2>/dev/null; echo "0 * * * * /home/$AVERION_USER/Averion/automation/health_check.sh >> /var/log/averion/health.log 2>&1") | crontab -u $AVERION_USER -
(crontab -u $AVERION_USER -l 2>/dev/null; echo "0 3 * * * /home/$AVERION_USER/Averion/automation/daily_cron.sh >> /var/log/averion_daily.log 2>&1") | crontab -u $AVERION_USER -
(crontab -u $AVERION_USER -l 2>/dev/null; echo "30 4 * * 0 /home/$AVERION_USER/Averion/automation/weekly_cron.sh >> /var/log/averion_weekly.log 2>&1") | crontab -u $AVERION_USER -
echo "✅ Cron jobs installed for $AVERION_USER"

# ═══════════════════════════════
# STEP 15 — Backups Folder
# ═══════════════════════════════
echo "💾 Step 15: Creating backup folder..."
mkdir -p /home/$AVERION_USER/backups
chown $AVERION_USER:$AVERION_USER /home/$AVERION_USER/backups
chmod 700 /home/$AVERION_USER/backups
echo "✅ Backup folder ready"

# ═══════════════════════════════
# STEP 16 — File Permissions
# ═══════════════════════════════
echo "🔐 Step 16: Setting file permissions..."
chown -R $AVERION_USER:$AVERION_USER /home/$AVERION_USER/Averion
chmod 600 /home/$AVERION_USER/Averion/.env 2>/dev/null || true
chmod 700 /home/$AVERION_USER/Averion/automation/*.sh 2>/dev/null || true
echo "✅ File permissions set"

# ═══════════════════════════════
# STEP 17 — Nginx Basic Config
# ═══════════════════════════════
echo "🌐 Step 17: Configuring Nginx..."
cat > /etc/nginx/conf.d/security.conf << NGINX
# Security headers
add_header X-Frame-Options SAMEORIGIN;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
server_tokens off;
NGINX

systemctl enable nginx
systemctl start nginx
echo "✅ Nginx configured with security headers"

# ═══════════════════════════════
# DONE
# ═══════════════════════════════
echo ""
echo "🎉 Day 1 Setup Complete!"
echo ""
echo "Security summary:"
echo "✅ Root login disabled"
echo "✅ SSH password auth disabled"
echo "✅ SSH on port $SSH_PORT"
echo "✅ UFW firewall active"
echo "✅ Fail2ban active"
echo "✅ PostgreSQL localhost only"
echo "✅ Redis localhost only"
echo "✅ Running as $AVERION_USER (not root)"
echo "✅ Auto security updates enabled"
echo ""
echo "Next steps:"
echo "1. cp /home/$AVERION_USER/Averion/setup/env.example /home/$AVERION_USER/Averion/.env"
echo "2. nano /home/$AVERION_USER/Averion/.env"
echo "3. python3 /home/$AVERION_USER/Averion/setup/init_db.py"
echo "4. pm2 restart averion"
echo "5. Continue with Day 2 (domain + HTTPS)"
echo ""
echo "⚠️  New SSH connection: ssh -p $SSH_PORT $AVERION_USER@YOUR_IP"
#!/bin/bash
# Averion — Hetzner Day 2 Setup Script
# Run after Day 1 is complete
# Requirements: domain DNS already pointing to server IP
# Run as root: bash hetzner_day2.sh

set -e
echo "🚀 Starting Averion Day 2 Setup..."

# ═══════════════════════════════
# VARIABLES — EDIT THESE FIRST
# ═══════════════════════════════
DOMAIN="averionbot.com"
EMAIL="your-email@gmail.com"

# ═══════════════════════════════
# STEP 1 — Nginx Configuration
# ═══════════════════════════════
echo "🌐 Step 1: Configuring Nginx..."
cat > /etc/nginx/sites-available/averion << NGINX
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/averion /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
echo "✅ Nginx configured"

# ═══════════════════════════════
# STEP 2 — HTTPS Certificate
# ═══════════════════════════════
echo "🔐 Step 2: Getting HTTPS certificate..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
echo "✅ HTTPS certificate installed"

# ═══════════════════════════════
# STEP 3 — Auto-renew Certificate
# ═══════════════════════════════
echo "🔄 Step 3: Setting up auto-renew..."
(crontab -l 2>/dev/null; echo "0 12 * * * certbot renew --quiet") | crontab -
echo "✅ Certificate auto-renew configured"

# ═══════════════════════════════
# STEP 4 — GitHub Actions Deploy Key
# ═══════════════════════════════
echo "🔑 Step 4: Setting up GitHub Actions..."
ssh-keygen -t ed25519 -C "averion-deploy" -f /root/.ssh/averion_deploy -N ""
echo ""
echo "Add this PUBLIC key to GitHub repo Settings → Deploy Keys:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat /root/.ssh/averion_deploy.pub
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Add this PRIVATE key to GitHub repo Settings → Secrets → HETZNER_SSH_KEY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat /root/.ssh/averion_deploy
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ═══════════════════════════════
# STEP 5 — Test Live Order
# ═══════════════════════════════
echo ""
echo "🧪 Step 5: Ready for live order test"
echo "To test live trading:"
echo "1. Edit .env: nano /home/averion/Averion/.env"
echo "2. Set PAPER_MODE=false"
echo "3. Restart: pm2 restart averion"
echo "4. Open dashboard and verify red LIVE banner"
echo "5. Watch for first \$1 test order on MEXC"
echo "6. Set PAPER_MODE=true after test"
echo "7. Restart: pm2 restart averion"

# ═══════════════════════════════
# DONE
# ═══════════════════════════════
echo ""
echo "🎉 Day 2 Setup Complete!"
echo ""
echo "Your dashboard: https://$DOMAIN/dashboard"
echo "Admin panel: https://$DOMAIN/\$ADMIN_PATH"
echo ""
echo "Next steps:"
echo "1. Add GitHub deploy keys (shown above)"
echo "2. Setup UptimeRobot monitoring"
echo "3. Test live \$1 order on MEXC"
echo "4. Start 107 paper research bots"
# Averion — Hetzner Day 1 Checklist
> Follow in exact order. Check each item before moving to next.
> All commands in hetzner_day1.sh — run that first!

---

## BEFORE YOU START
- [ ] Hetzner ID verification complete
- [ ] Server IP address noted
- [ ] GitHub token ready (in Replit .env)
- [ ] Telegram bot created (@BotFather)
- [ ] Telegram admin chat ID noted
- [ ] NOWPayments account created
- [ ] TRC20 wallet address ready

---

## PHASE 1 — Server Access (5 min)
- [ ] SSH into server: ssh root@YOUR_IP
- [ ] Note server IP address
- [ ] Add your SSH public key to server before running script!
- [ ] Run Day 1 script (asks to confirm SSH key added)
- [ ] After setup: ssh -p 2847 averion@YOUR_IP

## PHASE 2 — Run Day 1 Script (15 min)
- [ ] Clone repo: git clone https://github.com/baderbalubaid/Averion.git
- [ ] Run script: bash Averion/setup/hetzner_day1.sh
- [ ] Confirm: "Day 1 Setup Complete!" message shown
- [ ] Verify PostgreSQL running: systemctl status postgresql
- [ ] Verify Redis running: systemctl status redis-server
- [ ] Verify PM2 running: pm2 status

## PHASE 3 — Environment Setup (10 min)
- [ ] Copy env: cp /home/averion/Averion/setup/env.example /home/averion/Averion/.env
- [ ] Generate Fernet key:
      python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
- [ ] Edit .env: nano /home/averion/Averion/.env
- [ ] Fill in: DB_PASSWORD (strong password)
- [ ] Fill in: ADMIN_PATH (random string e.g. ops-x7k2m)
- [ ] Fill in: ADMIN_PASSWORD
- [ ] Fill in: OWNER_WALLET_TRC20
- [ ] Fill in: TELEGRAM_BOT_TOKEN
- [ ] Fill in: TELEGRAM_ADMIN_CHAT_ID
- [ ] Fill in: FERNET_KEY (from step above)
- [ ] Fill in: GITHUB_TOKEN
- [ ] Confirm PAPER_MODE=true
- [ ] Save and exit: Ctrl+X → Y → Enter

## PHASE 4 — Database Setup (5 min)
- [ ] Run schema: psql -U averion -d averion -h localhost < /home/averion/Averion/setup/schema.sql
- [ ] Initialize DB: python3 /home/averion/Averion/setup/init_db.py
- [ ] Should see: all 17 tables ✅
- [ ] Admin user created ✅

## PHASE 5 — Bot Startup (5 min)
- [ ] Restart bot with .env: pm2 restart averion
- [ ] Check logs: pm2 logs averion --lines 20
- [ ] Verify no errors in logs
- [ ] Test dashboard: curl http://localhost:8080/status
- [ ] Should return: running + BTC price

## PHASE 6 — Cron Jobs (5 min)
- [ ] Verify cron installed: crontab -l
- [ ] Should see 3 cron jobs:
      * Health check every hour
      * Daily cron at 3am
      * Weekly cron Sunday 4:30am
- [ ] Make scripts executable:
      chmod +x /home/averion/Averion/automation/*.sh

## PHASE 7 — Security (5 min)
- [ ] Verify firewall: ufw status
- [ ] Should show: 22 · 80 · 443 · 8080 ALLOW
- [ ] Verify fail2ban: systemctl status fail2ban
- [ ] Verify chrony: chronyc tracking

## PHASE 8 — GitHub Actions (5 min)
- [ ] Go to: github.com/baderbalubaid/Averion/settings/secrets/actions
- [ ] Add secret: HETZNER_IP = your server IP
- [ ] Add secret: HETZNER_SSH_KEY = your SSH private key
- [ ] Test: make small change → git push → verify auto-deploy

## PHASE 9 — Monitoring (5 min)
- [ ] Create UptimeRobot account: uptimerobot.com
- [ ] Add monitor:
      Type: HTTP(S)
      URL: http://YOUR_IP:8080/status
      Interval: 5 minutes
      Alert: Telegram + Email
- [ ] Verify monitor shows green

## PHASE 10 — Final Verification (5 min)
- [ ] Open dashboard: http://YOUR_IP:8080/dashboard
- [ ] Verify BTC price showing
- [ ] Verify all tabs working
- [ ] Verify paper mode active (PAPER badge visible)
- [ ] Send test Telegram message manually
- [ ] Check PM2: pm2 status → averion = online

---

## DAY 1 COMPLETE ✅
Total time: ~55 minutes

Next: Day 2 Checklist (domain + HTTPS + live test)

---

## DAY 2 CHECKLIST

## PHASE 11 — Domain (30 min wait)
- [ ] Buy averionbot.com domain
- [ ] Point A record to Hetzner IP
- [ ] Wait for DNS propagation (check: dig averionbot.com)

## PHASE 12 — Run Day 2 Script (10 min)
- [ ] Edit domain: nano /home/averion/Averion/setup/hetzner_day2.sh
- [ ] Change DOMAIN="averionbot.com"
- [ ] Change EMAIL="your@email.com"
- [ ] Run: bash /home/averion/Averion/setup/hetzner_day2.sh
- [ ] Verify HTTPS: https://averionbot.com/dashboard

## PHASE 13 — Live Order Test (10 min)
- [ ] Edit .env: PAPER_MODE=false
- [ ] Restart: pm2 restart averion
- [ ] Verify red LIVE banner in dashboard
- [ ] Wait for first $1 order on MEXC
- [ ] Confirm order on MEXC exchange website
- [ ] Set PAPER_MODE=true
- [ ] Restart: pm2 restart averion
- [ ] Verify PAPER badge back

## PHASE 14 — Research Bots (30 min)
- [ ] Set up 107 paper research bots
- [ ] Start with 10 trades per bot limit
- [ ] Monitor loop time: pm2 logs averion
- [ ] Verify all bots running in dashboard

---

## DAY 2 COMPLETE ✅
Platform is live! 6 month research period begins.

---

## IMPORTANT NOTES — Lessons Learned

### Python Packages
- Always use: pip install -r requirements.txt --break-system-packages
- Never use pip3 on Hetzner — use pip only
- requirements.txt has exact pinned versions — never change without testing
- If asked "Install Replit tools?" → type n (Hetzner only question)
- Do NOT run pip install without --break-system-packages on Ubuntu 24.04

### File Paths
- Never hardcode /home/user/ — use os.path.expanduser('~/') or os.getcwd()
- Replit path = /home/runner/workspace/
- Hetzner path = /home/averion/Averion/
- Always use relative paths in scripts when possible

### Git Push
- Always use: source .env first to load GITHUB_TOKEN
- Push command: git push https://baderbalubaid:$GITHUB_TOKEN@github.com/baderbalubaid/Averion.git main
- If push rejected for secrets: go to GitHub security URL and allow
- If authentication failed: token may be expired — generate new one

### Database
- Always run schema.sql BEFORE init_db.py
- PostgreSQL user = averion · database = averion
- Connection: psql -U averion -d averion -h localhost
- If connection refused: systemctl start postgresql

### Excel Reports
- Generated daily at 4am automatically
- Saved to: /home/averion/Averion/reports/
- Download via SCP: scp root@IP:/home/averion/Averion/reports/latest.xlsx .
- Open in Excel or Google Sheets
- Never rename columns — AI workflows depend on stable names
# Averion Environment Variables
# Copy this file to .env and fill in your values
# Command: cp setup/env.example .env

# ═══════════════════════════════
# CORE SETTINGS
# ═══════════════════════════════
PAPER_MODE=true
SECRET_KEY=generate-random-string-here-min-32-chars

# ═══════════════════════════════
# DATABASE
# ═══════════════════════════════
DB_HOST=localhost
DB_PORT=5432
DB_NAME=averion
DB_USER=averion
DB_PASSWORD=your-strong-password-here

# ═══════════════════════════════
# REDIS
# ═══════════════════════════════
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password-here

# ═══════════════════════════════
# ADMIN
# ═══════════════════════════════
ADMIN_PATH=ops-CHANGEME
ADMIN_PASSWORD=your-admin-password-here
ADMIN_EMAIL=admin@averionbot.com

# ═══════════════════════════════
# ENCRYPTION
# ═══════════════════════════════
# Generate with: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY=generate-with-python-cryptography

# ═══════════════════════════════
# OWNER WALLET
# ═══════════════════════════════
OWNER_WALLET_TRC20=your-trc20-address
OWNER_WALLET_BEP20=your-bep20-address
TRANSFER_THRESHOLD=10

# ═══════════════════════════════
# TELEGRAM
# ═══════════════════════════════
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_ADMIN_CHAT_ID=your-admin-chat-id

# ═══════════════════════════════
# COINMARKETCAP
# ═══════════════════════════════
CMC_API_KEY=your-cmc-api-key

# ═══════════════════════════════
# EMAIL
# ═══════════════════════════════
# Get free API key at resend.com (3,000/month free)
RESEND_API_KEY=your-resend-api-key
SENDER_EMAIL=noreply@averionbot.com

# ═══════════════════════════════
# NOWPAYMENTS (Phase 7)
# ═══════════════════════════════
NOWPAYMENTS_API_KEY=your-api-key
NOWPAYMENTS_IPN_SECRET=your-ipn-secret

# ═══════════════════════════════
# GITHUB (for auto-deploy)
# ═══════════════════════════════
GITHUB_TOKEN=your-github-token

# ═══════════════════════════════
# SERVER
# ═══════════════════════════════
PORT=8080
HOST=0.0.0.0
import psycopg2
import os
import hashlib
import secrets
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

def hash_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"

def main():
    print("🚀 Initializing Averion Database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ═══════════════════════════
    # Create Admin User
    # ═══════════════════════════
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@averionbot.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123')
    admin_hash = hash_password(admin_password)

    cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
    if cur.fetchone():
        print(f"⏭️  Admin user already exists: {admin_email}")
    else:
        cur.execute("""
            INSERT INTO users (
                email, password_hash, is_admin,
                is_zero_fee, created_at
            ) VALUES (%s, %s, TRUE, TRUE, %s)
        """, (admin_email, admin_hash, datetime.utcnow()))
        print(f"✅ Admin user created: {admin_email}")

    # ═══════════════════════════
    # Create Owner Balance Record
    # ═══════════════════════════
    cur.execute("SELECT id FROM owner_balance LIMIT 1")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO owner_balance
            (accumulated_fees_usdt, total_transferred)
            VALUES (0, 0)
        """)
        print("✅ Owner balance record created")
    else:
        print("⏭️  Owner balance already exists")

    # ═══════════════════════════
    # Verify All Tables Exist
    # ═══════════════════════════
    tables = [
        'users', 'exchanges', 'virtual_wallets', 'bots',
        'positions', 'trades', 'standby_orders',
        'reserve_wallets', 'reserve_deposits', 'fee_debt',
        'balance_history', 'coin_history', 'ohlcv_hourly',
        'owner_balance', 'referrals', 'wallet_bot_assignments',
        'wallet_transactions'
    ]

    print("\n📋 Verifying tables:")
    all_good = True
    for table in tables:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """, (table,))
        exists = cur.fetchone()[0]
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
        if not exists:
            all_good = False

    conn.commit()
    conn.close()

    print()
    if all_good:
        print("🎉 Database initialized successfully!")
        print(f"   Admin: {admin_email}")
        print(f"   Password: {admin_password}")
        print("   ⚠️  Change password after first login!")
    else:
        print("❌ Some tables missing — run schema.sql first:")
        print("   psql -U averion -d averion -h localhost < setup/schema.sql")

if __name__ == '__main__':
    main()
import os
import time
import psycopg2
import redis
import ccxt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════
# CONFIGURATION
# ═══════════════════════════════
PAPER_MODE = os.getenv('PAPER_MODE', 'true').lower() == 'true'
MAX_COINS = os.getenv('MAX_COINS')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# ═══════════════════════════════
# STARTUP ASSERTIONS
# ═══════════════════════════════
def check_assertions():
    if MAX_COINS and not PAPER_MODE:
        raise Exception(
            "CRITICAL: Remove MAX_COINS before going live! "
            "MAX_COINS is for Replit only."
        )
    print(f"✅ Mode: {'PAPER' if PAPER_MODE else 'LIVE'}")
    print(f"✅ Assertions passed")

# ═══════════════════════════════
# WAIT FOR POSTGRESQL
# ═══════════════════════════════
def wait_for_postgresql():
    print("⏳ Waiting for PostgreSQL...")
    attempts = 0
    max_attempts = 12  # 60 seconds total
    while attempts < max_attempts:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("✅ PostgreSQL ready")
            return True
        except Exception as e:
            attempts += 1
            print(f"PostgreSQL not ready ({attempts}/{max_attempts}): {e}")
            time.sleep(5)
    raise Exception("❌ PostgreSQL not available after 60 seconds · exiting")

# ═══════════════════════════════
# WAIT FOR REDIS
# ═══════════════════════════════
def wait_for_redis():
    print("⏳ Waiting for Redis...")
    attempts = 0
    max_attempts = 10  # 30 seconds total
    while attempts < max_attempts:
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            r.ping()
            print("✅ Redis ready")
            return r
        except Exception as e:
            attempts += 1
            print(f"Redis not ready ({attempts}/{max_attempts}): {e}")
            time.sleep(3)
    raise Exception("❌ Redis not available after 30 seconds · exiting")

# ═══════════════════════════════
# UNCONFIRMED ORDER RECONCILIATION
# ═══════════════════════════════
def reconcile_orders():
    print("🔄 Running startup reconciliation...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Get all active exchanges
        cur.execute("""
            SELECT id, exchange, api_key_enc, secret_enc, passphrase_enc
            FROM exchanges
            WHERE active = TRUE AND paused_at IS NULL
        """)
        exchanges = cur.fetchall()

        for exc in exchanges:
            exc_id, exc_name, api_key, secret, passphrase = exc
            try:
                # Initialize CCXT exchange
                exchange_class = getattr(ccxt, exc_name)
                config = {
                    'apiKey': api_key,
                    'secret': secret
                }
                if passphrase:
                    config['password'] = passphrase

                exchange = exchange_class(config)

                # Fetch last 100 orders
                orders = exchange.fetch_orders(limit=100)

                for order in orders:
                    order_id = order.get('id')
                    if not order_id:
                        continue

                    # Check if order exists in DB
                    cur.execute("""
                        SELECT id FROM trades
                        WHERE exchange_order_id = %s
                    """, (order_id,))

                    if not cur.fetchone():
                        # Order on exchange but not in DB
                        print(f"⚠️ Missing order found: {order_id} on {exc_name}")
                        cur.execute("""
                            INSERT INTO trades (
                                exchange_id, coin, side, price,
                                quantity, usdt_amount, order_type,
                                exchange_order_id, timestamp, is_paper
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE)
                        """, (
                            exc_id,
                            order.get('symbol', '').replace('/USDT', ''),
                            order.get('side'),
                            order.get('price') or 0,
                            order.get('filled') or 0,
                            order.get('cost') or 0,
                            order.get('type'),
                            order_id,
                            datetime.utcnow()
                        ))
                        print(f"✅ Reconciled: {order_id}")

                conn.commit()
                print(f"✅ Reconciliation complete for {exc_name}")

            except Exception as e:
                print(f"⚠️ Reconciliation skipped for {exc_name}: {e}")
                continue

        conn.close()
        print("✅ Startup reconciliation complete")

    except Exception as e:
        print(f"⚠️ Reconciliation error: {e} · continuing anyway")

# ═══════════════════════════════
# SEND TELEGRAM
# ═══════════════════════════════
def send_telegram(msg):
    try:
        import requests
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': ADMIN_CHAT, 'text': msg},
            timeout=10
        )
    except:
        pass

# ═══════════════════════════════
# MAIN BOT LOOP
# ═══════════════════════════════
def bot_loop(redis_client):
    print("🚀 Bot loop starting...")
    tg.admin_bot_started(PAPER_MODE)

    cycle = 0
    while True:
        try:
            cycle += 1
            start = time.time()

            from bot_loop import run_cycle
            run_cycle(redis_client)

            elapsed = time.time() - start
            print(f"Cycle {cycle} complete in {elapsed:.2f}s")

            # Store loop health in Redis
            redis_client.setex('bot:last_cycle', 120, str(datetime.utcnow()))
            redis_client.setex('bot:cycle_time', 120, str(round(elapsed, 2)))
            redis_client.setex('bot:status', 120, 'running')

            # Sleep remainder of 60 seconds
            sleep_time = max(0, 60 - elapsed)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("🛑 Bot stopped manually")
            tg.admin_bot_stopped("manual")
            break
        except Exception as e:
            print(f"❌ Loop error: {e}")
            redis_client.setex('bot:status', 120, f'error: {e}')
            time.sleep(10)

# ═══════════════════════════════
# STARTUP SEQUENCE
# ═══════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("AVERION — Adaptive DCA Trading Bot")
    print(f"Starting: {datetime.utcnow()}")
    print("=" * 50)

    try:
        # Step 1: Assertions
        check_assertions()

        # Step 2: Wait for PostgreSQL
        wait_for_postgresql()

        # Step 3: Wait for Redis
        redis_client = wait_for_redis()

        # Step 4: Reconcile orders
        reconcile_orders()

        # Step 5: Start bot loop
        bot_loop(redis_client)

    except Exception as e:
        print(f"❌ FATAL: {e}")
        tg.admin_error(str(e))
        exit(1)
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════
# CONNECTION POOL
# ═══════════════════════════════
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

_pool = None

def init_pool():
    global _pool
    _pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=10,
        **DB_CONFIG
    )
    print('✅ Database connection pool initialized')

@contextmanager
def get_db():
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        _pool.putconn(conn)

# ═══════════════════════════════
# USERS
# ═══════════════════════════════
def get_user_by_email(email):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, email, password_hash, is_admin,
                   is_zero_fee, is_suspended, free_trial_credit
            FROM users WHERE email = %s
        """, (email,))
        return cur.fetchone()

def get_user_by_id(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, email, is_admin, is_zero_fee,
                   is_suspended, telegram_chat_id,
                   telegram_verified, bot_slots_total,
                   trades_used_this_month, next_billing_date
            FROM users WHERE id = %s
        """, (user_id,))
        return cur.fetchone()

def create_user(email, password_hash, referral_code=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (email, password_hash, referral_code)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (email, password_hash, referral_code))
        return cur.fetchone()[0]

# ═══════════════════════════════
# EXCHANGES
# ═══════════════════════════════
def get_user_exchanges(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, exchange, custom_name, active,
                   paused_at, pause_reason, last_connected_at,
                   ip_whitelist_confirmed, key_expires_at
            FROM exchanges
            WHERE user_id = %s AND active = TRUE
            ORDER BY created_at ASC
        """, (user_id,))
        return cur.fetchall()

def get_exchange_by_id(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, exchange, api_key_enc,
                   secret_enc, passphrase_enc, active,
                   paused_at, pause_reason
            FROM exchanges WHERE id = %s
        """, (exchange_id,))
        return cur.fetchone()

def add_exchange(user_id, exchange, custom_name,
                 api_key_enc, secret_enc, passphrase_enc=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO exchanges
            (user_id, exchange, custom_name, api_key_enc,
             secret_enc, passphrase_enc)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, exchange, custom_name,
              api_key_enc, secret_enc, passphrase_enc))
        return cur.fetchone()[0]

def pause_exchange(exchange_id, reason, pause_type='manual'):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE exchanges
            SET paused_at = NOW(), pause_reason = %s,
                pause_type = %s
            WHERE id = %s
        """, (reason, pause_type, exchange_id))

def resume_exchange(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE exchanges
            SET paused_at = NULL, pause_reason = NULL,
                pause_type = NULL, reconnect_attempts = 0,
                last_connected_at = NOW()
            WHERE id = %s
        """, (exchange_id,))

# ═══════════════════════════════
# BOTS
# ═══════════════════════════════
def get_user_bots(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.name, b.method, b.direction,
                   b.trading_on, b.dca_on, b.is_paper,
                   b.status, b.expires_at, b.auto_renew,
                   b.base_coin, b.trades_per_bot,
                   b.trades_per_coin, b.gate_dca_enabled,
                   b.gate_timer_enabled, b.gate_timer_hours,
                   b.order_entry_type, b.order_dca_type,
                   e.exchange, e.custom_name
            FROM bots b
            JOIN exchanges e ON e.id = b.exchange_id
            WHERE b.user_id = %s AND b.status != 'deleted'
            ORDER BY b.created_at ASC
        """, (user_id,))
        return cur.fetchall()

def get_active_bots():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.user_id, b.exchange_id,
                   b.name, b.method, b.direction,
                   b.trading_on, b.dca_on, b.is_paper,
                   b.base_coin, b.dca_percent,
                   b.spacing_multiplier, b.size_multiplier,
                   b.take_profit_percent, b.trailing_percent,
                   b.base_order, b.trades_per_bot,
                   b.trades_per_coin, b.gate_dca_enabled,
                   b.gate_timer_enabled, b.gate_timer_hours,
                   b.order_entry_type, b.order_dca_type,
                   b.dca_checkpoint_level, b.dca_checkpoint_on,
                   e.exchange, e.api_key_enc, e.secret_enc,
                   e.passphrase_enc, e.paused_at
            FROM bots b
            JOIN exchanges e ON e.id = b.exchange_id
            WHERE b.status = 'active'
            AND b.trading_on = TRUE
            AND e.paused_at IS NULL
            ORDER BY b.id ASC
        """)
        return cur.fetchall()

def create_bot(user_id, exchange_id, wallet_id, name,
               method, direction, base_order, dca_percent,
               spacing_multiplier, size_multiplier,
               take_profit_percent, trailing_percent,
               base_coin, is_paper, trades_per_bot,
               trades_per_coin, gate_dca_enabled,
               gate_timer_enabled, gate_timer_hours,
               order_entry_type, order_dca_type):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bots (
                user_id, exchange_id, wallet_id, name,
                method, direction, base_order, dca_percent,
                spacing_multiplier, size_multiplier,
                take_profit_percent, trailing_percent,
                base_coin, is_paper, trades_per_bot,
                trades_per_coin, gate_dca_enabled,
                gate_timer_enabled, gate_timer_hours,
                order_entry_type, order_dca_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            ) RETURNING id
        """, (user_id, exchange_id, wallet_id, name,
              method, direction, base_order, dca_percent,
              spacing_multiplier, size_multiplier,
              take_profit_percent, trailing_percent,
              base_coin, is_paper, trades_per_bot,
              trades_per_coin, gate_dca_enabled,
              gate_timer_enabled, gate_timer_hours,
              order_entry_type, order_dca_type))
        return cur.fetchone()[0]

# ═══════════════════════════════
# POSITIONS
# ═══════════════════════════════
def get_open_positions(exchange_id=None, bot_id=None):
    with get_db() as conn:
        cur = conn.cursor()
        query = """
            SELECT p.id, p.bot_id, p.user_id, p.exchange_id,
                   p.coin, p.direction, p.status,
                   p.avg_cost, p.quantity, p.total_invested,
                   p.dca_count, p.last_buy_price,
                   p.tp_armed, p.peak_price, p.queued,
                   p.standby_amount, p.standby_price,
                   p.category, p.is_paper, p.base_coin,
                   p.sequence_number, p.is_gate_reference,
                   p.coin_trade_number, p.gate_reference_since,
                   p.checkpoint_reached, p.pending_buyback,
                   p.opened_at
            FROM positions p
            WHERE p.status = 'open'
        """
        params = []
        if exchange_id:
            query += " AND p.exchange_id = %s"
            params.append(exchange_id)
        if bot_id:
            query += " AND p.bot_id = %s"
            params.append(bot_id)
        query += " ORDER BY p.total_invested DESC"
        cur.execute(query, params)
        return cur.fetchall()

def open_position(bot_id, user_id, exchange_id, wallet_id,
                  coin, direction, avg_cost, quantity,
                  total_invested, last_buy_price, category,
                  is_paper, base_coin, sequence_number,
                  coin_trade_number, entry_method=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO positions (
                bot_id, user_id, exchange_id, wallet_id,
                coin, direction, avg_cost, quantity,
                total_invested, last_buy_price, category,
                is_paper, base_coin, sequence_number,
                coin_trade_number, entry_method,
                is_gate_reference, gate_reference_since
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                TRUE, NOW()
            ) RETURNING id
        """, (bot_id, user_id, exchange_id, wallet_id,
              coin, direction, avg_cost, quantity,
              total_invested, last_buy_price, category,
              is_paper, base_coin, sequence_number,
              coin_trade_number, entry_method))
        return cur.fetchone()[0]

def update_position_after_dca(position_id, avg_cost,
                               quantity, total_invested,
                               last_buy_price, dca_count):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                avg_cost = %s,
                quantity = %s,
                total_invested = %s,
                last_buy_price = %s,
                dca_count = %s
            WHERE id = %s
        """, (avg_cost, quantity, total_invested,
              last_buy_price, dca_count, position_id))

def arm_tp(position_id, peak_price):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                tp_armed = TRUE, peak_price = %s
            WHERE id = %s
        """, (peak_price, position_id))

def update_peak_price(position_id, peak_price):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET peak_price = %s
            WHERE id = %s
        """, (peak_price, position_id))

def close_position(position_id, close_reason):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                status = 'closed',
                closed_at = NOW(),
                close_reason = %s,
                is_gate_reference = FALSE
            WHERE id = %s
        """, (close_reason, position_id))

def promote_gate_reference(bot_id, coin):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                is_gate_reference = TRUE,
                gate_reference_since = NOW()
            WHERE id = (
                SELECT id FROM positions
                WHERE bot_id = %s AND coin = %s
                AND status = 'open'
                ORDER BY sequence_number DESC
                LIMIT 1
            )
        """, (bot_id, coin))

# ═══════════════════════════════
# TRADES
# ═══════════════════════════════
def record_trade(position_id, bot_id, user_id,
                 exchange_id, coin, side, price,
                 quantity, usdt_amount, exchange_fee,
                 fee_currency, reason, order_type,
                 exchange_order_id, is_paper, dca_level):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO trades (
                position_id, bot_id, user_id, exchange_id,
                coin, side, price, quantity, usdt_amount,
                exchange_fee, fee_currency, reason,
                order_type, exchange_order_id, is_paper,
                dca_level
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (position_id, bot_id, user_id, exchange_id,
              coin, side, price, quantity, usdt_amount,
              exchange_fee, fee_currency, reason,
              order_type, exchange_order_id, is_paper,
              dca_level))
        return cur.fetchone()[0]

def get_position_trades(position_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, side, price, quantity, usdt_amount,
                   exchange_fee, reason, order_type,
                   dca_level, timestamp
            FROM trades
            WHERE position_id = %s
            ORDER BY timestamp ASC
        """, (position_id,))
        return cur.fetchall()

# ═══════════════════════════════
# SMART QUEUE
# ═══════════════════════════════
def get_queue_candidates(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.coin, p.total_invested,
                   p.last_buy_price, p.avg_cost,
                   p.dca_count, p.category,
                   p.bot_id, p.user_id,
                   b.dca_percent, b.spacing_multiplier,
                   b.size_multiplier, b.base_order,
                   b.dca_on, b.dca_checkpoint_level,
                   b.dca_checkpoint_on
            FROM positions p
            JOIN bots b ON b.id = p.bot_id
            WHERE p.exchange_id = %s
            AND p.status = 'open'
            AND p.queued = FALSE
            AND b.dca_on = TRUE
            AND b.trading_on = TRUE
            ORDER BY p.total_invested DESC
        """, (exchange_id,))
        return cur.fetchall()

def set_position_queued(position_id, queued=True):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET queued = %s
            WHERE id = %s
        """, (queued, position_id))

# ═══════════════════════════════
# ATTENTION LOG
# ═══════════════════════════════
def add_attention_log(user_id, severity, item_type,
                      message, bot_id=None, position_id=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO attention_log
            (user_id, bot_id, position_id, severity,
             item_type, message)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, bot_id, position_id, severity,
              item_type, message))
        return cur.fetchone()[0]

def resolve_attention_log(log_id, action_taken):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE attention_log SET
                resolved = TRUE,
                resolved_at = NOW(),
                action_taken = %s
            WHERE id = %s
        """, (action_taken, log_id))

def get_user_attention_logs(user_id, resolved=False):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, severity, item_type, message,
                   bot_id, position_id, created_at
            FROM attention_log
            WHERE user_id = %s AND resolved = %s
            ORDER BY
                CASE severity
                    WHEN 'red' THEN 1
                    WHEN 'yellow' THEN 2
                    WHEN 'green' THEN 3
                END,
                created_at DESC
        """, (user_id, resolved))
        return cur.fetchall()

# ═══════════════════════════════
# RESERVE WALLET
# ═══════════════════════════════
def get_reserve_wallet(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, balance_usdt, total_deposited,
                   total_deducted
            FROM reserve_wallets
            WHERE user_id = %s
        """, (user_id,))
        return cur.fetchone()

def deduct_performance_fee(user_id, position_id,
                            fee_amount, trade_profit):
    with get_db() as conn:
        cur = conn.cursor()
        # Check balance
        cur.execute("""
            SELECT balance_usdt FROM reserve_wallets
            WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
        balance = float(row[0]) if row else 0

        if balance >= fee_amount:
            # Deduct from reserve
            cur.execute("""
                UPDATE reserve_wallets SET
                    balance_usdt = balance_usdt - %s,
                    total_deducted = total_deducted + %s,
                    last_updated = NOW()
                WHERE user_id = %s
            """, (fee_amount, fee_amount, user_id))
            paid = True
        else:
            # Record as debt
            paid = False

        # Record in fee_debt
        cur.execute("""
            INSERT INTO fee_debt
            (user_id, position_id, amount_usdt, trade_profit)
            VALUES (%s, %s, %s, %s)
        """, (user_id, position_id, fee_amount, trade_profit))

        return paid

# ═══════════════════════════════
# COIN CLASSIFICATION
# ═══════════════════════════════
def get_coin_category(coin):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT category, recorded_cap
            FROM coin_history
            WHERE coin = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (coin,))
        row = cur.fetchone()
        return row[0] if row else 'micro'

def get_all_coin_categories():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (coin) coin, category,
                   recorded_cap, recorded_at
            FROM coin_history
            ORDER BY coin, recorded_at DESC
        """)
        return {row[0]: row[1] for row in cur.fetchall()}

# ═══════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════
def record_system_health(cpu, ram, disk, redis_mb,
                          pg_conn, cycle_time,
                          active_bots, open_positions):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO system_health (
                cpu_percent, ram_percent, disk_percent,
                redis_mb, pg_connections, bot_cycle_time,
                active_bots, open_positions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (cpu, ram, disk, redis_mb, pg_conn,
              cycle_time, active_bots, open_positions))
        # Delete older than 30 days
        cur.execute("""
            DELETE FROM system_health
            WHERE recorded_at < NOW() - INTERVAL '30 days'
        """)

def record_performance_timing(step, duration,
                               records, status, error=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO performance_timing (
                step, duration_seconds, records_processed,
                status, error_message, started_at
            ) VALUES (%s, %s, %s, %s, %s,
                      NOW() - INTERVAL '%s seconds')
        """, (step, duration, records, status, error, duration))
        # Delete older than 30 days
        cur.execute("""
            DELETE FROM performance_timing
            WHERE completed_at < NOW() - INTERVAL '30 days'
        """)

def record_bot_event(bot_id, user_id, event_type,
                     coin=None, exchange=None,
                     error_message=None, stack_trace=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bot_events (
                bot_id, user_id, event_type, coin,
                exchange, error_message, stack_trace
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (bot_id, user_id, event_type, coin,
              exchange, error_message, stack_trace))
        # Delete older than 30 days
        cur.execute("""
            DELETE FROM bot_events
            WHERE recorded_at < NOW() - INTERVAL '30 days'
        """)

if __name__ == '__main__':
    init_pool()
    print('✅ Database module ready')
    print('✅ All functions available')

# ═══════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════
def queue_notification(user_id, chat_id, message, message_type):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notification_queue
            (user_id, chat_id, message, message_type)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, chat_id, message, message_type))
        return cur.fetchone()[0]

def get_pending_notifications():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, chat_id, message, message_type
            FROM notification_queue
            WHERE sent = FALSE
            ORDER BY created_at ASC
            LIMIT 50
        """)
        return cur.fetchall()

def mark_notification_sent(notification_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE notification_queue
            SET sent = TRUE, sent_at = NOW()
            WHERE id = %s
        """, (notification_id,))

def increment_notification_retry(notification_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE notification_queue
            SET retry_count = retry_count + 1
            WHERE id = %s
        """, (notification_id,))

# ═══════════════════════════════
# VIRTUAL WALLETS
# ═══════════════════════════════
def get_user_wallets(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT w.id, w.name, w.currency,
                   w.allocation_type, w.allocation_amount,
                   w.current_balance, w.standby_reserved,
                   e.exchange, e.custom_name
            FROM virtual_wallets w
            JOIN exchanges e ON e.id = w.exchange_id
            WHERE w.user_id = %s
            ORDER BY w.created_at ASC
        """, (user_id,))
        return cur.fetchall()

def get_wallet_by_id(wallet_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, exchange_id, name,
                   currency, allocation_type,
                   allocation_amount, current_balance,
                   standby_reserved
            FROM virtual_wallets WHERE id = %s
        """, (wallet_id,))
        return cur.fetchone()

def create_wallet(user_id, exchange_id, name,
                  currency, allocation_type, allocation_amount):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO virtual_wallets
            (user_id, exchange_id, name, currency,
             allocation_type, allocation_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, exchange_id, name, currency,
              allocation_type, allocation_amount))
        return cur.fetchone()[0]

def update_wallet_balance(wallet_id, amount, operation='add'):
    with get_db() as conn:
        cur = conn.cursor()
        if operation == 'add':
            cur.execute("""
                UPDATE virtual_wallets
                SET current_balance = current_balance + %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (amount, wallet_id))
        else:
            cur.execute("""
                UPDATE virtual_wallets
                SET current_balance = current_balance - %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (amount, wallet_id))

def record_wallet_transaction(wallet_id, position_id,
                               tx_type, amount, balance_after):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO wallet_transactions
            (wallet_id, position_id, type, amount, balance_after)
            VALUES (%s, %s, %s, %s, %s)
        """, (wallet_id, position_id, tx_type,
              amount, balance_after))

# ═══════════════════════════════
# BALANCE HISTORY
# ═══════════════════════════════
def record_balance_history(user_id, exchange_id, value_usdt):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO balance_history
            (user_id, exchange_id, value_usdt)
            VALUES (%s, %s, %s)
        """, (user_id, exchange_id, value_usdt))

def get_balance_history(exchange_id, days=30):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT value_usdt, recorded_at
            FROM balance_history
            WHERE exchange_id = %s
            AND recorded_at > NOW() - INTERVAL '%s days'
            ORDER BY recorded_at ASC
        """, (exchange_id, days))
        return cur.fetchall()

# ═══════════════════════════════
# OHLCV
# ═══════════════════════════════
def store_ohlcv(coin, exchange, timestamp,
                open_p, high, low, close, volume):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ohlcv_hourly
            (coin, exchange, timestamp, open, high,
             low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (coin, exchange, timestamp)
            DO NOTHING
        """, (coin, exchange, timestamp,
              open_p, high, low, close, volume))

def get_ohlcv(coin, exchange, limit=100):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, open, high, low, close,
                   volume, atr_14
            FROM ohlcv_hourly
            WHERE coin = %s AND exchange = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (coin, exchange, limit))
        return cur.fetchall()

def update_atr(coin, exchange, atr_14):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE ohlcv_hourly SET atr_14 = %s
            WHERE coin = %s AND exchange = %s
            AND timestamp = (
                SELECT MAX(timestamp) FROM ohlcv_hourly
                WHERE coin = %s AND exchange = %s
            )
        """, (atr_14, coin, exchange, coin, exchange))

def cleanup_old_ohlcv(days=90):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM ohlcv_hourly
            WHERE timestamp < NOW() - INTERVAL '%s days'
        """, (days,))
        return cur.rowcount

# ═══════════════════════════════
# RESEARCH SCORES
# ═══════════════════════════════
def update_research_score(bot_id, method, config_id,
                           total_trades, winning_trades,
                           total_profit, max_drawdown,
                           avg_hold_hours):
    with get_db() as conn:
        cur = conn.cursor()
        losing = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100
                    ) if total_trades > 0 else 0

        cur.execute("""
            INSERT INTO research_scores (
                bot_id, method, bot_config_id,
                total_trades, winning_trades, losing_trades,
                win_rate, total_profit, max_drawdown,
                avg_hold_hours, last_calculated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (bot_id) DO UPDATE SET
                total_trades = EXCLUDED.total_trades,
                winning_trades = EXCLUDED.winning_trades,
                losing_trades = EXCLUDED.losing_trades,
                win_rate = EXCLUDED.win_rate,
                total_profit = EXCLUDED.total_profit,
                max_drawdown = EXCLUDED.max_drawdown,
                avg_hold_hours = EXCLUDED.avg_hold_hours,
                last_calculated = NOW()
        """, (bot_id, method, config_id, total_trades,
              winning_trades, losing, win_rate,
              total_profit, max_drawdown, avg_hold_hours))

def get_research_rankings():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.bot_id, r.method, r.bot_config_id,
                   r.total_trades, r.win_rate,
                   r.total_profit, r.max_drawdown,
                   r.avg_hold_hours, r.promotion_score,
                   r.rank, r.status,
                   b.name as bot_name
            FROM research_scores r
            JOIN bots b ON b.id = r.bot_id
            WHERE r.status = 'active'
            ORDER BY r.promotion_score DESC NULLS LAST
        """)
        return cur.fetchall()

# ═══════════════════════════════
# STANDBY ORDERS
# ═══════════════════════════════
def create_standby_order(position_id, bot_id,
                          wallet_id, standby_amount,
                          target_price, dca_level):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO standby_orders
            (position_id, bot_id, wallet_id,
             standby_amount, target_price, dca_level)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (position_id, bot_id, wallet_id,
              standby_amount, target_price, dca_level))
        return cur.fetchone()[0]

def get_active_standby_orders(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.position_id, s.standby_amount,
                   s.target_price, s.dca_level,
                   p.coin, p.bot_id, p.user_id
            FROM standby_orders s
            JOIN positions p ON p.id = s.position_id
            JOIN bots b ON b.id = p.bot_id
            WHERE s.status = 'active'
            AND b.exchange_id = %s
        """, (exchange_id,))
        return cur.fetchall()

def trigger_standby_order(standby_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE standby_orders
            SET status = 'triggered', triggered_at = NOW()
            WHERE id = %s
        """, (standby_id,))

def cancel_standby_order(standby_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE standby_orders
            SET status = 'cancelled', expired_at = NOW()
            WHERE id = %s
        """, (standby_id,))

# ═══════════════════════════════
# ADMIN
# ═══════════════════════════════
def get_platform_stats():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM users WHERE is_admin=FALSE) as total_users,
                (SELECT COUNT(*) FROM bots WHERE status='active') as active_bots,
                (SELECT COUNT(*) FROM positions WHERE status='open') as open_positions,
                (SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=FALSE) as live_positions,
                (SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=TRUE) as paper_positions,
                (SELECT COALESCE(SUM(balance_usdt),0) FROM reserve_wallets) as total_reserve,
                (SELECT accumulated_fees_usdt FROM owner_balance LIMIT 1) as owner_balance,
                (SELECT COUNT(*) FROM trades WHERE DATE(timestamp)=CURRENT_DATE) as trades_today
        """)
        return cur.fetchone()

def get_all_users_admin():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.email, u.created_at,
                   u.is_suspended, u.telegram_verified,
                   COUNT(DISTINCT b.id) as bot_count,
                   COUNT(DISTINCT p.id) as open_positions,
                   COALESCE(r.balance_usdt, 0) as reserve_balance,
                   COALESCE(SUM(fd.amount_usdt) FILTER
                       (WHERE fd.paid_at IS NULL), 0) as fee_debt
            FROM users u
            LEFT JOIN bots b ON b.user_id = u.id
                AND b.status = 'active'
            LEFT JOIN positions p ON p.user_id = u.id
                AND p.status = 'open'
            LEFT JOIN reserve_wallets r ON r.user_id = u.id
            LEFT JOIN fee_debt fd ON fd.user_id = u.id
            WHERE u.is_admin = FALSE
            GROUP BY u.id, u.email, u.created_at,
                     u.is_suspended, u.telegram_verified,
                     r.balance_usdt
            ORDER BY open_positions DESC
        """)
        return cur.fetchall()

# ═══════════════════════════════
# SECURITY AUDIT LOG
# ═══════════════════════════════
def log_security_event(user_id, event_type, ip_address=None,
                        user_agent=None, details=None):
    import json
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO security_audit_log
            (user_id, event_type, ip_address, user_agent, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, event_type, ip_address, user_agent,
              json.dumps(details) if details else None))

def get_security_logs(user_id=None, limit=100):
    with get_db() as conn:
        cur = conn.cursor()
        if user_id:
            cur.execute("""
                SELECT id, user_id, event_type, ip_address,
                       details, created_at
                FROM security_audit_log
                WHERE user_id = %s
                ORDER BY created_at DESC LIMIT %s
            """, (user_id, limit))
        else:
            cur.execute("""
                SELECT id, user_id, event_type, ip_address,
                       details, created_at
                FROM security_audit_log
                ORDER BY created_at DESC LIMIT %s
            """, (limit,))
        return cur.fetchall()

# ═══════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════
def create_verification_code(user_id):
    import random
    code = str(random.randint(100000, 999999))
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET
                verification_code = %s,
                verification_expires_at = NOW() + INTERVAL '15 minutes'
            WHERE id = %s
        """, (code, user_id))
    return code

def verify_code(user_id, code):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT verification_code, verification_expires_at
            FROM users WHERE id = %s
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            return False
        stored_code, expires_at = row
        if stored_code != code:
            return False
        from datetime import datetime, timezone
        if expires_at < datetime.now(timezone.utc):
            return False
        # Mark as verified
        cur.execute("""
            UPDATE users SET
                last_verified_at = NOW(),
                verification_code = NULL,
                verification_expires_at = NULL
            WHERE id = %s
        """, (user_id,))
        return True
import os
import hashlib
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import uvicorn
import redis
import jwt

import database as db
import auth as auth_module

load_dotenv()

PAPER_MODE = os.getenv('PAPER_MODE', 'true').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
ADMIN_PATH = os.getenv('ADMIN_PATH', 'ops-admin')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# ═══════════════════════════════
# STARTUP
# ═══════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_pool()
    print('✅ API started')
    yield

app = FastAPI(title='Averion API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# ═══════════════════════════════
# REDIS CLIENT
# ═══════════════════════════════
def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# ═══════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════
security = HTTPBearer()

# Password functions handled by auth module





def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY, algorithms=['HS256']
        )
        return payload
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

def require_admin(payload: dict = Depends(verify_token)):
    if not payload.get('is_admin'):
        raise HTTPException(status_code=403, detail='Admin only')
    return payload

# ═══════════════════════════════
# BRUTE FORCE PROTECTION
# ═══════════════════════════════
def check_brute_force(ip: str) -> bool:
    r = get_redis()
    key = f'login_fails:{ip}'
    fails = r.get(key)
    return int(fails) >= 5 if fails else False

def record_login_fail(ip: str):
    r = get_redis()
    key = f'login_fails:{ip}'
    r.incr(key)
    r.expire(key, 1800)  # 30 minutes

def clear_login_fails(ip: str):
    r = get_redis()
    r.delete(f'login_fails:{ip}')

# ═══════════════════════════════
# STATIC FILES
# ═══════════════════════════════
@app.get('/dashboard')
def dashboard():
    return FileResponse('dashboard.html')

@app.get(f'/{ADMIN_PATH}')
def admin_dashboard():
    return FileResponse('admin.html')

@app.get('/')
def homepage():
    return FileResponse('index.html')

@app.get('/login')
def login_page():
    return FileResponse('login.html')

@app.get('/register')
def register_page():
    return FileResponse('register.html')

# ═══════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post('/auth/login')
def login(req: LoginRequest, request: Request):
    ip = request.client.host

    if auth_module.check_brute_force(ip):
        raise HTTPException(status_code=429, detail='Too many failed attempts')

    result, error = auth_module.login(
        req.email, req.password, ip,
        request.headers.get('user-agent')
    )
    if error:
        auth_module.record_login_fail(ip)
        raise HTTPException(status_code=401, detail=error)

    auth_module.clear_login_fails(ip)
    return result

# ═══════════════════════════════
# STATUS
# ═══════════════════════════════
@app.get('/status')
def get_status():
    r = get_redis()
    bot_status = r.get('bot:status') or 'unknown'
    cycle_time = r.get('bot:cycle_time') or '0'
    last_cycle = r.get('bot:last_cycle') or 'never'

    btc_price = 0
    try:
        btc_price = float(r.get('price:BTC/USDT') or 0)
    except:
        pass

    return {
        'running': bot_status == 'running',
        'bot_status': bot_status,
        'cycle_time': cycle_time,
        'last_cycle': last_cycle,
        'btc_price': btc_price,
        'mode': 'paper' if PAPER_MODE else 'live'
    }

# ═══════════════════════════════
# POSITIONS
# ═══════════════════════════════
@app.get('/positions')
def get_positions(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    r = get_redis()

    positions = db.get_open_positions()
    result = []

    for p in positions:
        if p[2] != user_id:  # user_id check
            continue

        coin = p[4]
        current_price = 0
        try:
            current_price = float(
                r.get(f'price:{coin}/USDT') or p[7] or 0
            )
        except:
            current_price = float(p[7] or 0)

        avg_cost = float(p[7] or 0)
        quantity = float(p[8] or 0)
        invested = float(p[9] or 0)

        pnl = (current_price - avg_cost) * quantity
        pnl_pct = ((current_price - avg_cost) / avg_cost * 100
                   ) if avg_cost else 0

        result.append({
            'id': p[0],
            'bot_id': p[1],
            'coin': coin,
            'direction': p[5],
            'status': p[6],
            'avg_cost': avg_cost,
            'quantity': quantity,
            'total_invested': invested,
            'dca_count': p[10],
            'last_buy_price': float(p[11] or 0),
            'tp_armed': p[12],
            'current_price': current_price,
            'pnl': round(pnl, 4),
            'pnl_pct': round(pnl_pct, 2),
            'category': p[17],
            'is_paper': p[18],
            'base_coin': p[19],
            'opened_at': str(p[26])
        })

    return result

@app.get('/positions/{position_id}')
def get_position_detail(position_id: int,
                         payload: dict = Depends(verify_token)):
    trades = db.get_position_trades(position_id)
    return {
        'position_id': position_id,
        'trades': [{
            'id': t[0],
            'side': t[1],
            'price': float(t[2]),
            'quantity': float(t[3]),
            'usdt_amount': float(t[4]),
            'exchange_fee': float(t[5] or 0),
            'reason': t[6],
            'order_type': t[7],
            'dca_level': t[8],
            'timestamp': str(t[9])
        } for t in trades]
    }

@app.post('/positions/{position_id}/close')
def close_position(position_id: int,
                    payload: dict = Depends(verify_token)):
    db.close_position(position_id, 'manual')
    db.add_attention_log(
        payload['user_id'], 'green',
        'manual_close', f'Position {position_id} closed manually',
        position_id=position_id
    )
    return {'message': f'Position {position_id} closed'}

# ═══════════════════════════════
# TRADES / HISTORY
# ═══════════════════════════════
@app.get('/trades')
def get_trades(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id, t.coin, t.side, t.price,
                   t.quantity, t.usdt_amount, t.reason,
                   t.exchange_fee, t.dca_level, t.timestamp
            FROM trades t
            WHERE t.user_id = %s
            ORDER BY t.timestamp DESC LIMIT 100
        """, (user_id,))
        rows = cur.fetchall()
    return [{'id': r[0], 'coin': r[1], 'side': r[2],
              'price': float(r[3]), 'quantity': float(r[4]),
              'usdt_amount': float(r[5]), 'reason': r[6],
              'fee': float(r[7] or 0), 'dca_level': r[8],
              'timestamp': str(r[9])} for r in rows]

@app.get('/history')
def get_history(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.coin, p.direction, p.avg_cost,
                   p.dca_count, p.total_invested,
                   p.opened_at, p.closed_at, p.close_reason,
                   p.category, p.entry_method, p.base_coin,
                   e.exchange
            FROM positions p
            JOIN exchanges e ON e.id = p.exchange_id
            WHERE p.user_id = %s AND p.status = 'closed'
            ORDER BY p.closed_at DESC LIMIT 200
        """, (user_id,))
        rows = cur.fetchall()
    return [{'id': r[0], 'coin': r[1], 'direction': r[2],
              'avg_cost': float(r[3] or 0),
              'dca_count': r[4],
              'total_invested': float(r[5] or 0),
              'opened_at': str(r[6]), 'closed_at': str(r[7]),
              'close_reason': r[8], 'category': r[9],
              'entry_method': r[10], 'base_coin': r[11],
              'exchange': r[12]} for r in rows]

# ═══════════════════════════════
# BOTS
# ═══════════════════════════════
@app.get('/bots')
def get_bots(payload: dict = Depends(verify_token)):
    bots = db.get_user_bots(payload['user_id'])
    return [{'id': b[0], 'name': b[1], 'method': b[2],
              'direction': b[3], 'trading_on': b[4],
              'dca_on': b[5], 'is_paper': b[6],
              'status': b[7], 'expires_at': str(b[8]),
              'auto_renew': b[9], 'base_coin': b[10],
              'trades_per_bot': b[11],
              'trades_per_coin': b[12],
              'gate_dca_enabled': b[13],
              'gate_timer_enabled': b[14],
              'gate_timer_hours': b[15],
              'order_entry_type': b[16],
              'order_dca_type': b[17],
              'exchange': b[18],
              'exchange_name': b[19]} for b in bots]

class BotToggle(BaseModel):
    trading_on: Optional[bool] = None
    dca_on: Optional[bool] = None

@app.post('/bots/{bot_id}/toggle')
def toggle_bot(bot_id: int, toggle: BotToggle,
               payload: dict = Depends(verify_token)):
    with db.get_db() as conn:
        cur = conn.cursor()
        if toggle.trading_on is not None:
            cur.execute("""
                UPDATE bots SET trading_on = %s
                WHERE id = %s AND user_id = %s
            """, (toggle.trading_on, bot_id, payload['user_id']))
        if toggle.dca_on is not None:
            cur.execute("""
                UPDATE bots SET dca_on = %s
                WHERE id = %s AND user_id = %s
            """, (toggle.dca_on, bot_id, payload['user_id']))
    return {'message': 'Bot updated'}

# ═══════════════════════════════
# EXCHANGES
# ═══════════════════════════════
@app.get('/exchanges')
def get_exchanges(payload: dict = Depends(verify_token)):
    exchanges = db.get_user_exchanges(payload['user_id'])
    return [{'id': e[0], 'exchange': e[1],
              'custom_name': e[2], 'active': e[3],
              'paused': e[4] is not None,
              'pause_reason': e[5],
              'last_connected': str(e[6]),
              'ip_confirmed': e[7]} for e in exchanges]

# ═══════════════════════════════
# ATTENTION LOG
# ═══════════════════════════════
@app.get('/attention-log')
def get_attention_log(payload: dict = Depends(verify_token)):
    logs = db.get_user_attention_logs(payload['user_id'])
    return [{'id': l[0], 'severity': l[1],
              'item_type': l[2], 'message': l[3],
              'bot_id': l[4], 'position_id': l[5],
              'created_at': str(l[6])} for l in logs]

@app.post('/attention-log/{log_id}/resolve')
def resolve_log(log_id: int, action: str = 'dismissed',
                payload: dict = Depends(verify_token)):
    db.resolve_attention_log(log_id, action)
    return {'message': 'Resolved'}

# ═══════════════════════════════
# RESERVE WALLET
# ═══════════════════════════════
@app.get('/reserve-wallet')
def get_reserve(payload: dict = Depends(verify_token)):
    wallet = db.get_reserve_wallet(payload['user_id'])
    if not wallet:
        return {'balance': 0, 'total_deposited': 0}
    return {
        'id': wallet[0],
        'balance': float(wallet[1]),
        'total_deposited': float(wallet[2]),
        'total_deducted': float(wallet[3])
    }

# ═══════════════════════════════
# BALANCE HISTORY
# ═══════════════════════════════
@app.get('/balance-history')
def get_balance_history(exchange_id: int = 1, days: int = 30,
                         payload: dict = Depends(verify_token)):
    rows = db.get_balance_history(exchange_id, days)
    return [{'value': float(r[0]), 'date': str(r[1])}
            for r in rows]

# ═══════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════
@app.get('/admin/stats')
def admin_stats(payload: dict = Depends(require_admin)):
    stats = db.get_platform_stats()
    r = get_redis()
    return {
        'total_users': stats[0],
        'active_bots': stats[1],
        'open_positions': stats[2],
        'live_positions': stats[3],
        'paper_positions': stats[4],
        'total_reserve': float(stats[5] or 0),
        'owner_balance': float(stats[6] or 0),
        'trades_today': stats[7],
        'bot_status': r.get('bot:status') or 'unknown',
        'cycle_time': r.get('bot:cycle_time') or '0',
        'last_cycle': r.get('bot:last_cycle') or 'never'
    }

@app.get('/admin/users')
def admin_users(payload: dict = Depends(require_admin)):
    users = db.get_all_users_admin()
    return [{'id': u[0], 'email': u[1],
              'created_at': str(u[2]),
              'suspended': u[3],
              'telegram': u[4],
              'bots': u[5],
              'open_positions': u[6],
              'reserve': float(u[7] or 0),
              'fee_debt': float(u[8] or 0)} for u in users]

@app.post('/admin/bot/restart')
def admin_restart_bot(payload: dict = Depends(require_admin)):
    import subprocess
    subprocess.run(['pm2', 'restart', 'averion'])
    return {'message': 'Bot restarting'}

@app.post('/admin/cron/{step}/run')
def admin_run_cron_step(step: str,
                         payload: dict = Depends(require_admin)):
    import subprocess
    scripts = {
        'infrastructure': 'automation/daily_cron.sh',
        'coingecko': 'automation/fetch_coingecko.py',
        'cmc': 'automation/fetch_cmc.py',
        'classification': 'automation/classify_coins.py',
        'reporting': 'automation/daily_aggregation.py',
        'diagnostics': 'automation/generate_diagnostics.py'
    }
    if step not in scripts:
        raise HTTPException(status_code=404, detail='Unknown step')

    script = scripts[step]
    if script.endswith('.py'):
        subprocess.Popen(['python3', script])
    else:
        subprocess.Popen(['bash', script])

    return {'message': f'Step {step} started'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

# ═══════════════════════════════
# EXCHANGES — ADD / TEST / DELETE
# ═══════════════════════════════
class ExchangeCreate(BaseModel):
   exchange: str
   custom_name: str
   api_key: str
   secret: str
   passphrase: Optional[str] = None
   ip_whitelist_confirmed: bool = False

@app.post('/exchanges')
def add_exchange(req: ExchangeCreate,
                payload: dict = Depends(verify_token)):
   from cryptography.fernet import Fernet
   import base64

   fernet_key = os.getenv('FERNET_KEY')
   if not fernet_key:
       raise HTTPException(status_code=500,
                           detail='Encryption not configured')

   f = Fernet(fernet_key.encode())
   api_key_enc = f.encrypt(req.api_key.encode()).decode()
   secret_enc = f.encrypt(req.secret.encode()).decode()
   passphrase_enc = None
   if req.passphrase:
       passphrase_enc = f.encrypt(req.passphrase.encode()).decode()

   exchange_id = db.add_exchange(
       payload['user_id'], req.exchange, req.custom_name,
       api_key_enc, secret_enc, passphrase_enc
   )

   # Confirm IP whitelist
   if req.ip_whitelist_confirmed:
       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("""
               UPDATE exchanges SET ip_whitelist_confirmed = TRUE
               WHERE id = %s
           """, (exchange_id,))

   return {'message': 'Exchange added', 'exchange_id': exchange_id}

@app.post('/exchanges/{exchange_id}/test')
def test_exchange(exchange_id: int,
                 payload: dict = Depends(verify_token)):
   from cryptography.fernet import Fernet
   import ccxt

   exc = db.get_exchange_by_id(exchange_id)
   if not exc or exc[1] != payload['user_id']:
       raise HTTPException(status_code=404,
                           detail='Exchange not found')

   fernet_key = os.getenv('FERNET_KEY')
   f = Fernet(fernet_key.encode())

   try:
       api_key = f.decrypt(exc[3].encode()).decode()
       secret = f.decrypt(exc[4].encode()).decode()
       passphrase = None
       if exc[5]:
           passphrase = f.decrypt(exc[5].encode()).decode()

       exchange_class = getattr(ccxt, exc[2])
       config = {
           'apiKey': api_key,
           'secret': secret,
           'enableRateLimit': True
       }
       if passphrase:
           config['password'] = passphrase

       exchange = exchange_class(config)
       balance = exchange.fetch_balance()
       usdt = balance.get('USDT', {}).get('free', 0)

       # Update last connected
       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("""
               UPDATE exchanges SET last_connected_at = NOW()
               WHERE id = %s
           """, (exchange_id,))

       return {
           'success': True,
           'balance_usdt': round(float(usdt), 2),
           'message': f'✅ Connected · Balance: ${usdt:.2f} USDT'
       }

   except ccxt.AuthenticationError:
       return {
           'success': False,
           'message': '❌ Invalid API key or secret'
       }
   except ccxt.ExchangeError as e:
       return {
           'success': False,
           'message': f'❌ Exchange error: {str(e)[:100]}'
       }
   except Exception as e:
       return {
           'success': False,
           'message': f'❌ Error: {str(e)[:100]}'
       }

@app.delete('/exchanges/{exchange_id}')
def delete_exchange(exchange_id: int,
                   payload: dict = Depends(verify_token)):
   with db.get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           UPDATE exchanges SET active = FALSE
           WHERE id = %s AND user_id = %s
       """, (exchange_id, payload['user_id']))
   return {'message': 'Exchange removed'}

# ═══════════════════════════════
# BOTS — CREATE / DELETE
# ═══════════════════════════════
class BotCreate(BaseModel):
   exchange_id: int
   wallet_id: int
   name: str
   method: str
   direction: str
   base_order: float = 1.0
   dca_percent: float = 7.0
   spacing_multiplier: float = 1.4
   size_multiplier: float = 1.5
   take_profit_percent: float = 5.0
   trailing_percent: float = 2.0
   base_coin: str = 'USDT'
   is_paper: bool = True
   trades_per_bot: int = 1
   trades_per_coin: int = 1
   gate_dca_enabled: bool = False
   gate_timer_enabled: bool = False
   gate_timer_hours: int = 5
   order_entry_type: str = 'market'
   order_dca_type: str = 'market'

@app.post('/bots')
def create_bot(req: BotCreate,
              payload: dict = Depends(verify_token)):
   bot_id = db.create_bot(
       payload['user_id'], req.exchange_id, req.wallet_id,
       req.name, req.method, req.direction, req.base_order,
       req.dca_percent, req.spacing_multiplier,
       req.size_multiplier, req.take_profit_percent,
       req.trailing_percent, req.base_coin, req.is_paper,
       req.trades_per_bot, req.trades_per_coin,
       req.gate_dca_enabled, req.gate_timer_enabled,
       req.gate_timer_hours, req.order_entry_type,
       req.order_dca_type
   )
   return {'message': 'Bot created', 'bot_id': bot_id}

@app.delete('/bots/{bot_id}')
def delete_bot(bot_id: int,
              payload: dict = Depends(verify_token)):
   with db.get_db() as conn:
       cur = conn.cursor()
       # Check ownership
       cur.execute("""
           SELECT id FROM bots
           WHERE id = %s AND user_id = %s
       """, (bot_id, payload['user_id']))
       if not cur.fetchone():
           raise HTTPException(status_code=404,
                               detail='Bot not found')
       # Soft delete
       cur.execute("""
           UPDATE bots SET status = 'deleted'
           WHERE id = %s
       """, (bot_id,))
   return {'message': f'Bot {bot_id} deleted'}

# ═══════════════════════════════
# VIRTUAL WALLETS
# ═══════════════════════════════
class WalletCreate(BaseModel):
   exchange_id: int
   name: str
   currency: str = 'USDT'
   allocation_type: str = 'fixed'
   allocation_amount: float = 0

@app.get('/wallets')
def get_wallets(payload: dict = Depends(verify_token)):
   wallets = db.get_user_wallets(payload['user_id'])
   return [{'id': w[0], 'name': w[1], 'currency': w[2],
             'allocation_type': w[3],
             'allocation_amount': float(w[4] or 0),
             'current_balance': float(w[5] or 0),
             'standby_reserved': float(w[6] or 0),
             'exchange': w[7],
             'exchange_name': w[8]} for w in wallets]

@app.post('/wallets')
def create_wallet(req: WalletCreate,
                 payload: dict = Depends(verify_token)):
   wallet_id = db.create_wallet(
       payload['user_id'], req.exchange_id, req.name,
       req.currency, req.allocation_type, req.allocation_amount
   )
   return {'message': 'Wallet created', 'wallet_id': wallet_id}

# ═══════════════════════════════
# ADMIN — CRON STATUS
# ═══════════════════════════════
@app.get('/admin/cron-status')
def admin_cron_status(payload: dict = Depends(require_admin)):
   with db.get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           SELECT DISTINCT ON (step)
               step, status, duration_seconds,
               records_processed, error_message,
               completed_at
           FROM performance_timing
           WHERE completed_at > NOW() - INTERVAL '48 hours'
           ORDER BY step, completed_at DESC
       """)
       rows = cur.fetchall()

   steps = {
       'infrastructure': None,
       'coingecko': None,
       'cmc': None,
       'classification': None,
       'reporting': None,
       'cleanup': None
   }

   for r in rows:
       step = r[0]
       if step in steps:
           steps[step] = {
               'step': step,
               'status': r[1],
               'duration': float(r[2] or 0),
               'records': r[3],
               'error': r[4],
               'completed_at': str(r[5])
           }

   return steps

# ═══════════════════════════════
# ADMIN — DIAGNOSTICS
# ═══════════════════════════════
@app.get('/admin/diagnostics')
def admin_diagnostics(payload: dict = Depends(require_admin)):
   try:
       with open('diagnostics/latest.md', 'r') as f:
           content = f.read()
       return {'content': content, 'available': True}
   except:
       return {'content': 'No diagnostics available yet',
               'available': False}

@app.post('/admin/diagnostics/generate')
def generate_diagnostics(payload: dict = Depends(require_admin)):
   import subprocess
   subprocess.Popen(['python3',
                     'automation/generate_diagnostics.py'])
   return {'message': 'Diagnostics generation started'}

# ═══════════════════════════════
# ADMIN — SYSTEM HEALTH
# ═══════════════════════════════
@app.get('/admin/health')
def admin_health(payload: dict = Depends(require_admin)):
   with db.get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           SELECT cpu_percent, ram_percent, disk_percent,
                  redis_mb, pg_connections, bot_cycle_time,
                  active_bots, open_positions, recorded_at
           FROM system_health
           ORDER BY recorded_at DESC LIMIT 168
       """)
       rows = cur.fetchall()

   return [{
       'cpu': float(r[0] or 0),
       'ram': float(r[1] or 0),
       'disk': float(r[2] or 0),
       'redis_mb': float(r[3] or 0),
       'pg_conn': r[4],
       'cycle_time': float(r[5] or 0),
       'active_bots': r[6],
       'open_positions': r[7],
       'recorded_at': str(r[8])
   } for r in rows]

# ═══════════════════════════════
# AUTH — REGISTER / VERIFY
# ═══════════════════════════════
class RegisterRequest(BaseModel):
    email: str
    password: str
    referral_code: Optional[str] = None

@app.post('/auth/register')
def register(req: RegisterRequest, request: Request):
    result, error = auth_module.register_user(
        req.email, req.password, req.referral_code
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

class VerifyRequest(BaseModel):
    user_id: int
    code: str

@app.post('/auth/verify')
def verify(req: VerifyRequest, request: Request):
    ip = request.client.host
    success = auth_module.verify_code(
        req.user_id, req.code, ip
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail='Invalid or expired code'
        )
    return {'message': 'Verified successfully'}

@app.post('/auth/send-code')
def send_code(payload: dict = Depends(verify_token)):
    success = auth_module.send_verification(
        payload['user_id']
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail='Telegram not connected'
        )
    return {'message': 'Code sent via Telegram'}

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

@app.post('/auth/change-password')
def change_password(req: PasswordChange,
                    request: Request,
                    payload: dict = Depends(verify_token)):
    success, message = auth_module.change_password(
        payload['user_id'],
        req.old_password,
        req.new_password,
        request.client.host
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {'message': message}

# ═══════════════════════════════
# SUPPORTED EXCHANGES LIST
# ═══════════════════════════════
@app.get('/exchanges/supported')
def get_supported_exchanges():
    from exchanges import get_supported_exchanges
    return get_supported_exchanges()

# ═══════════════════════════════
# ADMIN — SECURITY LOGS
# ═══════════════════════════════
@app.get('/admin/security-logs')
def admin_security_logs(limit: int = 100,
                         payload: dict = Depends(require_admin)):
    logs = db.get_security_logs(limit=limit)
    return [{'id': l[0], 'user_id': l[1],
              'event': l[2], 'ip': l[3],
              'details': l[4], 'time': str(l[5])}
            for l in logs]

# ═══════════════════════════════
# TELEGRAM — CONNECT
# ═══════════════════════════════
@app.post('/telegram/connect')
def connect_telegram(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    # Generate connect code for user
    code = db.create_verification_code(user_id)
    return {
        'message': f'Send this code to @AverionBot: CONNECT-{code}',
        'code': f'CONNECT-{code}',
        'bot_username': 'AverionBot'
    }

@app.get('/telegram/status')
def telegram_status(payload: dict = Depends(verify_token)):
    user = db.get_user_by_id(payload['user_id'])
    return {
        'connected': bool(user[3]) if user else False,
        'verified': bool(user[4]) if user else False
    }

# ═══════════════════════════════
# AUTH — RESET PASSWORD
# ═══════════════════════════════
class ResetPasswordRequest(BaseModel):
    email: str
    method: str = 'email'

class ResetPasswordConfirm(BaseModel):
    email: str
    code: str
    new_password: str

@app.post('/auth/reset-password')
def reset_password(req: ResetPasswordRequest):
    user = db.get_user_by_email(req.email)
    if not user:
        # Don't reveal if email exists
        return {'message': 'If this email exists · code sent'}

    user_id = user[0]
    code = db.create_verification_code(user_id)

    if req.method == 'telegram':
        chat_id = user[5] if len(user) > 5 else None
        if chat_id:
            import telegram as tg
            tg.send_message(chat_id,
                f'🔐 <b>Password Reset Code</b>\n\n'
                f'Your code: <b>{code}</b>\n'
                f'Valid for 15 minutes.\n\n'
                f'If you did not request this · ignore.'
            )
        else:
            return {'message': 'Telegram not connected · try email'}
    else:
        # Email reset — Phase 6 with SendGrid
        # For now: store code · admin can see in logs
        db.log_security_event(
            user_id, 'password_reset_requested',
            details={'method': req.method, 'code': code}
        )

    return {'message': 'If this email exists · code sent'}

@app.post('/auth/reset-password/confirm')
def reset_password_confirm(req: ResetPasswordConfirm):
    user = db.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=400,
                            detail='Invalid request')

    user_id = user[0]

    # Verify code
    success = db.verify_code(user_id, req.code)
    if not success:
        raise HTTPException(status_code=400,
                            detail='Invalid or expired code')

    # Validate new password
    import re
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400,
                            detail='Password must be at least 8 characters')
    if not re.search(r'[A-Z]', req.new_password):
        raise HTTPException(status_code=400,
                            detail='Password must contain uppercase letter')
    if not re.search(r'[0-9]', req.new_password):
        raise HTTPException(status_code=400,
                            detail='Password must contain a number')
    if not re.search(r'[@$!%*#&]', req.new_password):
        raise HTTPException(status_code=400,
                            detail='Password must contain special character')

    # Update password
    new_hash = auth_module.hash_password(req.new_password)
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET password_hash = %s
            WHERE id = %s
        """, (new_hash, user_id))

    db.log_security_event(user_id, 'password_reset_complete')
    return {'message': 'Password updated · please login'}
import os
import time
import ccxt
import redis
from datetime import datetime, timezone
from dotenv import load_dotenv
import database as db
import telegram as tg

load_dotenv()

PAPER_MODE = os.getenv('PAPER_MODE', 'true').lower() == 'true'
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# ═══════════════════════════════
# REDIS CLIENT
# ═══════════════════════════════
def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# ═══════════════════════════════
# TELEGRAM
# ═══════════════════════════════
# Telegram handled by telegram.py module

# ═══════════════════════════════
# EXCHANGE INITIALIZATION
# ═══════════════════════════════
def init_exchange(exchange_row):
    from exchanges import init_exchange as _init
    return _init(exchange_row)

# ═══════════════════════════════
# PRICE FETCHING
# ═══════════════════════════════
def fetch_and_cache_prices(exchange_obj, exchange_name, r):
    try:
        tickers = exchange_obj.fetch_tickers()
        for symbol, ticker in tickers.items():
            if ticker.get('last'):
                r.setex(
                    f'price:{exchange_name}:{symbol}',
                    120,
                    str(ticker['last'])
                )
        print(f'✅ Prices cached: {len(tickers)} pairs on {exchange_name}')
        return tickers
    except Exception as e:
        print(f'❌ Price fetch error {exchange_name}: {e}')
        db.record_bot_event(None, None, 'price_fetch_error',
                           exchange=exchange_name,
                           error_message=str(e))
        return {}

def get_price(coin, exchange_name, r, tickers):
    # Try Redis first
    cached = r.get(f'price:{exchange_name}:{coin}/USDT')
    if cached:
        return float(cached)
    # Try from tickers
    symbol = f'{coin}/USDT'
    if symbol in tickers and tickers[symbol].get('last'):
        return float(tickers[symbol]['last'])
    return None

# ═══════════════════════════════
# ST FLAG CHECK
# ═══════════════════════════════
def check_st_flag(coin, exchange_name, tickers, r):
    symbol = f'{coin}/USDT'
    # Check Redis cache first
    cached = r.get(f'st:{exchange_name}:{coin}')
    if cached:
        return cached == 'true'

    # Check from tickers
    if symbol in tickers:
        ticker = tickers[symbol]
        # Different exchanges use different fields
        if ticker.get('info', {}).get('status') in ['ST', 'SUSPENDED']:
            r.setex(f'st:{exchange_name}:{coin}', 3600, 'true')
            return True

    r.setex(f'st:{exchange_name}:{coin}', 3600, 'false')
    return False

# ═══════════════════════════════
# SMART QUEUE SCORING
# ═══════════════════════════════
def calculate_score(position, current_price, bot):
    avg_cost = float(position[7] or 0)
    total_invested = float(position[9] or 0)
    dca_count = position[10]
    dca_percent = float(bot[10] or 7.0)
    spacing_mult = float(bot[11] or 1.4)
    size_mult = float(bot[12] or 1.5)
    base_order = float(bot[13] or 1.0)

    if avg_cost == 0 or current_price == 0:
        return 0

    # Loss percentage
    loss_pct = ((avg_cost - current_price) / avg_cost) * 100
    if loss_pct <= 0:
        return 0  # Not in loss · not eligible

    # Next DCA trigger price
    effective_spacing = dca_percent * (spacing_mult ** dca_count)
    next_dca_price = float(position[11] or avg_cost) * (
        1 - effective_spacing / 100
    )

    # Next DCA amount
    next_dca_amount = base_order * (size_mult ** dca_count)

    if next_dca_amount == 0:
        return 0

    # Score = Loss% / USDT required
    score = loss_pct / next_dca_amount

    return score, next_dca_price, next_dca_amount

# ═══════════════════════════════
# EXECUTE TRADE
# ═══════════════════════════════
def execute_buy(exchange_obj, coin, amount_usdt,
                position_id, bot_id, user_id, exchange_id,
                dca_level, reason, r):
    symbol = f'{coin}/USDT'

    if PAPER_MODE:
        # Paper trade
        price = get_price(coin, '', r, {})
        if not price:
            print(f'No price for {coin} · skipping paper trade')
            return None

        quantity = amount_usdt / price
        trade_id = db.record_trade(
            position_id, bot_id, user_id, exchange_id,
            coin, 'buy', price, quantity, amount_usdt,
            0, 'USDT', reason, 'market', f'paper_{int(time.time())}',
            True, dca_level
        )
        print(f'📄 Paper buy: {coin} ${amount_usdt:.2f} @ ${price:.6f}')
        return {'price': price, 'quantity': quantity,
                'trade_id': trade_id}
    else:
        # Live trade
        try:
            order = exchange_obj.create_market_buy_order(
                symbol, None,
                params={'quoteOrderQty': amount_usdt}
            )
            price = float(order.get('average') or
                         order.get('price') or 0)
            quantity = float(order.get('filled') or 0)
            fee = float(order.get('fee', {}).get('cost') or 0)
            fee_currency = order.get('fee', {}).get('currency', 'USDT')
            order_id = order.get('id', '')

            trade_id = db.record_trade(
                position_id, bot_id, user_id, exchange_id,
                coin, 'buy', price, quantity, amount_usdt,
                fee, fee_currency, reason, 'market',
                order_id, False, dca_level
            )
            print(f'✅ Live buy: {coin} ${amount_usdt:.2f} @ ${price:.6f}')
            return {'price': price, 'quantity': quantity,
                    'fee': fee, 'trade_id': trade_id}

        except ccxt.AuthenticationError as e:
            db.pause_exchange(exchange_id, 'API key invalid', 'auth_error')
            send_admin(f'🔴 Exchange paused: API key invalid\nExchange ID: {exchange_id}')
            db.record_bot_event(bot_id, user_id, 'api_auth_error',
                               coin=coin, error_message=str(e))
            return None

        except ccxt.InsufficientFunds:
            print(f'Insufficient funds for {coin}')
            return None

        except Exception as e:
            print(f'Buy error {coin}: {e}')
            db.record_bot_event(bot_id, user_id, 'buy_error',
                               coin=coin, error_message=str(e))
            return None

def execute_sell(exchange_obj, coin, quantity,
                 position_id, bot_id, user_id, exchange_id,
                 reason, r):
    symbol = f'{coin}/USDT'

    if PAPER_MODE:
        price = get_price(coin, '', r, {})
        if not price:
            return None

        usdt_received = quantity * price
        trade_id = db.record_trade(
            position_id, bot_id, user_id, exchange_id,
            coin, 'sell', price, quantity, usdt_received,
            0, 'USDT', reason, 'market',
            f'paper_{int(time.time())}', True, 0
        )
        print(f'📄 Paper sell: {coin} {quantity:.4f} @ ${price:.6f}')
        return {'price': price, 'usdt_received': usdt_received,
                'trade_id': trade_id}
    else:
        try:
            order = exchange_obj.create_market_sell_order(
                symbol, quantity
            )
            price = float(order.get('average') or
                         order.get('price') or 0)
            usdt_received = float(order.get('cost') or
                                   price * quantity)
            fee = float(order.get('fee', {}).get('cost') or 0)
            fee_currency = order.get('fee', {}).get('currency', 'USDT')
            order_id = order.get('id', '')

            trade_id = db.record_trade(
                position_id, bot_id, user_id, exchange_id,
                coin, 'sell', price, quantity, usdt_received,
                fee, fee_currency, reason, 'market',
                order_id, False, 0
            )
            print(f'✅ Live sell: {coin} {quantity:.4f} @ ${price:.6f}')
            return {'price': price, 'usdt_received': usdt_received,
                    'fee': fee, 'trade_id': trade_id}

        except Exception as e:
            print(f'Sell error {coin}: {e}')
            db.record_bot_event(bot_id, user_id, 'sell_error',
                               coin=coin, error_message=str(e))
            return None

# ═══════════════════════════════
# TP CHECK
# ═══════════════════════════════
def check_tp(position, current_price, bot):
    position_id = position[0]
    avg_cost = float(position[7] or 0)
    quantity = float(position[8] or 0)
    tp_armed = position[12]
    peak_price = float(position[13] or 0)
    tp_percent = float(bot[14] or 5.0)
    trailing_percent = float(bot[15] or 2.0)

    if avg_cost == 0:
        return False

    tp_price = avg_cost * (1 + tp_percent / 100)

    # Arm TP when price reaches target
    if current_price >= tp_price and not tp_armed:
        db.arm_tp(position_id, current_price)
        print(f'🎯 TP armed: position {position_id} @ ${current_price:.6f}')
        return False

    # Update peak price
    if tp_armed and current_price > peak_price:
        db.update_peak_price(position_id, current_price)
        return False

    # Fire TP when price drops from peak
    if tp_armed and peak_price > 0:
        trail_price = peak_price * (1 - trailing_percent / 100)
        if current_price <= trail_price:
            print(f'🚀 TP firing: position {position_id}')
            return True

    return False

# ═══════════════════════════════
# OPEN NEW POSITION
# ═══════════════════════════════
def try_open_position(bot, exchange_obj, tickers, r):
    bot_id = bot[0]
    user_id = bot[1]
    exchange_id = bot[2]
    coin_category = db.get_all_coin_categories()
    base_order = float(bot[13] or 1.0)
    method = bot[4]
    direction = bot[5]
    base_coin = bot[10]
    trades_per_bot = bot[11] or 1
    trades_per_coin = bot[12] or 1

    # Check max trades per bot
    open_positions = db.get_open_positions(bot_id=bot_id)
    if len(open_positions) >= trades_per_bot:
        return

    # Get eligible coins
    open_coins = {}
    for p in open_positions:
        coin = p[4]
        open_coins[coin] = open_coins.get(coin, 0) + 1

    # Find coin to trade
    for symbol, ticker in tickers.items():
        if not symbol.endswith(f'/{base_coin}'):
            continue

        coin = symbol.replace(f'/{base_coin}', '')

        # Check trades per coin limit
        if open_coins.get(coin, 0) >= trades_per_coin:
            continue

        # Check gate conditions
        if not check_gate_conditions(bot, coin, open_positions):
            continue

        # Check ST flag
        if check_st_flag(coin, '', tickers, r):
            continue

        category = coin_category.get(coin, 'micro')
        current_price = float(ticker.get('last') or 0)
        if current_price == 0:
            continue

        # Get sequence number
        coin_positions = [p for p in open_positions if p[4] == coin]
        sequence_number = len(coin_positions) + 1
        coin_trade_number = len(coin_positions) + 1

        # Execute entry
        result = execute_buy(
            exchange_obj, coin, base_order,
            None, bot_id, user_id, exchange_id,
            0, 'entry', r
        )

        if result:
            price = result['price']
            quantity = result['quantity']

            # Open position in DB
            pos_id = db.open_position(
                bot_id, user_id, exchange_id, None,
                coin, direction, price, quantity,
                base_order, price, category,
                PAPER_MODE, base_coin,
                sequence_number, coin_trade_number,
                method
            )
            print(f'✅ Position opened: {coin} #{pos_id}')
            tg.notify_trade_open(user_id, coin, direction, result['price'], base_order, method, PAPER_MODE)
            break

def check_gate_conditions(bot, coin, open_positions):
    gate_dca = bot[16]
    gate_timer = bot[17]
    gate_hours = bot[18] or 5

    if not gate_dca and not gate_timer:
        return True  # No gate · always tradeable

    # Find reference position for this coin
    coin_positions = [p for p in open_positions
                      if p[4] == coin and p[20]]  # is_gate_reference

    if not coin_positions:
        return True  # No reference · open first trade

    ref = coin_positions[0]
    ref_since = ref[23]  # gate_reference_since

    if gate_dca:
        dca_count = ref[10]
        if dca_count >= 1:  # Reference hit DCA
            return True

    if gate_timer and ref_since:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        if ref_since.tzinfo is None:
            ref_since = ref_since.replace(tzinfo=timezone.utc)
        elapsed = (now - ref_since).total_seconds() / 3600
        if elapsed >= gate_hours:
            return True

    return False

# ═══════════════════════════════
# MAIN BOT CYCLE
# ═══════════════════════════════
def run_cycle(r):
    cycle_start = time.time()
    print(f'\n--- Cycle {datetime.utcnow()} ---')

    # Get all active bots grouped by exchange
    active_bots = db.get_active_bots()
    if not active_bots:
        print('No active bots')
        return

    # Group by exchange
    exchanges_needed = {}
    for bot in active_bots:
        exc_id = bot[2]
        if exc_id not in exchanges_needed:
            exchanges_needed[exc_id] = []
        exchanges_needed[exc_id].append(bot)

    # Process each exchange
    for exc_id, bots in exchanges_needed.items():
        exc_row = db.get_exchange_by_id(exc_id)
        if not exc_row:
            continue

        # Skip paused exchanges
        if exc_row[7]:  # paused_at
            print(f'Exchange {exc_id} paused · skipping')
            continue

        # Initialize exchange
        exchange_obj = init_exchange(exc_row)
        if not exchange_obj:
            continue

        # Fetch all prices at once
        tickers = fetch_and_cache_prices(
            exchange_obj, exc_row[2], r
        )

        if not tickers:
            continue

        # Get open positions for this exchange
        open_positions = db.get_open_positions(exchange_id=exc_id)

        # ─────────────────────────
        # STEP 1: Check ST flags + TP
        # ─────────────────────────
        positions_to_close = []
        for pos in open_positions:
            coin = pos[4]
            current_price = get_price(coin, exc_row[2], r, tickers)
            if not current_price:
                continue

            # ST flag check
            if check_st_flag(coin, exc_row[2], tickers, r):
                print(f'🚨 ST flag: {coin} · selling')
                result = execute_sell(
                    exchange_obj, coin, float(pos[8] or 0),
                    pos[0], pos[1], pos[2], exc_id, 'st_flag', r
                )
                if result:
                    positions_to_close.append((pos, result, 'st_flag'))
                    db.add_attention_log(
                        pos[2], 'red', 'st_flag',
                        f'{coin} ST flag detected · position closed',
                        bot_id=pos[1], position_id=pos[0]
                    )
                continue

            # TP check
            bot = next((b for b in bots if b[0] == pos[1]), None)
            if not bot:
                continue

            if check_tp(pos, current_price, bot):
                result = execute_sell(
                    exchange_obj, coin, float(pos[8] or 0),
                    pos[0], pos[1], pos[2], exc_id, 'tp', r
                )
                if result:
                    positions_to_close.append((pos, result, 'tp'))

        # Close positions and handle fees
        for pos, result, reason in positions_to_close:
            db.close_position(pos[0], reason)

            if reason == 'tp':
                # Calculate profit and fee
                invested = float(pos[9] or 0)
                received = result.get('usdt_received', 0)
                gross_profit = received - invested

                if gross_profit > 0:
                    fee_amount = gross_profit * 0.20
                    db.deduct_performance_fee(
                        pos[2], pos[0], fee_amount, gross_profit
                    )
                    print(f'💰 TP closed: {pos[4]} profit: ${gross_profit:.2f} fee: ${fee_amount:.2f}')
                    tg.notify_trade_closed(pos[2], pos[4], pos[5], float(pos[7] or 0), result.get('price', 0), gross_profit, fee_amount, pos[10], 'tp', PAPER_MODE)

                # Promote gate reference
                db.promote_gate_reference(pos[1], pos[4])

        # ─────────────────────────
        # STEP 2: Smart Queue DCA
        # ─────────────────────────
        queue_candidates = db.get_queue_candidates(exc_id)
        best_score = 0
        best_candidate = None
        best_next_price = None
        best_next_amount = None

        for pos in queue_candidates:
            coin = pos[0]  # from queue query
            current_price = get_price(coin, exc_row[2], r, tickers)
            if not current_price:
                continue

            bot = next((b for b in bots if b[0] == pos[7]), None)
            if not bot:
                continue

            result = calculate_score(pos, current_price, bot)
            if not result:
                continue

            score, next_dca_price, next_dca_amount = result

            # Check if price reached DCA trigger
            if current_price > next_dca_price:
                continue  # Not triggered yet

            if score > best_score:
                best_score = score
                best_candidate = pos
                best_next_price = next_dca_price
                best_next_amount = next_dca_amount

        # Execute best DCA
        if best_candidate:
            pos_id = best_candidate[0] if hasattr(
                best_candidate, '__getitem__') else best_candidate.id
            coin = best_candidate[1] if hasattr(
                best_candidate, '__getitem__') else best_candidate.coin

            print(f'📊 Queue: {coin} score={best_score:.4f}')

            db.set_position_queued(pos_id, True)
            result = execute_buy(
                exchange_obj, coin, best_next_amount,
                pos_id, best_candidate[7], best_candidate[6],
                exc_id, best_candidate[5] + 1, 'dca', r
            )

            if result:
                # Update position
                old_qty = float(best_candidate[4] or 0)
                old_invested = float(best_candidate[3] or 0)
                new_qty = old_qty + result['quantity']
                new_invested = old_invested + best_next_amount
                new_avg = new_invested / new_qty if new_qty > 0 else 0

                db.update_position_after_dca(
                    pos_id, new_avg, new_qty,
                    new_invested, result['price'],
                    best_candidate[5] + 1
                )
                db.set_position_queued(pos_id, False)

        # ─────────────────────────
        # STEP 3: Open new positions
        # ─────────────────────────
        for bot in bots:
            try_open_position(bot, exchange_obj, tickers, r)

    # Record cycle time
    cycle_time = time.time() - cycle_start
    r.setex('bot:cycle_time', 120, str(round(cycle_time, 2)))
    r.setex('bot:last_cycle', 120, str(datetime.utcnow()))
    r.setex('bot:status', 120, 'running')
    print(f'✅ Cycle complete in {cycle_time:.2f}s')

# ═══════════════════════════════
# BOT LOOP ENTRY
# ═══════════════════════════════
def run_bot():
    print('🚀 Bot loop starting...')
    r = get_redis()
    consecutive_errors = 0

    while True:
        try:
            run_cycle(r)
            consecutive_errors = 0
            time.sleep(60)

        except KeyboardInterrupt:
            print('🛑 Bot stopped')
            break

        except Exception as e:
            consecutive_errors += 1
            print(f'❌ Cycle error ({consecutive_errors}): {e}')
            db.record_bot_event(None, None, 'cycle_error',
                               error_message=str(e))

            if consecutive_errors >= 3:
                send_admin(
                    f'🔴 Averion: {consecutive_errors} consecutive errors\n{str(e)[:200]}'
                )

            time.sleep(30)

if __name__ == '__main__':
    db.init_pool()
    run_bot()
import os
import ccxt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import database as db

load_dotenv()

# ═══════════════════════════════
# FERNET ENCRYPTION
# ═══════════════════════════════
def get_fernet():
   key = os.getenv('FERNET_KEY')
   if not key:
       raise Exception('FERNET_KEY not set in .env')
   return Fernet(key.encode())

def encrypt(text: str) -> str:
   return get_fernet().encrypt(text.encode()).decode()

def decrypt(text: str) -> str:
   return get_fernet().decrypt(text.encode()).decode()

# ═══════════════════════════════
# EXCHANGE INITIALIZATION
# ═══════════════════════════════
def init_exchange(exchange_row):
   exc_id = exchange_row[0]
   exc_name = exchange_row[2]
   api_key_enc = exchange_row[3]
   secret_enc = exchange_row[4]
   passphrase_enc = exchange_row[5]

   try:
       api_key = decrypt(api_key_enc)
       secret = decrypt(secret_enc)
       passphrase = decrypt(passphrase_enc) if passphrase_enc else None

       exchange_class = getattr(ccxt, exc_name)
       config = {
           'apiKey': api_key,
           'secret': secret,
           'enableRateLimit': True,
           'options': {'defaultType': 'spot'}
       }
       if passphrase:
           config['password'] = passphrase

       exchange = exchange_class(config)
       return exchange

   except ccxt.AuthenticationError as e:
       db.pause_exchange(exc_id, 'Authentication failed', 'auth_error')
       db.record_bot_event(None, None, 'auth_error',
                          exchange=exc_name,
                          error_message=str(e))
       return None

   except Exception as e:
       print(f'Exchange init error {exc_name}: {e}')
       db.record_bot_event(None, None, 'init_error',
                          exchange=exc_name,
                          error_message=str(e))
       return None

# ═══════════════════════════════
# EXCHANGES THAT NEED PASSPHRASE
# ═══════════════════════════════
PASSPHRASE_REQUIRED = ['kucoin', 'okx', 'bitget']

def requires_passphrase(exchange_name: str) -> bool:
   return exchange_name.lower() in PASSPHRASE_REQUIRED

# ═══════════════════════════════
# BALANCE FETCHING
# ═══════════════════════════════
def get_balance(exchange_obj, currency='USDT'):
   try:
       balance = exchange_obj.fetch_balance()
       free = float(balance.get(currency, {}).get('free') or 0)
       total = float(balance.get(currency, {}).get('total') or 0)
       return {'free': free, 'total': total, 'currency': currency}
   except ccxt.AuthenticationError:
       raise
   except Exception as e:
       print(f'Balance fetch error: {e}')
       return {'free': 0, 'total': 0, 'currency': currency}

def get_all_balances(exchange_obj):
   try:
       balance = exchange_obj.fetch_balance()
       result = {}
       for currency, amounts in balance.items():
           if isinstance(amounts, dict):
               free = float(amounts.get('free') or 0)
               if free > 0:
                   result[currency] = free
       return result
   except Exception as e:
       print(f'All balances error: {e}')
       return {}

# ═══════════════════════════════
# PRICE FETCHING
# ═══════════════════════════════
def fetch_all_tickers(exchange_obj):
   try:
       return exchange_obj.fetch_tickers()
   except ccxt.RateLimitExceeded:
       print('Rate limit exceeded · waiting 30s')
       import time
       time.sleep(30)
       return fetch_all_tickers(exchange_obj)
   except Exception as e:
       print(f'Ticker fetch error: {e}')
       return {}

def fetch_ticker(exchange_obj, symbol):
   try:
       ticker = exchange_obj.fetch_ticker(symbol)
       return {
           'last': float(ticker.get('last') or 0),
           'bid': float(ticker.get('bid') or 0),
           'ask': float(ticker.get('ask') or 0),
           'volume': float(ticker.get('baseVolume') or 0),
           'symbol': symbol
       }
   except Exception as e:
       print(f'Ticker error {symbol}: {e}')
       return None

# ═══════════════════════════════
# ORDER EXECUTION
# ═══════════════════════════════
def market_buy(exchange_obj, symbol, usdt_amount):
   try:
       order = exchange_obj.create_market_buy_order(
           symbol, None,
           params={'quoteOrderQty': usdt_amount}
       )
       return parse_order(order)
   except ccxt.InsufficientFunds as e:
       return {'error': 'insufficient_funds', 'message': str(e)}
   except ccxt.AuthenticationError as e:
       return {'error': 'auth_error', 'message': str(e)}
   except ccxt.BadSymbol as e:
       return {'error': 'bad_symbol', 'message': str(e)}
   except Exception as e:
       return {'error': 'unknown', 'message': str(e)}

def market_sell(exchange_obj, symbol, quantity):
   try:
       order = exchange_obj.create_market_sell_order(
           symbol, quantity
       )
       return parse_order(order)
   except ccxt.InsufficientFunds as e:
       return {'error': 'insufficient_funds', 'message': str(e)}
   except ccxt.AuthenticationError as e:
       return {'error': 'auth_error', 'message': str(e)}
   except Exception as e:
       return {'error': 'unknown', 'message': str(e)}

def limit_buy(exchange_obj, symbol, quantity, price):
   try:
       order = exchange_obj.create_limit_buy_order(
           symbol, quantity, price
       )
       return parse_order(order)
   except ccxt.InsufficientFunds as e:
       return {'error': 'insufficient_funds', 'message': str(e)}
   except Exception as e:
       return {'error': 'unknown', 'message': str(e)}

def cancel_order(exchange_obj, order_id, symbol):
   try:
       exchange_obj.cancel_order(order_id, symbol)
       return True
   except ccxt.OrderNotFound:
       return True  # Already cancelled
   except Exception as e:
       print(f'Cancel order error: {e}')
       return False

def fetch_order(exchange_obj, order_id, symbol):
   try:
       order = exchange_obj.fetch_order(order_id, symbol)
       return parse_order(order)
   except Exception as e:
       print(f'Fetch order error: {e}')
       return None

def fetch_recent_orders(exchange_obj, limit=100):
   try:
       orders = exchange_obj.fetch_orders(limit=limit)
       return [parse_order(o) for o in orders]
   except Exception as e:
       print(f'Fetch orders error: {e}')
       return []

def parse_order(order):
   return {
       'id': order.get('id'),
       'symbol': order.get('symbol'),
       'side': order.get('side'),
       'type': order.get('type'),
       'status': order.get('status'),
       'price': float(order.get('price') or 0),
       'average': float(order.get('average') or 0),
       'amount': float(order.get('amount') or 0),
       'filled': float(order.get('filled') or 0),
       'remaining': float(order.get('remaining') or 0),
       'cost': float(order.get('cost') or 0),
       'fee': float(order.get('fee', {}).get('cost') or 0),
       'fee_currency': order.get('fee', {}).get('currency', 'USDT'),
       'timestamp': order.get('timestamp')
   }

# ═══════════════════════════════
# EXCHANGE MINIMUM ORDER SIZE
# ═══════════════════════════════
def get_min_order_size(exchange_obj, symbol):
   try:
       markets = exchange_obj.load_markets()
       market = markets.get(symbol, {})
       limits = market.get('limits', {})
       min_amount = limits.get('amount', {}).get('min') or 0
       min_cost = limits.get('cost', {}).get('min') or 0
       return {
           'min_amount': float(min_amount),
           'min_cost': float(min_cost),
           'symbol': symbol
       }
   except Exception as e:
       print(f'Min order error {symbol}: {e}')
       return {'min_amount': 0, 'min_cost': 0, 'symbol': symbol}

def get_all_min_orders(exchange_obj, base_currency='USDT'):
   try:
       markets = exchange_obj.load_markets()
       result = {}
       for symbol, market in markets.items():
           if not symbol.endswith(f'/{base_currency}'):
               continue
           limits = market.get('limits', {})
           min_amount = limits.get('amount', {}).get('min') or 0
           min_cost = limits.get('cost', {}).get('min') or 0
           result[symbol] = {
               'min_amount': float(min_amount),
               'min_cost': float(min_cost)
           }
       return result
   except Exception as e:
       print(f'All min orders error: {e}')
       return {}

# ═══════════════════════════════
# ST FLAG DETECTION
# ═══════════════════════════════
def check_st_flag_exchange(exchange_obj, symbol):
   try:
       ticker = exchange_obj.fetch_ticker(symbol)
       info = ticker.get('info', {})

       # MEXC specific
       if info.get('status') in ['ST', 'SUSPENDED', '3']:
           return True

       # Generic: no trading volume for 24h
       volume = float(ticker.get('baseVolume') or 0)
       if volume == 0:
           return True

       return False
   except ccxt.BadSymbol:
       return True  # Symbol not found = likely suspended
   except Exception:
       return False

# ═══════════════════════════════
# RECONCILIATION
# ═══════════════════════════════
def reconcile_exchange_orders(exchange_obj, exchange_id):
   orders = fetch_recent_orders(exchange_obj, limit=100)
   reconciled = 0

   for order in orders:
       if not order.get('id'):
           continue
       if order.get('status') not in ['closed', 'filled']:
           continue

       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("""
               SELECT id FROM trades
               WHERE exchange_order_id = %s
           """, (order['id'],))

           if not cur.fetchone():
               # Missing trade · insert it
               symbol = order.get('symbol', '')
               coin = symbol.split('/')[0] if '/' in symbol else symbol
               cur.execute("""
                   INSERT INTO trades (
                       exchange_id, coin, side, price,
                       quantity, usdt_amount, order_type,
                       exchange_order_id, is_paper, timestamp
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE, NOW())
               """, (
                   exchange_id, coin,
                   order.get('side', ''),
                   order.get('average') or order.get('price') or 0,
                   order.get('filled') or 0,
                   order.get('cost') or 0,
                   order.get('type', 'market'),
                   order['id']
               ))
               reconciled += 1
               print(f'✅ Reconciled order: {order["id"]}')

   print(f'✅ Reconciliation complete: {reconciled} orders added')
   return reconciled

# ═══════════════════════════════
# SUPPORTED EXCHANGES
# ═══════════════════════════════
SUPPORTED_EXCHANGES = [
   {'id': 'mexc', 'name': 'MEXC', 'passphrase': False},
   {'id': 'kucoin', 'name': 'KuCoin', 'passphrase': True},
   {'id': 'binance', 'name': 'Binance', 'passphrase': False},
   {'id': 'bybit', 'name': 'Bybit', 'passphrase': False},
   {'id': 'okx', 'name': 'OKX', 'passphrase': True},
   {'id': 'bitget', 'name': 'Bitget', 'passphrase': True},
   {'id': 'gate', 'name': 'Gate.io', 'passphrase': False},
]

def get_supported_exchanges():
   return SUPPORTED_EXCHANGES

if __name__ == '__main__':
   print('✅ Exchanges module ready')
   print(f'Supported: {[e["name"] for e in SUPPORTED_EXCHANGES]}')
   print(f'Passphrase required: {[e["name"] for e in SUPPORTED_EXCHANGES if e["passphrase"]]}')
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import database as db

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# ═══════════════════════════════
# CORE SEND FUNCTION
# ═══════════════════════════════
def send_message(chat_id, message, parse_mode='HTML'):
    if not BOT_TOKEN or not chat_id:
        print(f'Telegram not configured · message: {message[:50]}')
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            },
            timeout=10
        )
        return r.status_code == 200
    except Exception as e:
        print(f'Telegram send error: {e}')
        db.queue_notification(None, chat_id, message, 'failed')
        return False

def send_admin(message):
    return send_message(ADMIN_CHAT, message)

# ═══════════════════════════════
# RETRY FAILED NOTIFICATIONS
# ═══════════════════════════════
def retry_pending_notifications():
    pending = db.get_pending_notifications()
    sent = 0
    for notif in pending:
        notif_id = notif[0]
        chat_id = notif[2]
        message = notif[3]
        retry_count = notif[5] if len(notif) > 5 else 0

        if retry_count >= 3:
            # Give up after 3 retries
            db.mark_notification_sent(notif_id)
            continue

        success = send_message(chat_id, message)
        if success:
            db.mark_notification_sent(notif_id)
            sent += 1
        else:
            db.increment_notification_retry(notif_id)

    if sent > 0:
        print(f'✅ Sent {sent} pending notifications')

# ═══════════════════════════════
# TRADE NOTIFICATIONS
# ═══════════════════════════════
def notify_trade_open(user_id, coin, direction,
                       price, amount, method, is_paper):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:  # telegram_chat_id
        return

    chat_id = user[3]
    mode = '📄 Paper' if is_paper else '💰 Live'
    emoji = '📈' if direction == 'long' else '📉'

    msg = f"""{emoji} <b>Trade Opened</b> {mode}

Coin: <b>{coin}</b>
Direction: {direction.upper()}
Entry Price: ${price:.6f}
Amount: ${amount:.2f}
Method: {method}
Time: {datetime.utcnow().strftime('%H:%M UTC')}"""

    send_message(chat_id, msg)

def notify_trade_closed(user_id, coin, direction,
                         entry_price, exit_price,
                         profit, fee, dca_count,
                         reason, is_paper):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    chat_id = user[3]
    mode = '📄 Paper' if is_paper else '💰 Live'
    profit_emoji = '✅' if profit > 0 else '❌'
    net_profit = profit - fee

    msg = f"""{profit_emoji} <b>Trade Closed</b> {mode}

Coin: <b>{coin}</b>
Direction: {direction.upper()}
Entry: ${entry_price:.6f}
Exit: ${exit_price:.6f}
DCA Levels: {dca_count}
Gross Profit: ${profit:.2f}
Fee (20%): -${fee:.2f}
<b>Net Profit: ${net_profit:.2f}</b>
Reason: {reason.upper()}
Time: {datetime.utcnow().strftime('%H:%M UTC')}"""

    send_message(chat_id, msg)

def notify_dca(user_id, coin, dca_level,
               price, amount, avg_cost, is_paper):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    chat_id = user[3]
    mode = '📄' if is_paper else '💰'

    msg = f"""{mode} <b>DCA #{dca_level}</b>

Coin: <b>{coin}</b>
Price: ${price:.6f}
Amount: ${amount:.2f}
New Avg Cost: ${avg_cost:.6f}"""

    send_message(chat_id, msg)

# ═══════════════════════════════
# ALERT NOTIFICATIONS
# ═══════════════════════════════
def alert_reserve_low(user_id, balance):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>Reserve Wallet Low</b>

Balance: <b>${balance:.2f}</b>
Performance fees may not be collected.
Please top up your reserve wallet.

<a href="https://averionbot.com/settings">Top Up Now</a>"""

    send_message(user[3], msg)
    db.add_attention_log(user_id, 'red', 'reserve_low',
                         f'Reserve wallet low: ${balance:.2f}')

def alert_reserve_empty(user_id):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""🔴 <b>Reserve Wallet Empty</b>

Fees will be recorded as debt.
Bot continues trading normally.
Top up to clear debt and avoid issues."""

    send_message(user[3], msg)

def alert_api_key_expiring(user_id, exchange_name, days_left):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>API Key Expiring Soon</b>

Exchange: <b>{exchange_name}</b>
Days remaining: <b>{days_left}</b>
Please update your API key before it expires."""

    send_message(user[3], msg)
    db.add_attention_log(user_id, 'red', 'api_expiring',
                         f'{exchange_name} API key expires in {days_left} days')

def alert_api_key_invalid(user_id, exchange_name):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""🔴 <b>API Key Invalid</b>

Exchange: <b>{exchange_name}</b>
Exchange has been paused.
Please update your API key."""

    send_message(user[3], msg)
    db.add_attention_log(user_id, 'red', 'api_invalid',
                         f'{exchange_name} API key invalid · exchange paused')

def alert_st_flag(user_id, coin, pnl):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    emoji = '✅' if pnl >= 0 else '❌'
    msg = f"""🚨 <b>ST Flag Detected</b>

Coin: <b>{coin}</b>
Position closed automatically.
P&L: {emoji} ${pnl:.2f}

Exchange suspended trading on this coin."""

    send_message(user[3], msg)

def alert_checkpoint(user_id, coin, dca_level,
                      next_cost, bot_id, position_id):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>DCA Checkpoint Reached</b>

Coin: <b>{coin}</b>
Level: {dca_level}
Next DCA cost: ${next_cost:.2f}

DCA has been turned OFF automatically.
Open dashboard to continue or wait for TP."""

    send_message(user[3], msg)

def alert_low_balance(user_id, exchange_name):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>Insufficient Balance</b>

Exchange: <b>{exchange_name}</b>
No position can be funded right now.
Bot will retry when funds available."""

    send_message(user[3], msg)

# ═══════════════════════════════
# REPORT NOTIFICATIONS
# ═══════════════════════════════
def send_daily_report(user_id, closed_today, profit_today,
                       fees_today, open_positions, reserve):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    profit_emoji = '📈' if profit_today > 0 else '📊'

    msg = f"""{profit_emoji} <b>Daily Report</b>
{datetime.utcnow().strftime('%B %d, %Y')}

Closed today: {closed_today}
Gross profit: ${profit_today:.2f}
Fees paid: ${fees_today:.2f}
Net profit: ${profit_today - fees_today:.2f}

Open positions: {open_positions}
Reserve balance: ${reserve:.2f}"""

    send_message(user[3], msg)

def send_weekly_report(user_id, closed_week, profit_week,
                        fees_week, best_coin, worst_coin):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""📊 <b>Weekly Report</b>
{datetime.utcnow().strftime('%B %d, %Y')}

Positions closed: {closed_week}
Gross profit: ${profit_week:.2f}
Fees paid: ${fees_week:.2f}
Net profit: ${profit_week - fees_week:.2f}

Best coin: {best_coin or 'N/A'}
Worst coin: {worst_coin or 'N/A'}"""

    send_message(user[3], msg)

def send_monthly_report(user_id, closed_month,
                         profit_month, fees_month):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""📅 <b>Monthly Report</b>
{datetime.utcnow().strftime('%B %Y')}

Positions closed: {closed_month}
Gross profit: ${profit_month:.2f}
Fees paid: ${fees_month:.2f}
<b>Net profit: ${profit_month - fees_month:.2f}</b>"""

    send_message(user[3], msg)

# ═══════════════════════════════
# VERIFICATION CODE
# ═══════════════════════════════
def send_verification_code(user_id, chat_id):
    code = db.create_verification_code(user_id)

    msg = f"""🔐 <b>Averion Verification Code</b>

Your code: <b>{code}</b>
Valid for 15 minutes.

If you did not request this, ignore this message."""

    success = send_message(chat_id, msg)
    if success:
        db.log_security_event(user_id, 'verification_code_sent',
                              details={'chat_id': chat_id})
    return success

# ═══════════════════════════════
# ADMIN NOTIFICATIONS
# ═══════════════════════════════
def admin_bot_started(mode):
    send_admin(
        f'🚀 <b>Averion Started</b>\n'
        f'Mode: {"📄 Paper" if mode else "💰 Live"}\n'
        f'Time: {datetime.utcnow().strftime("%H:%M UTC")}'
    )

def admin_bot_stopped(reason='manual'):
    send_admin(
        f'🛑 <b>Averion Stopped</b>\n'
        f'Reason: {reason}\n'
        f'Time: {datetime.utcnow().strftime("%H:%M UTC")}'
    )

def admin_error(error_message, consecutive=1):
    send_admin(
        f'🔴 <b>Bot Error #{consecutive}</b>\n\n'
        f'{error_message[:500]}'
    )

def admin_cron_complete(step, duration, records):
    send_admin(
        f'✅ <b>Cron: {step}</b>\n'
        f'Duration: {duration:.1f}s\n'
        f'Records: {records}'
    )

def admin_cron_failed(step, error):
    send_admin(
        f'❌ <b>Cron Failed: {step}</b>\n\n'
        f'{str(error)[:300]}'
    )

def admin_reclassification(coin, from_cat, to_cat):
    send_admin(
        f'📊 <b>Reclassification</b>\n'
        f'{coin}: {from_cat} → {to_cat}'
    )

if __name__ == '__main__':
    print('✅ Telegram module ready')
    if BOT_TOKEN:
        print(f'Bot token: {BOT_TOKEN[:10]}...')
    else:
        print('⚠️ No bot token configured')
import os
import hashlib
import secrets
import jwt
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import database as db
import telegram as tg
import email_service as email_svc

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
TOKEN_DAYS = 30

# ═══════════════════════════════
# PASSWORD HASHING
# ═══════════════════════════════
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(
        f'{salt}{password}'.encode()
    ).hexdigest()
    return f'{salt}:{hashed}'

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split(':')
        return hashlib.sha256(
            f'{salt}{password}'.encode()
        ).hexdigest() == hashed
    except:
        return False

# ═══════════════════════════════
# JWT TOKENS
# ═══════════════════════════════
def create_token(user_id: int, is_admin: bool) -> str:
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=TOKEN_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise Exception('Token expired · please login again')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def is_token_expiring_soon(token: str, days=7) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        exp = datetime.utcfromtimestamp(payload['exp'])
        remaining = (exp - datetime.utcnow()).days
        return remaining <= days
    except:
        return True

# ═══════════════════════════════
# LOGIN
# ═══════════════════════════════
def login(email: str, password: str,
          ip: str = None, user_agent: str = None):
    user = db.get_user_by_email(email)

    if not user:
        db.log_security_event(
            None, 'login_failed', ip, user_agent,
            {'email': email, 'reason': 'user_not_found'}
        )
        return None, 'Invalid email or password'

    user_id = user[0]
    password_hash = user[2]
    is_admin = user[3]
    is_suspended = user[6] if len(user) > 6 else False

    if is_suspended:
        db.log_security_event(
            user_id, 'login_blocked', ip, user_agent,
            {'reason': 'account_suspended'}
        )
        return None, 'Account suspended'

    if not verify_password(password, password_hash):
        db.log_security_event(
            user_id, 'login_failed', ip, user_agent,
            {'reason': 'wrong_password'}
        )
        return None, 'Invalid email or password'

    # Check if needs verification (new device or 30 days)
    needs_verification = check_needs_verification(user_id, ip)

    token = create_token(user_id, is_admin)

    db.log_security_event(
        user_id, 'login_success', ip, user_agent,
        {'needs_verification': needs_verification}
    )

    return {
        'token': token,
        'user_id': user_id,
        'email': email,
        'is_admin': is_admin,
        'needs_verification': needs_verification
    }, None

# ═══════════════════════════════
# DEVICE / SESSION VERIFICATION
# ═══════════════════════════════
def check_needs_verification(user_id: int, ip: str) -> bool:
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )

    # Check if this IP is trusted
    trusted_key = f'trusted_ip:{user_id}:{ip}'
    if r.get(trusted_key):
        return False  # Known device · no verification needed

    # New device · needs verification
    return True

def trust_device(user_id: int, ip: str, days=30):
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    trusted_key = f'trusted_ip:{user_id}:{ip}'
    r.setex(trusted_key, days * 86400, '1')

# ═══════════════════════════════
# VERIFICATION CODE
# ═══════════════════════════════
def send_verification(user_id: int) -> bool:
    user = db.get_user_by_id(user_id)
    if not user:
        return False

    telegram_chat_id = user[3]  # telegram_chat_id
    if not telegram_chat_id:
        return False

    return tg.send_verification_code(user_id, telegram_chat_id)

def verify_code(user_id: int, code: str,
                ip: str = None) -> bool:
    success = db.verify_code(user_id, code)

    if success:
        trust_device(user_id, ip, days=30)
        db.log_security_event(
            user_id, 'verification_success', ip,
            details={'code_verified': True}
        )

    else:
        db.log_security_event(
            user_id, 'verification_failed', ip,
            details={'reason': 'wrong_or_expired_code'}
        )

    return success

# ═══════════════════════════════
# BRUTE FORCE PROTECTION
# ═══════════════════════════════
def check_brute_force(ip: str) -> bool:
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    key = f'login_fails:{ip}'
    fails = r.get(key)
    return int(fails) >= 5 if fails else False

def record_login_fail(ip: str):
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    key = f'login_fails:{ip}'
    count = r.incr(key)
    r.expire(key, 1800)  # 30 minutes

    if count >= 5:
        tg.send_admin(
            f'🔴 <b>Brute Force Detected</b>\n'
            f'IP: {ip}\n'
            f'Failed attempts: {count}\n'
            f'Locked for 30 minutes'
        )

def clear_login_fails(ip: str):
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    r.delete(f'login_fails:{ip}')

# ═══════════════════════════════
# USER REGISTRATION
# ═══════════════════════════════
def register_user(email: str, password: str,
                   referral_code: str = None) -> tuple:
    # Check if email exists
    existing = db.get_user_by_email(email)
    if existing:
        return None, 'Email already registered'

    # Validate password strength
    import re
    if len(password) < 8:
        return None, 'Password must be at least 8 characters'
    if not re.search(r'[A-Z]', password):
        return None, 'Password must contain at least one uppercase letter'
    if not re.search(r'[0-9]', password):
        return None, 'Password must contain at least one number'
    if not re.search(r'[@$!%*#&]', password):
        return None, 'Password must contain at least one special character'

    # Hash password
    password_hash = hash_password(password)

    # Generate referral code
    user_referral = secrets.token_hex(4).upper()

    # Create user
    user_id = db.create_user(email, password_hash, user_referral)

    # Create reserve wallet
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reserve_wallets (user_id)
            VALUES (%s)
        """, (user_id,))

    # Handle referral
    if referral_code:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id FROM users
                WHERE referral_code = %s
            """, (referral_code,))
            referrer = cur.fetchone()
            if referrer:
                cur.execute("""
                    INSERT INTO referrals
                    (referrer_user_id, referred_user_id)
                    VALUES (%s, %s)
                """, (referrer[0], user_id))

    db.log_security_event(
        user_id, 'registration',
        details={'email': email, 'referral': referral_code}
    )

    # Send welcome email
    email_svc.send_welcome_email(email)

    # Send verification code
    code = db.create_verification_code(user_id)
    email_svc.send_verification_email(email, code)

    token = create_token(user_id, False)
    return {'token': token, 'user_id': user_id, 'needs_email_verification': True}, None

# ═══════════════════════════════
# PASSWORD CHANGE
# ═══════════════════════════════
def change_password(user_id: int, old_password: str,
                     new_password: str, ip: str = None) -> tuple:
    user = db.get_user_by_id(user_id)
    if not user:
        return False, 'User not found'

    if not verify_password(old_password, user[2]):
        db.log_security_event(
            user_id, 'password_change_failed', ip,
            details={'reason': 'wrong_old_password'}
        )
        return False, 'Current password incorrect'

    if len(new_password) < 8:
        return False, 'Password must be at least 8 characters'

    new_hash = hash_password(new_password)
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET password_hash = %s
            WHERE id = %s
        """, (new_hash, user_id))

    db.log_security_event(
        user_id, 'password_changed', ip
    )
    tg.send_admin(f'🔐 Password changed · User #{user_id}')
    return True, 'Password changed successfully'

if __name__ == '__main__':
    print('✅ Auth module ready')
    test_hash = hash_password('testpassword123')
    print(f'✅ Password hashing works: {verify_password("testpassword123", test_hash)}')
import os
import requests
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'noreply@averionbot.com')
SENDER_NAME = 'Averion'

# ═══════════════════════════════
# CORE SEND FUNCTION
# ═══════════════════════════════
def send_email(to: str, subject: str, html: str) -> bool:
    if not RESEND_API_KEY:
        print(f'Email not configured · subject: {subject}')
        return False
    try:
        res = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'from': f'{SENDER_NAME} <{SENDER_EMAIL}>',
                'to': [to],
                'subject': subject,
                'html': html
            },
            timeout=10
        )
        if res.status_code == 200:
            print(f'✅ Email sent to {to}: {subject}')
            return True
        else:
            print(f'❌ Email failed: {res.status_code} {res.text}')
            return False
    except Exception as e:
        print(f'❌ Email error: {e}')
        return False

# ═══════════════════════════════
# EMAIL TEMPLATES
# ═══════════════════════════════
def _base_template(content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif;
                   background: #0E0E1C; color: #F0F0FF;
                   margin: 0; padding: 0; }}
            .container {{ max-width: 560px; margin: 40px auto;
                         background: #16162A;
                         border: 1px solid #2A2A45;
                         border-radius: 16px;
                         padding: 40px; }}
            .logo {{ font-size: 24px; font-weight: 800;
                    color: #10D98A; letter-spacing: 2px;
                    margin-bottom: 32px; }}
            .content {{ color: #CCCCDD; line-height: 1.7; }}
            .code {{ background: #0E0E1C; border: 1px solid #2A2A45;
                    border-radius: 10px; padding: 20px;
                    text-align: center; font-size: 32px;
                    font-weight: 800; color: #10D98A;
                    letter-spacing: 8px; margin: 24px 0; }}
            .btn {{ display: inline-block; background: #10D98A;
                   color: #0E0E1C; padding: 14px 32px;
                   border-radius: 10px; text-decoration: none;
                   font-weight: 700; margin: 24px 0; }}
            .footer {{ margin-top: 32px; font-size: 12px;
                      color: #555566; text-align: center; }}
            .warning {{ background: rgba(244,100,95,0.1);
                       border: 1px solid rgba(244,100,95,0.3);
                       border-radius: 8px; padding: 12px;
                       color: #F4645F; font-size: 13px;
                       margin-top: 16px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">AVERION</div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                © 2026 Averion · averionbot.com<br>
                Intelligent DCA Trading Platform
            </div>
        </div>
    </body>
    </html>
    """

# ═══════════════════════════════
# VERIFICATION EMAIL
# ═══════════════════════════════
def send_verification_email(to: str, code: str) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">Verify your email</h2>
        <p>Enter this code in Averion to verify your account:</p>
        <div class="code">{code}</div>
        <p style="color:#888;font-size:13px">
            Valid for 15 minutes.<br>
            If you did not create an Averion account, ignore this email.
        </p>
    """)
    return send_email(to, 'Verify your Averion account', html)

# ═══════════════════════════════
# PASSWORD RESET EMAIL
# ═══════════════════════════════
def send_password_reset_email(to: str, code: str) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">Reset your password</h2>
        <p>Enter this code to reset your Averion password:</p>
        <div class="code">{code}</div>
        <p style="color:#888;font-size:13px">
            Valid for 15 minutes.
        </p>
        <div class="warning">
            ⚠️ If you did not request this, your account may be
            at risk. Change your password immediately.
        </div>
    """)
    return send_email(to, 'Reset your Averion password', html)

# ═══════════════════════════════
# WELCOME EMAIL
# ═══════════════════════════════
def send_welcome_email(to: str) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">Welcome to Averion! 🚀</h2>
        <p>Your account is ready. Here is how to get started:</p>
        <ol style="color:#CCCCDD;line-height:2">
            <li>Connect your exchange (MEXC or KuCoin)</li>
            <li>Create your first bot</li>
            <li>Start with paper trading</li>
            <li>Go live when ready</li>
        </ol>
        <p>We only charge <strong style="color:#10D98A">20%
        of your profits</strong>. Loss months cost you nothing.</p>
        <a href="https://averionbot.com/dashboard" class="btn">
            Open Dashboard →
        </a>
        <p style="color:#888;font-size:13px">
            Questions? Reply to this email or contact
            support@averionbot.com
        </p>
    """)
    return send_email(to, 'Welcome to Averion!', html)

# ═══════════════════════════════
# RESERVE WALLET LOW
# ═══════════════════════════════
def send_reserve_low_email(to: str, balance: float) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">⚠️ Reserve Wallet Low</h2>
        <p>Your reserve wallet balance is low:</p>
        <div class="code" style="color:#F59E0B;font-size:24px">
            ${balance:.2f} USDT
        </div>
        <p>Performance fees may not be collected.
           Please top up to keep your bots running.</p>
        <a href="https://averionbot.com/settings" class="btn">
            Top Up Now →
        </a>
    """)
    return send_email(to, '⚠️ Averion Reserve Wallet Low', html)

# ═══════════════════════════════
# API KEY EXPIRING
# ═══════════════════════════════
def send_api_key_expiring_email(to: str, exchange: str,
                                 days_left: int) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">⚠️ API Key Expiring</h2>
        <p>Your <strong>{exchange}</strong> API key expires
           in <strong style="color:#F4645F">{days_left} days</strong>.
        </p>
        <p>Update your API key before it expires to avoid
           trading interruptions.</p>
        <a href="https://averionbot.com/settings" class="btn">
            Update API Key →
        </a>
    """)
    return send_email(
        to,
        f'⚠️ {exchange} API Key Expiring in {days_left} Days',
        html
    )

# ═══════════════════════════════
# UPDATE auth.py TO USE EMAIL SERVICE
# ═══════════════════════════════
# In auth.py register_user() → call:
#   email_service.send_verification_email(email, code)
# In auth.py reset password → call:
#   email_service.send_password_reset_email(email, code)
# In auth.py after registration → call:
#   email_service.send_welcome_email(email)

if __name__ == '__main__':
    print('✅ Email service ready')
    print(f'Provider: Resend')
    print(f'Sender: {SENDER_EMAIL}')
    if RESEND_API_KEY:
        print('✅ API key configured')
    else:
        print('⚠️ RESEND_API_KEY not set · emails will not send')
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Averion — Intelligent DCA Trading</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg: #0E0E1C;
            --card: #16162A;
            --border: #2A2A45;
            --green: #10D98A;
            --blue: #38BDF8;
            --text: #FFFFFF;
            --muted: #888888;
        }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
        }

        /* ── NAV ── */
        nav {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(14, 14, 28, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            z-index: 100;
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav-logo {
            font-size: 20px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--green), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
        }

        .nav-links {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .btn-nav {
            padding: 8px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text);
        }

        .btn-outline:hover {
            border-color: var(--green);
            color: var(--green);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--green), #0BB876);
            border: none;
            color: #0E0E1C;
        }

        .btn-primary:hover { opacity: 0.9; }

        /* ── HERO ── */
        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 120px 24px 80px;
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: 20%;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 600px;
            background: radial-gradient(circle,
                rgba(16, 217, 138, 0.08) 0%,
                transparent 70%);
            pointer-events: none;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(16, 217, 138, 0.1);
            border: 1px solid rgba(16, 217, 138, 0.3);
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 13px;
            color: var(--green);
            margin-bottom: 24px;
        }

        .hero h1 {
            font-size: clamp(36px, 6vw, 72px);
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 20px;
        }

        .hero h1 span {
            background: linear-gradient(135deg, var(--green), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: clamp(16px, 2vw, 20px);
            color: var(--muted);
            max-width: 560px;
            margin: 0 auto 40px;
        }

        .hero-buttons {
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .btn-hero {
            padding: 14px 32px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }

        /* ── STATS ── */
        .stats {
            display: flex;
            justify-content: center;
            gap: 48px;
            flex-wrap: wrap;
            margin-top: 64px;
            padding: 32px;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
        }

        .stat-item { text-align: center; }

        .stat-value {
            font-size: 32px;
            font-weight: 800;
            color: var(--green);
        }

        .stat-label {
            font-size: 13px;
            color: var(--muted);
            margin-top: 4px;
        }

        /* ── SECTIONS ── */
        section {
            padding: 80px 24px;
            max-width: 1100px;
            margin: 0 auto;
        }

        .section-title {
            text-align: center;
            margin-bottom: 48px;
        }

        .section-title h2 {
            font-size: clamp(28px, 4vw, 44px);
            font-weight: 800;
            margin-bottom: 12px;
        }

        .section-title p {
            color: var(--muted);
            font-size: 16px;
            max-width: 500px;
            margin: 0 auto;
        }

        /* ── FEATURES ── */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
        }

        .feature-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            transition: border-color 0.2s;
        }

        .feature-card:hover {
            border-color: rgba(16, 217, 138, 0.4);
        }

        .feature-icon {
            font-size: 32px;
            margin-bottom: 16px;
        }

        .feature-card h3 {
            font-size: 18px;
            margin-bottom: 10px;
        }

        .feature-card p {
            color: var(--muted);
            font-size: 14px;
            line-height: 1.7;
        }

        /* ── HOW IT WORKS ── */
        .steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
        }

        .step {
            text-align: center;
            padding: 32px 24px;
        }

        .step-number {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--green), var(--blue));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 18px;
            color: #0E0E1C;
            margin: 0 auto 16px;
        }

        .step h3 {
            font-size: 18px;
            margin-bottom: 10px;
        }

        .step p {
            color: var(--muted);
            font-size: 14px;
        }

        /* ── PRICING ── */
        .pricing-card {
            background: var(--card);
            border: 1px solid var(--green);
            border-radius: 20px;
            padding: 48px;
            text-align: center;
            max-width: 500px;
            margin: 0 auto;
        }

        .pricing-badge {
            display: inline-block;
            background: rgba(16, 217, 138, 0.1);
            border: 1px solid rgba(16, 217, 138, 0.3);
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 13px;
            color: var(--green);
            margin-bottom: 20px;
        }

        .pricing-amount {
            font-size: 64px;
            font-weight: 800;
            color: var(--green);
            line-height: 1;
        }

        .pricing-amount span {
            font-size: 24px;
            color: var(--muted);
        }

        .pricing-desc {
            color: var(--muted);
            margin: 16px 0 28px;
            font-size: 15px;
        }

        .pricing-features {
            list-style: none;
            text-align: left;
            margin-bottom: 32px;
        }

        .pricing-features li {
            padding: 10px 0;
            border-bottom: 1px solid var(--border);
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .pricing-features li:last-child {
            border-bottom: none;
        }

        .check { color: var(--green); font-size: 16px; }

        /* ── CTA ── */
        .cta-section {
            text-align: center;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 64px 32px;
            margin: 0 24px 80px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        .cta-section h2 {
            font-size: clamp(24px, 4vw, 40px);
            font-weight: 800;
            margin-bottom: 16px;
        }

        .cta-section p {
            color: var(--muted);
            margin-bottom: 32px;
            font-size: 16px;
        }

        /* ── FOOTER ── */
        footer {
            border-top: 1px solid var(--border);
            padding: 32px 24px;
            text-align: center;
            color: var(--muted);
            font-size: 13px;
        }

        footer a {
            color: var(--muted);
            text-decoration: none;
            margin: 0 12px;
        }

        footer a:hover { color: var(--green); }
    </style>
</head>
<body>

<!-- NAV -->
<nav>
    <div class="nav-logo">AVERION</div>
    <div class="nav-links">
        <a href="/login" class="btn-nav btn-outline">Sign In</a>
        <a href="/register" class="btn-nav btn-primary">Get Started</a>
    </div>
</nav>

<!-- HERO -->
<div class="hero">
    <div>
        <div class="hero-badge">🚀 Performance-based pricing — we win when you win</div>
        <h1>
            The Smarter Way to<br>
            <span>DCA Trade Crypto</span>
        </h1>
        <p>
            Automate your DCA strategy across multiple exchanges.
            We only charge 20% of your profits — zero fees on losses.
        </p>
        <div class="hero-buttons">
            <a href="/register" class="btn-hero btn-primary">
                Start for Free
            </a>
            <a href="/login" class="btn-hero btn-outline btn-nav">
                Sign In
            </a>
        </div>

        <!-- Stats -->
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">20%</div>
                <div class="stat-label">Only on profits</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">7</div>
                <div class="stat-label">Exchanges supported</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">24/7</div>
                <div class="stat-label">Automated trading</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">0%</div>
                <div class="stat-label">Fee on losses</div>
            </div>
        </div>
    </div>
</div>

<!-- FEATURES -->
<section>
    <div class="section-title">
        <h2>Everything you need to trade smarter</h2>
        <p>Powerful DCA automation built for real traders</p>
    </div>
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>Smart DCA Engine</h3>
            <p>
                10 entry methods analyzed simultaneously.
                Our AI selects the best moment to enter based on
                RSI, VWAP, volume, and market conditions.
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🏦</div>
            <h3>Multi-Exchange Support</h3>
            <p>
                Trade on MEXC, KuCoin, Binance, Bybit, OKX,
                Bitget, and Gate.io from one dashboard.
                Your funds stay on the exchange — always.
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Smart Queue System</h3>
            <p>
                Automatic capital prioritization. The bot
                always recovers your most critical positions
                first using our proprietary scoring formula.
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <h3>Safety First</h3>
            <p>
                ST flag detection, DCA checkpoints, reserve
                wallet protection, and automatic position
                recovery keep your capital safe.
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3>Telegram Alerts</h3>
            <p>
                Real-time trade notifications, daily reports,
                and critical alerts delivered instantly to
                your Telegram. Never miss a trade.
            </p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <h3>Performance Only</h3>
            <p>
                We charge 20% only on winning trades.
                Loss months cost you nothing. Our success
                is directly tied to your profits.
            </p>
        </div>
    </div>
</section>

<!-- HOW IT WORKS -->
<section style="background: #12122040; border-radius: 24px; max-width: 100%; padding: 80px 24px;">
    <div style="max-width: 1100px; margin: 0 auto;">
        <div class="section-title">
            <h2>How it works</h2>
            <p>Up and running in minutes</p>
        </div>
        <div class="steps">
            <div class="step">
                <div class="step-number">1</div>
                <h3>Connect Exchange</h3>
                <p>Add your exchange API key securely.
                   Read-only + trade permissions only.
                   No withdrawal access — ever.</p>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <h3>Create Your Bot</h3>
                <p>Choose your strategy, coins, and
                   parameters. Or let Smart DCA handle
                   everything automatically.</p>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <h3>Earn Automatically</h3>
                <p>Bot runs 24/7, executes trades,
                   takes profits, and reports daily.
                   You just watch your balance grow.</p>
            </div>
        </div>
    </div>
</section>

<!-- PRICING -->
<section>
    <div class="section-title">
        <h2>Simple, honest pricing</h2>
        <p>No monthly fees. No hidden charges. Only pay when you profit.</p>
    </div>
    <div class="pricing-card">
        <div class="pricing-badge">Performance Based</div>
        <div class="pricing-amount">20%<span> of profit</span></div>
        <p class="pricing-desc">
            We take 20% of winning trades only.<br>
            Loss trades cost you absolutely nothing.
        </p>
        <ul class="pricing-features">
            <li><span class="check">✓</span> 5 bots included free</li>
            <li><span class="check">✓</span> 100 trades per month free</li>
            <li><span class="check">✓</span> All exchanges included</li>
            <li><span class="check">✓</span> Smart DCA engine</li>
            <li><span class="check">✓</span> Telegram notifications</li>
            <li><span class="check">✓</span> Daily Excel reports</li>
            <li><span class="check">✓</span> 0% fee on losing trades</li>
        </ul>
        <a href="/register" class="btn-hero btn-primary" style="display:block; text-align:center;">
            Start for Free
        </a>
    </div>
</section>

<!-- CTA -->
<div class="cta-section">
    <h2>Ready to trade smarter?</h2>
    <p>Join traders who let their bots do the work.<br>
       Start with paper trading — no risk required.</p>
    <a href="/register" class="btn-hero btn-primary">
        Create Free Account
    </a>
</div>

<!-- FOOTER -->
<footer>
    <div style="margin-bottom: 16px;">
        <span style="font-weight: 700; color: #FFF;">AVERION</span>
    </div>
    <div>
        <a href="/login">Sign In</a>
        <a href="/register">Register</a>
    </div>
    <div style="margin-top: 16px;">
        © 2026 Averion · Intelligent DCA Trading Platform
    </div>
</footer>

</body>
</html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Averion — Sign In</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0E0E1C; --card: #16162A;
            --border: #2A2A45; --green: #10D98A;
            --blue: #38BDF8; --red: #F4645F;
            --text: #FFFFFF; --muted: #888888;
        }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .logo {
            text-align: center;
            margin-bottom: 32px;
        }
        .logo a {
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--green), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
            text-decoration: none;
        }
        .logo p {
            color: var(--muted);
            font-size: 13px;
            margin-top: 6px;
        }
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 36px;
            width: 100%;
            max-width: 420px;
        }
        .card h2 {
            font-size: 22px;
            margin-bottom: 6px;
        }
        .card .sub {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 28px;
        }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            font-size: 13px;
            color: #AAA;
            margin-bottom: 8px;
        }
        input {
            width: 100%;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 13px 16px;
            color: var(--text);
            font-size: 15px;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus { border-color: var(--green); }
        input::placeholder { color: #444; }
        .btn {
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: opacity 0.2s;
            text-decoration: none;
            display: block;
            text-align: center;
            border: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--green), #0BB876);
            color: #0E0E1C;
        }
        .btn-primary:hover { opacity: 0.9; }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
        .error {
            background: rgba(244,100,95,0.1);
            border: 1px solid rgba(244,100,95,0.3);
            border-radius: 8px;
            padding: 12px;
            color: var(--red);
            font-size: 13px;
            margin-bottom: 16px;
            display: none;
        }
        .forgot {
            text-align: right;
            margin-top: -12px;
            margin-bottom: 20px;
        }
        .forgot a {
            color: var(--muted);
            font-size: 12px;
            text-decoration: none;
            cursor: pointer;
        }
        .forgot a:hover { color: var(--green); }
        .divider {
            text-align: center;
            color: var(--muted);
            font-size: 13px;
            margin: 20px 0;
            position: relative;
        }
        .divider::before, .divider::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 42%;
            height: 1px;
            background: var(--border);
        }
        .divider::before { left: 0; }
        .divider::after { right: 0; }
        .bottom-link {
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: var(--muted);
        }
        .bottom-link a {
            color: var(--green);
            text-decoration: none;
            font-weight: 600;
        }
        .spinner {
            display: inline-block;
            width: 14px; height: 14px;
            border: 2px solid rgba(0,0,0,0.3);
            border-top-color: #0E0E1C;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* Forgot password modal */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.7);
            z-index: 100;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 32px;
            width: 100%;
            max-width: 380px;
        }
        .modal h3 { margin-bottom: 8px; }
        .modal p {
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 20px;
        }
        .reset-options {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 20px;
        }
        .reset-option {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px;
            cursor: pointer;
            transition: border-color 0.2s;
            text-align: left;
        }
        .reset-option:hover { border-color: var(--green); }
        .reset-option.selected { border-color: var(--green); }
        .reset-option h4 { font-size: 14px; margin-bottom: 4px; }
        .reset-option p { font-size: 12px; color: var(--muted); margin: 0; }
        .btn-cancel {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--muted);
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn-cancel:hover { border-color: var(--red); color: var(--red); }

        /* Verify screen */
        #verify-screen { display: none; }
        .code-info {
            background: rgba(56,189,248,0.1);
            border: 1px solid rgba(56,189,248,0.3);
            border-radius: 8px;
            padding: 14px;
            color: var(--blue);
            font-size: 13px;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        input.code-input {
            text-align: center;
            font-size: 28px;
            letter-spacing: 8px;
            font-weight: 700;
            color: var(--green);
        }
        .resend {
            text-align: center;
            margin-top: 12px;
        }
        .resend a {
            color: var(--muted);
            font-size: 13px;
            cursor: pointer;
            text-decoration: none;
        }
        .resend a:hover { color: var(--green); }
    </style>
</head>
<body>

<div class="logo">
    <a href="/">AVERION</a>
    <p>Intelligent DCA Trading</p>
</div>

<div class="card">

    <!-- Login Screen -->
    <div id="login-screen">
        <h2>Welcome back</h2>
        <p class="sub">Sign in to your Averion account</p>

        <div class="error" id="login-error"></div>

        <div class="form-group">
            <label>Email address</label>
            <input type="email" id="email"
                   placeholder="your@email.com"
                   autocomplete="email">
        </div>

        <div class="form-group">
            <label>Password</label>
            <input type="password" id="password"
                   placeholder="••••••••"
                   autocomplete="current-password">
        </div>

        <div class="forgot">
            <a onclick="openForgot()">Forgot password?</a>
        </div>

        <button class="btn btn-primary" id="login-btn"
                onclick="handleLogin()">
            Sign In
        </button>

        <div class="bottom-link">
            Don't have an account?
            <a href="/register">Create one free</a>
        </div>
    </div>

    <!-- Verify Screen -->
    <div id="verify-screen">
        <h2>Verify your identity</h2>
        <p class="sub">New device detected</p>

        <div class="code-info" id="verify-info">
            📱 A 6-digit code has been sent to your
            Telegram (@AverionBot).<br><br>
            Enter the code below to continue.
        </div>

        <div class="error" id="verify-error"></div>

        <div class="form-group">
            <label>Verification code</label>
            <input type="text" id="verify-code"
                   class="code-input"
                   placeholder="000000"
                   maxlength="6"
                   inputmode="numeric">
        </div>

        <button class="btn btn-primary" id="verify-btn"
                onclick="handleVerify()">
            Verify
        </button>

        <div class="resend">
            <a onclick="resendCode()">Resend code</a>
            &nbsp;·&nbsp;
            <a onclick="showLogin()">Back to login</a>
        </div>
    </div>

</div>

<!-- Forgot Password Modal -->
<div class="modal-overlay" id="forgot-modal">
    <div class="modal">
        <h3>Reset password</h3>
        <p>Choose how you want to receive your reset code</p>

        <div class="reset-options">
            <div class="reset-option selected"
                 id="opt-email"
                 onclick="selectReset('email')">
                <h4>📧 Email</h4>
                <p>Receive a reset link via email</p>
            </div>
            <div class="reset-option"
                 id="opt-telegram"
                 onclick="selectReset('telegram')">
                <h4>💬 Telegram</h4>
                <p>Receive a code via @AverionBot</p>
            </div>
        </div>

        <div class="form-group">
            <label>Email address</label>
            <input type="email" id="reset-email"
                   placeholder="your@email.com">
        </div>

        <div class="error" id="reset-error"></div>

        <button class="btn btn-primary"
                id="reset-btn"
                onclick="handleReset()"
                style="margin-bottom: 12px">
            Send Reset Code
        </button>
        <button class="btn-cancel" onclick="closeForgot()">
            Cancel
        </button>
    </div>
</div>

<script>
    const API = '';
    let pendingUserId = null;
    let resetMethod = 'email';
    let resetEmail = '';

    // ── SCREENS ──────────────────────────────────
    function showLogin() {
        document.getElementById('login-screen').style.display = 'block';
        document.getElementById('verify-screen').style.display = 'none';
    }

    function showVerify() {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('verify-screen').style.display = 'block';
    }

    function setBtn(id, loading, label) {
        const btn = document.getElementById(id);
        btn.disabled = loading;
        btn.innerHTML = loading
            ? `<span class="spinner"></span>${label}`
            : label;
    }

    function showError(id, msg) {
        const el = document.getElementById(id);
        el.textContent = msg;
        el.style.display = msg ? 'block' : 'none';
    }

    // ── LOGIN ─────────────────────────────────────
    async function handleLogin() {
        showError('login-error', '');
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!email || !password) {
            showError('login-error', 'Please enter email and password');
            return;
        }

        setBtn('login-btn', true, 'Signing in...');

        try {
            const res = await fetch(`${API}/auth/login`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            const data = await res.json();

            if (!res.ok) {
                showError('login-error', data.detail || 'Login failed');
                setBtn('login-btn', false, 'Sign In');
                return;
            }

            localStorage.setItem('averion_token', data.token);
            localStorage.setItem('averion_user_id', data.user_id);
            localStorage.setItem('averion_is_admin', data.is_admin);

            if (data.needs_verification) {
                pendingUserId = data.user_id;
                await fetch(`${API}/auth/send-code`, {
                    method: 'POST',
                    headers: {'Authorization': `Bearer ${data.token}`}
                });
                showVerify();
                setBtn('login-btn', false, 'Sign In');
            } else {
                window.location.href = '/dashboard';
            }

        } catch(e) {
            showError('login-error', 'Connection error · please try again');
            setBtn('login-btn', false, 'Sign In');
        }
    }

    // ── VERIFY ────────────────────────────────────
    async function handleVerify() {
        showError('verify-error', '');
        const code = document.getElementById('verify-code').value.trim();

        if (code.length !== 6) {
            showError('verify-error', 'Please enter the 6-digit code');
            return;
        }

        setBtn('verify-btn', true, 'Verifying...');

        try {
            const token = localStorage.getItem('averion_token');
            const res = await fetch(`${API}/auth/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    user_id: parseInt(pendingUserId), code
                })
            });
            const data = await res.json();

            if (!res.ok) {
                showError('verify-error', data.detail || 'Invalid code');
                setBtn('verify-btn', false, 'Verify');
                return;
            }

            window.location.href = '/dashboard';

        } catch(e) {
            showError('verify-error', 'Connection error');
            setBtn('verify-btn', false, 'Verify');
        }
    }

    async function resendCode() {
        const token = localStorage.getItem('averion_token');
        await fetch(`${API}/auth/send-code`, {
            method: 'POST',
            headers: {'Authorization': `Bearer ${token}`}
        });
        const info = document.getElementById('verify-info');
        info.style.color = '#10D98A';
        info.textContent = '✅ New code sent!';
        setTimeout(() => {
            info.style.color = '';
            info.innerHTML = '📱 A 6-digit code has been sent to your Telegram (@AverionBot).<br><br>Enter the code below to continue.';
        }, 3000);
    }

    // ── FORGOT PASSWORD ───────────────────────────
    function openForgot() {
        document.getElementById('forgot-modal').classList.add('active');
    }

    function closeForgot() {
        document.getElementById('forgot-modal').classList.remove('active');
        showError('reset-error', '');
    }

    function selectReset(method) {
        resetMethod = method;
        document.getElementById('opt-email').classList.toggle(
            'selected', method === 'email'
        );
        document.getElementById('opt-telegram').classList.toggle(
            'selected', method === 'telegram'
        );
    }

    async function handleReset() {
        showError('reset-error', '');
        const email = document.getElementById('reset-email').value.trim();

        if (!email) {
            showError('reset-error', 'Please enter your email');
            return;
        }

        setBtn('reset-btn', true, 'Sending...');

        try {
            const res = await fetch(`${API}/auth/reset-password`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, method: resetMethod})
            });
            const data = await res.json();

            if (!res.ok) {
                showError('reset-error', data.detail || 'Failed to send');
                setBtn('reset-btn', false, 'Send Reset Code');
                return;
            }

            resetEmail = email;
            closeForgot();
            document.getElementById('login-screen').style.display = 'none';
            document.getElementById('reset-confirm-screen').style.display = 'block';

        } catch(e) {
            showError('reset-error', 'Connection error');
            setBtn('reset-btn', false, 'Send Reset Code');
        }
    }

    // ── ENTER KEY ─────────────────────────────────
    document.addEventListener('keypress', e => {
        if (e.key !== 'Enter') return;
        if (document.getElementById('verify-screen').style.display !== 'none') {
            handleVerify();
        } else {
            handleLogin();
        }
    });

    // ── AUTO REDIRECT IF LOGGED IN ────────────────
    const token = localStorage.getItem('averion_token');
    if (token) {
        fetch(`${API}/status`, {
            headers: {'Authorization': `Bearer ${token}`}
        }).then(r => {
            if (r.ok) window.location.href = '/dashboard';
        }).catch(() => {});
    }

    async function handleResetConfirm() {
        const errorEl = document.getElementById('confirm-error');
        errorEl.style.display = 'none';
        const code = document.getElementById('confirm-code').value.trim();
        const newPwd = document.getElementById('new-password').value;
        const confirmPwd = document.getElementById('new-password-confirm').value;

        if (code.length !== 6) {
            errorEl.textContent = 'Please enter the 6-digit code';
            errorEl.style.display = 'block';
            return;
        }
        if (newPwd.length < 8) {
            errorEl.textContent = 'Password must be at least 8 characters';
            errorEl.style.display = 'block';
            return;
        }
        if (!/[A-Z]/.test(newPwd)) {
            errorEl.textContent = 'Password must contain uppercase letter';
            errorEl.style.display = 'block';
            return;
        }
        if (!/[0-9]/.test(newPwd)) {
            errorEl.textContent = 'Password must contain a number';
            errorEl.style.display = 'block';
            return;
        }
        if (!/[@$!%*#&]/.test(newPwd)) {
            errorEl.textContent = 'Password must contain special character (@$!%*#&)';
            errorEl.style.display = 'block';
            return;
        }
        if (newPwd !== confirmPwd) {
            errorEl.textContent = 'Passwords do not match';
            errorEl.style.display = 'block';
            return;
        }

        const btn = document.getElementById('confirm-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span>Resetting...';

        try {
            const res = await fetch(`${API}/auth/reset-password/confirm`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: resetEmail,
                    code: code,
                    new_password: newPwd
                })
            });
            const data = await res.json();

            if (!res.ok) {
                errorEl.textContent = data.detail || 'Reset failed';
                errorEl.style.display = 'block';
                btn.disabled = false;
                btn.textContent = 'Reset Password';
                return;
            }

            // Success · go to login
            document.getElementById('reset-confirm-screen').style.display = 'none';
            showLogin();
            const loginError = document.getElementById('login-error');
            loginError.style.display = 'block';
            loginError.style.background = 'rgba(16,217,138,0.1)';
            loginError.style.borderColor = 'rgba(16,217,138,0.3)';
            loginError.style.color = '#10D98A';
            loginError.textContent = '✅ Password reset successfully · please login';

        } catch(e) {
            errorEl.textContent = 'Connection error · please try again';
            errorEl.style.display = 'block';
            btn.disabled = false;
            btn.textContent = 'Reset Password';
        }
    }

</script>


<!-- Reset Confirm Screen -->
<div id="reset-confirm-screen" style="display:none">
    <div class="card" style="margin-top:20px">
        <h2>Enter reset code</h2>
        <p class="sub">Check your Telegram or email</p>

        <div class="error" id="confirm-error"></div>

        <div class="form-group">
            <label>6-digit code</label>
            <input type="text" id="confirm-code"
                   class="code-input"
                   placeholder="000000"
                   maxlength="6"
                   inputmode="numeric">
        </div>

        <div class="form-group">
            <label>New password</label>
            <input type="password" id="new-password"
                   placeholder="Min 8 chars · uppercase · number · special">
        </div>

        <div class="form-group">
            <label>Confirm new password</label>
            <input type="password" id="new-password-confirm"
                   placeholder="Repeat new password">
        </div>

        <button class="btn btn-primary" id="confirm-btn"
                onclick="handleResetConfirm()">
            Reset Password
        </button>

        <div class="resend" style="margin-top:12px">
            <a onclick="showLogin()">← Back to login</a>
        </div>
    </div>
</div>
</body>
</html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Averion — Create Account</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0E0E1C; --card: #16162A;
            --border: #2A2A45; --green: #10D98A;
            --blue: #38BDF8; --red: #F4645F;
            --text: #FFFFFF; --muted: #888888;
        }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .logo {
            text-align: center;
            margin-bottom: 32px;
        }
        .logo a {
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--green), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
            text-decoration: none;
        }
        .logo p { color: var(--muted); font-size: 13px; margin-top: 6px; }
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 36px;
            width: 100%;
            max-width: 420px;
        }
        .card h2 { font-size: 22px; margin-bottom: 6px; }
        .card .sub { color: var(--muted); font-size: 13px; margin-bottom: 28px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-size: 13px; color: #AAA; margin-bottom: 8px; }
        input {
            width: 100%;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 13px 16px;
            color: var(--text);
            font-size: 15px;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus { border-color: var(--green); }
        input::placeholder { color: #444; }
        .btn {
            width: 100%;
            padding: 14px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: opacity 0.2s;
            border: none;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--green), #0BB876);
            color: #0E0E1C;
        }
        .btn-primary:hover { opacity: 0.9; }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
        .error {
            background: rgba(244,100,95,0.1);
            border: 1px solid rgba(244,100,95,0.3);
            border-radius: 8px;
            padding: 12px;
            color: var(--red);
            font-size: 13px;
            margin-bottom: 16px;
            display: none;
        }
        .password-strength {
            margin-top: 8px;
            height: 4px;
            border-radius: 2px;
            background: var(--border);
            overflow: hidden;
        }
        .strength-bar {
            height: 100%;
            border-radius: 2px;
            transition: all 0.3s;
            width: 0%;
        }
        .strength-text {
            font-size: 11px;
            margin-top: 4px;
            color: var(--muted);
        }
        .benefits {
            background: rgba(16,217,138,0.05);
            border: 1px solid rgba(16,217,138,0.15);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 20px;
        }
        .benefits p {
            font-size: 12px;
            color: var(--muted);
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }
        .benefits p:last-child { margin-bottom: 0; }
        .benefits span { color: var(--green); }
        .terms {
            font-size: 12px;
            color: var(--muted);
            text-align: center;
            margin-top: 16px;
            line-height: 1.6;
        }
        .terms a { color: var(--green); text-decoration: none; }
        .bottom-link {
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: var(--muted);
        }
        .bottom-link a {
            color: var(--green);
            text-decoration: none;
            font-weight: 600;
        }
        .spinner {
            display: inline-block;
            width: 14px; height: 14px;
            border: 2px solid rgba(0,0,0,0.3);
            border-top-color: #0E0E1C;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .optional {
            color: #555;
            font-size: 11px;
            font-weight: normal;
            margin-left: 4px;
        }
    </style>
</head>
<body>

<div class="logo">
    <a href="/">AVERION</a>
    <p>Intelligent DCA Trading</p>
</div>

<div class="card">
    <h2>Create your account</h2>
    <p class="sub">Start trading smarter — free to join</p>

    <!-- Benefits -->
    <div class="benefits">
        <p><span>✓</span> 5 bots included free</p>
        <p><span>✓</span> 100 trades per month free</p>
        <p><span>✓</span> 20% fee only on winning trades</p>
        <p><span>✓</span> Paper trading — test risk-free</p>
    </div>

    <div class="error" id="reg-error"></div>

    <div class="form-group">
        <label>Email address</label>
        <input type="email" id="email"
               placeholder="your@email.com"
               autocomplete="email">
    </div>

    <div class="form-group">
        <label>Password</label>
        <input type="password" id="password"
               placeholder="Min 8 chars · uppercase · number · special"
               autocomplete="new-password"
               oninput="checkStrength(this.value)">
        <div class="password-strength">
            <div class="strength-bar" id="strength-bar"></div>
        </div>
        <div class="strength-text" id="strength-text"></div>
    </div>

    <div class="form-group">
        <label>Confirm password</label>
        <input type="password" id="confirm-password"
               placeholder="Repeat password"
               autocomplete="new-password">
    </div>

    <div class="form-group">
        <label>Referral code <span class="optional">(optional)</span></label>
        <input type="text" id="referral"
               placeholder="Enter referral code if you have one">
    </div>

    <button class="btn btn-primary" id="reg-btn"
            onclick="handleRegister()">
        Create Free Account
    </button>

    <p class="terms">
        By creating an account you agree that your funds
        stay on the exchange at all times. Averion never
        holds your assets.
    </p>

    <div class="bottom-link">
        Already have an account?
        <a href="/login">Sign in</a>
    </div>
</div>

<script>
    const API = '';

    function checkStrength(password) {
        const bar = document.getElementById('strength-bar');
        const text = document.getElementById('strength-text');
        let score = 0;
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;

        const colors = ['#F4645F','#FFA500','#FFA500','#10D98A','#10D98A'];
        const labels = ['Too short · add uppercase + number + special','Weak','Fair','Strong ✓','Very strong ✓'];
        const widths = ['20%','40%','60%','80%','100%'];

        if (password.length === 0) {
            bar.style.width = '0%';
            text.textContent = '';
            return;
        }

        const idx = Math.min(score, 4);
        bar.style.width = widths[idx];
        bar.style.background = colors[idx];
        text.textContent = labels[idx];
        text.style.color = colors[idx];
    }

    function showError(msg) {
        const el = document.getElementById('reg-error');
        el.textContent = msg;
        el.style.display = msg ? 'block' : 'none';
    }

    async function handleRegister() {
        showError('');
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirm-password').value;
        const referral = document.getElementById('referral').value.trim();

        if (!email || !password) {
            showError('Please fill in all required fields');
            return;
        }

        if (password.length < 8) {
            showError('Password must be at least 8 characters');
            return;
        }
        if (!/[A-Z]/.test(password)) {
            showError('Password must contain at least one uppercase letter');
            return;
        }
        if (!/[0-9]/.test(password)) {
            showError('Password must contain at least one number');
            return;
        }
        if (!/[@$!%*#&]/.test(password)) {
            showError('Password must contain at least one special character (@$!%*#&)');
            return;
        }

        if (password !== confirm) {
            showError('Passwords do not match');
            return;
        }

        const btn = document.getElementById('reg-btn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span>Creating account...';

        try {
            const res = await fetch(`${API}/auth/register`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email,
                    password,
                    referral_code: referral || null
                })
            });
            const data = await res.json();

            if (!res.ok) {
                showError(data.detail || 'Registration failed');
                btn.disabled = false;
                btn.textContent = 'Create Free Account';
                return;
            }

            localStorage.setItem('averion_token', data.token);
            localStorage.setItem('averion_user_id', data.user_id);
            window.location.href = '/dashboard';

        } catch(e) {
            showError('Connection error · please try again');
            btn.disabled = false;
            btn.textContent = 'Create Free Account';
        }
    }

    // Enter key
    document.addEventListener('keypress', e => {
        if (e.key === 'Enter') handleRegister();
    });

    // Auto redirect
    const token = localStorage.getItem('averion_token');
    if (token) {
        fetch(`${API}/status`, {
            headers: {'Authorization': `Bearer ${token}`}
        }).then(r => {
            if (r.ok) window.location.href = '/dashboard';
        }).catch(() => {});
    }
</script>

</body>
</html>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Averion — Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0E0E1C; --card: #16162A;
            --border: #2A2A45; --green: #10D98A;
            --blue: #38BDF8; --red: #F4645F;
            --amber: #FFA500; --text: #FFFFFF;
            --muted: #888888;
        }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
        }

        /* ── TOP BAR ── */
        .topbar {
            background: var(--card);
            border-bottom: 1px solid var(--border);
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .topbar-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .logo {
            font-size: 18px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--green), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
        }
        .admin-badge {
            background: rgba(244,100,95,0.15);
            border: 1px solid rgba(244,100,95,0.3);
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 11px;
            color: var(--red);
            font-weight: 600;
        }
        .bot-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }
        .status-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--muted);
        }
        .status-dot.online { background: var(--green); }
        .status-dot.offline { background: var(--red); }
        .topbar-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .btn-sm {
            padding: 7px 14px;
            border-radius: 7px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: opacity 0.2s;
        }
        .btn-danger {
            background: rgba(244,100,95,0.15);
            border: 1px solid rgba(244,100,95,0.3);
            color: var(--red);
        }
        .btn-danger:hover { background: rgba(244,100,95,0.25); }
        .btn-primary {
            background: linear-gradient(135deg, var(--green), #0BB876);
            color: #0E0E1C;
        }
        .btn-primary:hover { opacity: 0.9; }
        .btn-secondary {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--muted);
        }
        .btn-secondary:hover { border-color: var(--green); color: var(--green); }

        /* ── TABS ── */
        .tabs {
            background: var(--card);
            border-bottom: 1px solid var(--border);
            padding: 0 24px;
            display: flex;
            gap: 4px;
            overflow-x: auto;
        }
        .tab {
            padding: 14px 18px;
            font-size: 13px;
            font-weight: 600;
            color: var(--muted);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .tab:hover { color: var(--text); }
        .tab.active {
            color: var(--green);
            border-bottom-color: var(--green);
        }

        /* ── MAIN ── */
        .main {
            padding: 24px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* ── CARDS ── */
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
        }
        .card-title {
            font-size: 13px;
            font-weight: 700;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .grid-4 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
        }
        .stat-label {
            font-size: 12px;
            color: var(--muted);
            margin-bottom: 8px;
        }
        .stat-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--text);
        }
        .stat-value.green { color: var(--green); }
        .stat-value.red { color: var(--red); }
        .stat-value.blue { color: var(--blue); }

        /* ── SERVICES ── */
        .service-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }
        .service-row:last-child { border-bottom: none; }
        .service-name {
            font-size: 14px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .service-detail { font-size: 12px; color: var(--muted); }
        .badge {
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }
        .badge-green {
            background: rgba(16,217,138,0.15);
            color: var(--green);
        }
        .badge-red {
            background: rgba(244,100,95,0.15);
            color: var(--red);
        }
        .badge-amber {
            background: rgba(255,165,0,0.15);
            color: var(--amber);
        }
        .badge-blue {
            background: rgba(56,189,248,0.15);
            color: var(--blue);
        }

        /* ── CRON STEPS ── */
        .cron-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
        }
        .cron-step {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
        }
        .cron-step.success { border-color: rgba(16,217,138,0.3); }
        .cron-step.failed { border-color: rgba(244,100,95,0.3); }
        .cron-step.running { border-color: rgba(56,189,248,0.3); }
        .cron-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        .cron-name { font-size: 13px; font-weight: 700; }
        .cron-time { font-size: 11px; color: var(--muted); margin-bottom: 8px; }
        .cron-meta { font-size: 11px; color: var(--muted); }
        .cron-error {
            font-size: 11px;
            color: var(--red);
            background: rgba(244,100,95,0.1);
            border-radius: 6px;
            padding: 8px;
            margin-top: 8px;
            cursor: pointer;
        }
        .cron-actions {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }
        .btn-xs {
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            border: none;
        }
        .btn-rerun {
            background: rgba(16,217,138,0.15);
            color: var(--green);
            border: 1px solid rgba(16,217,138,0.3);
        }
        .btn-rerun:hover { background: rgba(16,217,138,0.25); }
        .btn-logs {
            background: rgba(56,189,248,0.15);
            color: var(--blue);
            border: 1px solid rgba(56,189,248,0.3);
        }
        .btn-copy {
            background: rgba(136,136,136,0.15);
            color: var(--muted);
            border: 1px solid var(--border);
        }

        /* ── PROGRESS BARS ── */
        .progress-bar {
            height: 6px;
            background: var(--border);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.5s;
        }

        /* ── TABLE ── */
        .table-wrap { overflow-x: auto; }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th {
            text-align: left;
            padding: 10px 12px;
            color: var(--muted);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border);
        }
        td {
            padding: 12px;
            border-bottom: 1px solid rgba(42,42,69,0.5);
            vertical-align: middle;
        }
        tr:hover td { background: rgba(255,255,255,0.02); }
        tr:last-child td { border-bottom: none; }

        /* ── TOGGLES ── */
        .toggle-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 0;
            border-bottom: 1px solid var(--border);
        }
        .toggle-row:last-child { border-bottom: none; }
        .toggle-info h4 { font-size: 14px; margin-bottom: 4px; }
        .toggle-info p { font-size: 12px; color: var(--muted); }
        .toggle {
            width: 44px; height: 24px;
            background: var(--border);
            border-radius: 12px;
            cursor: pointer;
            position: relative;
            transition: background 0.2s;
            border: none;
            flex-shrink: 0;
        }
        .toggle.on { background: var(--green); }
        .toggle::after {
            content: '';
            position: absolute;
            width: 18px; height: 18px;
            background: white;
            border-radius: 50%;
            top: 3px; left: 3px;
            transition: left 0.2s;
        }
        .toggle.on::after { left: 23px; }

        /* ── HEALTH BARS ── */
        .health-item {
            margin-bottom: 16px;
        }
        .health-header {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 6px;
        }
        .health-label { color: var(--muted); }

        /* ── ALERTS ── */
        .alerts-section {
            margin-bottom: 20px;
        }
        .alert-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 8px;
            font-size: 13px;
        }
        .alert-red {
            background: rgba(244,100,95,0.1);
            border: 1px solid rgba(244,100,95,0.2);
        }
        .alert-amber {
            background: rgba(255,165,0,0.1);
            border: 1px solid rgba(255,165,0,0.2);
        }
        .alert-green {
            background: rgba(16,217,138,0.1);
            border: 1px solid rgba(16,217,138,0.2);
        }
        .alert-icon { font-size: 16px; }
        .alert-msg { flex: 1; }
        .alert-action {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: var(--text);
        }

        /* ── LOGS MODAL ── */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.8);
            z-index: 200;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            width: 100%;
            max-width: 700px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        .modal-header h3 { font-size: 16px; }
        .modal-close {
            background: none;
            border: none;
            color: var(--muted);
            font-size: 20px;
            cursor: pointer;
        }
        .log-content {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.6;
            overflow-y: auto;
            flex: 1;
            color: #AAA;
            white-space: pre-wrap;
        }
        .modal-actions {
            display: flex;
            gap: 10px;
            margin-top: 16px;
        }

        /* ── EMPTY STATE ── */
        .empty {
            text-align: center;
            padding: 40px;
            color: var(--muted);
            font-size: 14px;
        }

        /* ── REFRESH ── */
        .last-updated {
            font-size: 11px;
            color: var(--muted);
        }

        .spinner {
            display: inline-block;
            width: 12px; height: 12px;
            border: 2px solid rgba(255,255,255,0.2);
            border-top-color: var(--green);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
    <div class="topbar-left">
        <div class="logo">AVERION</div>
        <div class="admin-badge">ADMIN</div>
        <div class="bot-status">
            <div class="status-dot" id="bot-dot"></div>
            <span id="bot-status-text">Loading...</span>
        </div>
    </div>
    <div class="topbar-right">
        <span class="last-updated" id="last-updated"></span>
        <button class="btn-sm btn-danger" onclick="emergencyStop()">
            🔴 Stop All Trading
        </button>
        <button class="btn-sm btn-primary" onclick="restartBot()">
            🔄 Restart Bot
        </button>
        <button class="btn-sm btn-secondary" onclick="logout()">
            Sign Out
        </button>
    </div>
</div>

<!-- TABS -->
<div class="tabs">
    <div class="tab active" onclick="switchTab('health')">
        Health & Control
    </div>
    <div class="tab" onclick="switchTab('users')">Users</div>
    <div class="tab" onclick="switchTab('stats')">Platform Stats</div>
    <div class="tab" onclick="switchTab('categories')">Coin Categories</div>
    <div class="tab" onclick="switchTab('controls')">Controls</div>
</div>

<!-- MAIN -->
<div class="main">

    <!-- ── TAB 1: HEALTH & CONTROL ── -->
    <div class="tab-content active" id="tab-health">

        <!-- Active Alerts -->
        <div class="alerts-section" id="alerts-section">
            <div class="empty" style="padding:20px">
                ✅ All systems normal
            </div>
        </div>

        <!-- Yesterday Summary -->
        <div class="grid-4" style="margin-bottom:20px">
            <div class="stat-card">
                <div class="stat-label">Trades Closed Today</div>
                <div class="stat-value green" id="trades-today">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Bots</div>
                <div class="stat-value blue" id="active-bots">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Open Positions</div>
                <div class="stat-value" id="open-positions">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Owner Wallet</div>
                <div class="stat-value green" id="owner-wallet">—</div>
            </div>
        </div>

        <!-- Services -->
        <div class="grid-2">
            <div class="card">
                <div class="card-title">Services</div>
                <div class="service-row">
                    <div class="service-name">
                        <span>🗄️</span> PostgreSQL
                    </div>
                    <div style="text-align:right">
                        <div class="badge badge-green" id="pg-status">Checking...</div>
                        <div class="service-detail" id="pg-detail"></div>
                    </div>
                </div>
                <div class="service-row">
                    <div class="service-name">
                        <span>⚡</span> Redis
                    </div>
                    <div style="text-align:right">
                        <div class="badge badge-green" id="redis-status">Checking...</div>
                        <div class="service-detail" id="redis-detail"></div>
                    </div>
                </div>
                <div class="service-row">
                    <div class="service-name">
                        <span>🤖</span> Bot Loop
                    </div>
                    <div style="text-align:right">
                        <div class="badge" id="bot-badge">Checking...</div>
                        <div class="service-detail" id="bot-detail"></div>
                    </div>
                </div>
                <div class="service-row">
                    <div class="service-name">
                        <span>🔄</span> Last Cycle
                    </div>
                    <div style="text-align:right">
                        <div class="service-detail" id="last-cycle"></div>
                    </div>
                </div>
            </div>

            <!-- Server Health -->
            <div class="card">
                <div class="card-title">
                    Server Health
                    <span class="last-updated" id="health-updated"></span>
                </div>
                <div class="health-item">
                    <div class="health-header">
                        <span class="health-label">CPU</span>
                        <span id="cpu-val">—</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="cpu-bar"
                             style="width:0%; background: var(--green)"></div>
                    </div>
                </div>
                <div class="health-item">
                    <div class="health-header">
                        <span class="health-label">RAM</span>
                        <span id="ram-val">—</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="ram-bar"
                             style="width:0%; background: var(--blue)"></div>
                    </div>
                </div>
                <div class="health-item">
                    <div class="health-header">
                        <span class="health-label">Disk</span>
                        <span id="disk-val">—</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="disk-bar"
                             style="width:0%; background: var(--amber)"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Cron Steps -->
        <div class="card">
            <div class="card-title">
                Daily Cron Status
                <button class="btn-xs btn-rerun" onclick="loadCronStatus()">
                    ↻ Refresh
                </button>
            </div>
            <div class="cron-grid" id="cron-grid">
                <div class="empty">Loading cron status...</div>
            </div>
        </div>
    </div>

    <!-- ── TAB 2: USERS ── -->
    <div class="tab-content" id="tab-users">
        <div class="card">
            <div class="card-title">
                All Users
                <input type="text" id="user-search"
                       placeholder="Search email..."
                       style="background:var(--bg);border:1px solid var(--border);
                              border-radius:8px;padding:6px 12px;color:var(--text);
                              font-size:13px;outline:none;width:200px"
                       oninput="filterUsers()">
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Email</th>
                            <th>Bots</th>
                            <th>Open Trades</th>
                            <th>Reserve</th>
                            <th>Fee Debt</th>
                            <th>Telegram</th>
                            <th>Status</th>
                            <th>Joined</th>
                        </tr>
                    </thead>
                    <tbody id="users-table">
                        <tr><td colspan="9" class="empty">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- ── TAB 3: PLATFORM STATS ── -->
    <div class="tab-content" id="tab-stats">
        <div class="grid-4">
            <div class="stat-card">
                <div class="stat-label">Total Users</div>
                <div class="stat-value blue" id="stat-users">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Bots</div>
                <div class="stat-value" id="stat-bots">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Open Positions</div>
                <div class="stat-value" id="stat-positions">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Live Positions</div>
                <div class="stat-value green" id="stat-live">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Paper Positions</div>
                <div class="stat-value blue" id="stat-paper">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Reserve</div>
                <div class="stat-value green" id="stat-reserve">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Owner Wallet</div>
                <div class="stat-value green" id="stat-owner">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Trades Today</div>
                <div class="stat-value" id="stat-trades">—</div>
            </div>
        </div>

        <!-- Diagnostics -->
        <div class="card" style="margin-top:20px">
            <div class="card-title">
                Diagnostics Report
                <div style="display:flex;gap:8px">
                    <button class="btn-xs btn-rerun"
                            onclick="copyDiagnostics()">
                        📋 Copy Markdown
                    </button>
                    <button class="btn-xs btn-logs"
                            onclick="generateDiagnostics()">
                        🔄 Regenerate
                    </button>
                </div>
            </div>
            <div class="log-content" id="diagnostics-content"
                 style="max-height:400px">
                Loading diagnostics...
            </div>
        </div>
    </div>

    <!-- ── TAB 4: COIN CATEGORIES ── -->
    <div class="tab-content" id="tab-categories">
        <div class="card">
            <div class="card-title">Market Cap Categories</div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Market Cap Range</th>
                            <th>DCA %</th>
                            <th>Spacing Mult</th>
                            <th>Size Mult</th>
                            <th>TP %</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="badge badge-blue">Mega Cap</span></td>
                            <td>> $100B</td>
                            <td>2%</td>
                            <td>1.2x</td>
                            <td>1.2x</td>
                            <td>2%</td>
                        </tr>
                        <tr>
                            <td><span class="badge badge-green">Large Cap</span></td>
                            <td>$10B - $100B</td>
                            <td>4%</td>
                            <td>1.3x</td>
                            <td>1.3x</td>
                            <td>3%</td>
                        </tr>
                        <tr>
                            <td><span class="badge" style="background:rgba(255,165,0,0.15);color:var(--amber)">Mid Cap</span></td>
                            <td>$1B - $10B</td>
                            <td>6%</td>
                            <td>1.4x</td>
                            <td>1.4x</td>
                            <td>4%</td>
                        </tr>
                        <tr>
                            <td><span class="badge badge-amber">Small Cap</span></td>
                            <td>$100M - $1B</td>
                            <td>8%</td>
                            <td>1.5x</td>
                            <td>1.5x</td>
                            <td>5%</td>
                        </tr>
                        <tr>
                            <td><span class="badge badge-red">Micro Cap</span></td>
                            <td>< $100M</td>
                            <td>10%</td>
                            <td>1.6x</td>
                            <td>1.6x</td>
                            <td>6%</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <p style="color:var(--muted);font-size:12px;margin-top:12px">
                ℹ️ Category parameters are set by the Smart DCA engine.
                Updated daily at 04:30 after classification.
            </p>
        </div>
    </div>

    <!-- ── TAB 5: CONTROLS ── -->
    <div class="tab-content" id="tab-controls">
        <div class="grid-2">
            <div class="card">
                <div class="card-title">Component Toggles</div>
                <div class="toggle-row">
                    <div class="toggle-info">
                        <h4>CoinGecko Integration</h4>
                        <p>Fetch market caps daily at 03:30</p>
                    </div>
                    <button class="toggle on" id="tog-coingecko"
                            onclick="toggleComponent(this, 'coingecko')"></button>
                </div>
                <div class="toggle-row">
                    <div class="toggle-info">
                        <h4>CoinMarketCap Integration</h4>
                        <p>Fetch market caps daily at 04:00</p>
                    </div>
                    <button class="toggle on" id="tog-cmc"
                            onclick="toggleComponent(this, 'cmc')"></button>
                </div>
                <div class="toggle-row">
                    <div class="toggle-info">
                        <h4>Telegram Notifications</h4>
                        <p>Send alerts and reports to users</p>
                    </div>
                    <button class="toggle on" id="tog-telegram"
                            onclick="toggleComponent(this, 'telegram')"></button>
                </div>
                <div class="toggle-row">
                    <div class="toggle-info">
                        <h4>Excel Report Generation</h4>
                        <p>Generate daily Excel reports at 05:00</p>
                    </div>
                    <button class="toggle on" id="tog-excel"
                            onclick="toggleComponent(this, 'excel')"></button>
                </div>
                <div class="toggle-row">
                    <div class="toggle-info">
                        <h4>CCXT Auto-Upgrade</h4>
                        <p>Safe upgrade at 03:00 daily</p>
                    </div>
                    <button class="toggle on" id="tog-ccxt"
                            onclick="toggleComponent(this, 'ccxt')"></button>
                </div>
                <div class="toggle-row">
                    <div class="toggle-info">
                        <h4>New User Registration</h4>
                        <p>Allow new accounts to be created</p>
                    </div>
                    <button class="toggle on" id="tog-registration"
                            onclick="toggleComponent(this, 'registration')"></button>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Emergency Controls</div>
                <div style="display:flex;flex-direction:column;gap:12px">
                    <button class="btn-sm btn-danger"
                            style="padding:14px;font-size:14px"
                            onclick="emergencyStop()">
                        🔴 Stop All Live Trading
                    </button>
                    <button class="btn-sm"
                            style="padding:14px;font-size:14px;
                                   background:rgba(255,165,0,0.15);
                                   border:1px solid rgba(255,165,0,0.3);
                                   color:var(--amber)"
                            onclick="pauseNewPositions()">
                        ⏸️ Pause New Positions Only
                    </button>
                    <button class="btn-sm btn-primary"
                            style="padding:14px;font-size:14px"
                            onclick="restartBot()">
                        🔄 Restart Bot
                    </button>
                    <button class="btn-sm btn-secondary"
                            style="padding:14px;font-size:14px"
                            onclick="forceReconciliation()">
                        🔁 Force Reconciliation
                    </button>
                </div>

                <div class="card-title" style="margin-top:24px">
                    Backup Status
                </div>
                <div id="backup-info" style="color:var(--muted);font-size:13px">
                    Loading...
                </div>
            </div>
        </div>
    </div>

</div>

<!-- LOGS MODAL -->
<div class="modal-overlay" id="logs-modal">
    <div class="modal">
        <div class="modal-header">
            <h3 id="modal-title">Logs</h3>
            <button class="modal-close" onclick="closeLogs()">✕</button>
        </div>
        <div class="log-content" id="modal-log-content">
            No logs available
        </div>
        <div class="modal-actions">
            <button class="btn-xs btn-rerun" onclick="copyLog()">
                📋 Copy
            </button>
            <button class="btn-xs btn-secondary btn-sm"
                    onclick="closeLogs()">
                Close
            </button>
        </div>
    </div>
</div>

<script>
    const API = '';
    const TOKEN = localStorage.getItem('averion_token');
    let allUsers = [];
    let cronData = {};

    function headers() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${TOKEN}`
        };
    }

    // ── AUTH CHECK ────────────────────────────────
    if (!TOKEN) window.location.href = '/login';

    // ── TABS ─────────────────────────────────────
    function switchTab(name) {
        document.querySelectorAll('.tab').forEach((t, i) => {
            t.classList.toggle('active',
                t.textContent.toLowerCase().includes(name) ||
                (name === 'health' && i === 0) ||
                (name === 'users' && i === 1) ||
                (name === 'stats' && i === 2) ||
                (name === 'categories' && i === 3) ||
                (name === 'controls' && i === 4)
            );
        });
        document.querySelectorAll('.tab-content').forEach(c => {
            c.classList.remove('active');
        });
        document.getElementById(`tab-${name}`).classList.add('active');

        if (name === 'users') loadUsers();
        if (name === 'stats') loadStats();
        if (name === 'controls') loadDiagnostics();
    }

    // ── STATUS ────────────────────────────────────
    async function loadStatus() {
        try {
            const res = await fetch(`${API}/status`,
                { headers: headers() });
            const data = await res.json();

            const dot = document.getElementById('bot-dot');
            const text = document.getElementById('bot-status-text');
            const badge = document.getElementById('bot-badge');
            const detail = document.getElementById('bot-detail');

            if (data.running) {
                dot.className = 'status-dot online';
                text.textContent = `BOT RUNNING · ${data.cycle_time}s`;
                badge.className = 'badge badge-green';
                badge.textContent = 'Running';
            } else {
                dot.className = 'status-dot offline';
                text.textContent = 'BOT STOPPED';
                badge.className = 'badge badge-red';
                badge.textContent = 'Stopped';
            }
            detail.textContent = `Last: ${data.last_cycle || 'never'}`;

            document.getElementById('last-updated').textContent =
                `Updated: ${new Date().toLocaleTimeString()}`;

        } catch(e) {
            document.getElementById('bot-status-text').textContent = 'Connection error';
        }
    }

    // ── ADMIN STATS ───────────────────────────────
    async function loadAdminStats() {
        try {
            const res = await fetch(`${API}/admin/stats`,
                { headers: headers() });
            if (res.status === 401 || res.status === 403) {
                window.location.href = '/login';
                return;
            }
            const data = await res.json();

            document.getElementById('trades-today').textContent =
                data.trades_today || 0;
            document.getElementById('active-bots').textContent =
                data.active_bots || 0;
            document.getElementById('open-positions').textContent =
                data.open_positions || 0;
            document.getElementById('owner-wallet').textContent =
                `$${(data.owner_wallet || 0).toFixed(2)}`;

        } catch(e) { console.error(e); }
    }

    // ── HEALTH ────────────────────────────────────
    async function loadHealth() {
        try {
            const res = await fetch(`${API}/admin/health`,
                { headers: headers() });
            const rows = await res.json();
            if (!rows.length) return;

            const latest = rows[rows.length - 1];
            const cpu = latest.cpu || 0;
            const ram = latest.ram || 0;
            const disk = latest.disk || 0;

            document.getElementById('cpu-val').textContent = `${cpu}%`;
            document.getElementById('ram-val').textContent = `${ram}%`;
            document.getElementById('disk-val').textContent = `${disk}%`;

            const cpuBar = document.getElementById('cpu-bar');
            cpuBar.style.width = `${cpu}%`;
            cpuBar.style.background = cpu > 80 ? 'var(--red)' :
                cpu > 60 ? 'var(--amber)' : 'var(--green)';

            const ramBar = document.getElementById('ram-bar');
            ramBar.style.width = `${ram}%`;
            ramBar.style.background = ram > 80 ? 'var(--red)' :
                ram > 60 ? 'var(--amber)' : 'var(--blue)';

            const diskBar = document.getElementById('disk-bar');
            diskBar.style.width = `${disk}%`;
            diskBar.style.background = disk > 70 ? 'var(--red)' :
                disk > 50 ? 'var(--amber)' : 'var(--amber)';

            document.getElementById('health-updated').textContent =
                new Date(latest.recorded_at).toLocaleTimeString();

        } catch(e) { console.error(e); }
    }

    // ── CRON STATUS ───────────────────────────────
    async function loadCronStatus() {
        try {
            const res = await fetch(`${API}/admin/cron-status`,
                { headers: headers() });
            cronData = await res.json();

            const steps = [
                { key: 'infrastructure', name: 'Infrastructure', time: '03:00' },
                { key: 'coingecko', name: 'CoinGecko Fetch', time: '03:30' },
                { key: 'cmc', name: 'CMC Fetch', time: '04:00' },
                { key: 'classification', name: 'Classification', time: '04:30' },
                { key: 'reporting', name: 'Reporting', time: '05:00' },
                { key: 'cleanup', name: 'Sunday Cleanup', time: '05:30' },
            ];

            const grid = document.getElementById('cron-grid');
            grid.innerHTML = steps.map(step => {
                const d = cronData[step.key];
                const status = d ? d.status : null;
                const cls = status === 'success' ? 'success' :
                            status === 'failed' ? 'failed' :
                            status === 'running' ? 'running' : '';
                const badge = status === 'success' ?
                    '<span class="badge badge-green">✅ Complete</span>' :
                    status === 'failed' ?
                    '<span class="badge badge-red">❌ Failed</span>' :
                    status === 'running' ?
                    '<span class="badge badge-blue">⏳ Running</span>' :
                    '<span class="badge" style="background:rgba(136,136,136,0.1);color:var(--muted)">— Pending</span>';

                return `
                <div class="cron-step ${cls}">
                    <div class="cron-header">
                        <span class="cron-name">${step.time} · ${step.name}</span>
                        ${badge}
                    </div>
                    ${d ? `
                    <div class="cron-time">
                        Duration: ${d.duration?.toFixed(1)}s ·
                        Records: ${d.records || 0}
                    </div>` : ''}
                    ${d?.error ? `
                    <div class="cron-error" onclick="showLog('${step.name}', \`${d.error}\`)">
                        ❌ ${d.error.substring(0, 80)}...
                        <br><small>Click to view full error</small>
                    </div>` : ''}
                    <div class="cron-actions">
                        <button class="btn-xs btn-rerun"
                                onclick="rerunStep('${step.key}')">
                            ↻ Re-run
                        </button>
                        ${d?.error ? `
                        <button class="btn-xs btn-logs"
                                onclick="showLog('${step.name}', \`${d.error}\`)">
                            📋 Logs
                        </button>
                        <button class="btn-xs btn-copy"
                                onclick="copyText(\`${d.error}\`)">
                            Copy
                        </button>` : ''}
                    </div>
                </div>`;
            }).join('');

        } catch(e) {
            document.getElementById('cron-grid').innerHTML =
                '<div class="empty">Failed to load cron status</div>';
        }
    }

    async function rerunStep(step) {
        try {
            await fetch(`${API}/admin/cron/${step}/run`, {
                method: 'POST',
                headers: headers()
            });
            setTimeout(loadCronStatus, 2000);
        } catch(e) { alert('Failed to start step'); }
    }

    // ── USERS ─────────────────────────────────────
    async function loadUsers() {
        try {
            const res = await fetch(`${API}/admin/users`,
                { headers: headers() });
            allUsers = await res.json();
            renderUsers(allUsers);
        } catch(e) {
            document.getElementById('users-table').innerHTML =
                '<tr><td colspan="9" class="empty">Failed to load users</td></tr>';
        }
    }

    function renderUsers(users) {
        const tbody = document.getElementById('users-table');
        if (!users.length) {
            tbody.innerHTML = '<tr><td colspan="9" class="empty">No users yet</td></tr>';
            return;
        }
        tbody.innerHTML = users.map(u => `
            <tr>
                <td style="color:var(--muted)">#${u.id}</td>
                <td>${u.email}</td>
                <td>${u.bots || 0}</td>
                <td>${u.open_positions || 0}</td>
                <td style="color:var(--green)">$${(u.reserve || 0).toFixed(2)}</td>
                <td style="color:${u.fee_debt > 0 ? 'var(--red)' : 'var(--muted)'}">
                    ${u.fee_debt > 0 ? '-$' + u.fee_debt.toFixed(2) : '$0'}
                </td>
                <td>${u.telegram ?
                    '<span class="badge badge-green">✅</span>' :
                    '<span class="badge badge-red">❌</span>'}</td>
                <td>${u.suspended ?
                    '<span class="badge badge-red">Suspended</span>' :
                    '<span class="badge badge-green">Active</span>'}</td>
                <td style="color:var(--muted)">
                    ${new Date(u.created_at).toLocaleDateString()}
                </td>
            </tr>
        `).join('');
    }

    function filterUsers() {
        const q = document.getElementById('user-search').value.toLowerCase();
        renderUsers(allUsers.filter(u =>
            u.email.toLowerCase().includes(q)
        ));
    }

    // ── STATS ─────────────────────────────────────
    async function loadStats() {
        try {
            const res = await fetch(`${API}/admin/stats`,
                { headers: headers() });
            const data = await res.json();

            document.getElementById('stat-users').textContent = data.total_users || 0;
            document.getElementById('stat-bots').textContent = data.active_bots || 0;
            document.getElementById('stat-positions').textContent = data.open_positions || 0;
            document.getElementById('stat-live').textContent = data.live_positions || 0;
            document.getElementById('stat-paper').textContent = data.paper_positions || 0;
            document.getElementById('stat-reserve').textContent =
                `$${(data.total_reserve || 0).toFixed(2)}`;
            document.getElementById('stat-owner').textContent =
                `$${(data.owner_wallet || 0).toFixed(2)}`;
            document.getElementById('stat-trades').textContent = data.trades_today || 0;

        } catch(e) { console.error(e); }

        loadDiagnostics();
    }

    async function loadDiagnostics() {
        try {
            const res = await fetch(`${API}/admin/diagnostics`,
                { headers: headers() });
            const data = await res.json();
            document.getElementById('diagnostics-content').textContent =
                data.content || 'No diagnostics available';
        } catch(e) {
            document.getElementById('diagnostics-content').textContent =
                'Failed to load diagnostics';
        }
    }

    async function generateDiagnostics() {
        await fetch(`${API}/admin/diagnostics/generate`, {
            method: 'POST',
            headers: headers()
        });
        setTimeout(loadDiagnostics, 5000);
    }

    function copyDiagnostics() {
        const content = document.getElementById('diagnostics-content').textContent;
        navigator.clipboard.writeText(content);
        alert('✅ Copied to clipboard · paste to Claude for diagnosis');
    }

    // ── CONTROLS ──────────────────────────────────
    async function emergencyStop() {
        if (!confirm('🔴 Stop ALL live trading?\nThis will prevent new trades. Open positions continue.')) return;
        alert('Emergency stop sent · monitoring...');
    }

    async function pauseNewPositions() {
        if (!confirm('⏸️ Pause new positions only?\nOpen positions continue to TP.')) return;
        alert('New positions paused');
    }

    async function restartBot() {
        if (!confirm('🔄 Restart bot?')) return;
        await fetch(`${API}/admin/bot/restart`, {
            method: 'POST',
            headers: headers()
        });
        setTimeout(loadStatus, 3000);
    }

    async function forceReconciliation() {
        alert('Reconciliation started · check logs in 30 seconds');
    }

    function toggleComponent(btn, component) {
        btn.classList.toggle('on');
    }

    // ── LOGS MODAL ────────────────────────────────
    function showLog(title, content) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-log-content').textContent = content;
        document.getElementById('logs-modal').classList.add('active');
    }

    function closeLogs() {
        document.getElementById('logs-modal').classList.remove('active');
    }

    function copyLog() {
        const content = document.getElementById('modal-log-content').textContent;
        navigator.clipboard.writeText(content);
        alert('✅ Copied · paste to Claude for diagnosis');
    }

    function copyText(text) {
        navigator.clipboard.writeText(text);
        alert('✅ Copied');
    }

    function logout() {
        localStorage.clear();
        window.location.href = '/login';
    }

    // ── INIT ──────────────────────────────────────
    async function init() {
        await loadStatus();
        await loadAdminStats();
        await loadHealth();
        await loadCronStatus();
    }

    init();
    setInterval(loadStatus, 30000);
    setInterval(loadHealth, 60000);
    setInterval(loadCronStatus, 60000);
</script>

</body>
</html>
