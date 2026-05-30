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

- Bot sticks to user selected base order size — no auto-adjustment
- Before launching bot: system checks all coins against exchange minimums
- Shows warning in Step 7 wizard:
  "Coin X requires $5 minimum — will be skipped with your $1 base"
- User decides to increase base order or accept skipped coins
- Add Funds: blocks confirmation if amount < exchange minimum
- Short DCA: checks quantity >= minimum lot size before every sell
  - If holdings < minimum lot → skip level · show dashboard warning
  - User must increase holdings manually first

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
