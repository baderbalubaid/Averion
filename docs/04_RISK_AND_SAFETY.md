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
