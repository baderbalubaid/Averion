## Telegram & Email Notifications — Final (LOCKED)

---

## 1. Setup

ONE direct chat with @AverionBot
No separate channels ever.

Connection flow:
1. Settings → Notifications → [Connect Telegram]
2. Dashboard shows unique code: /connect ABC123XYZ
3. Customer opens Telegram → finds @AverionBot
4. Sends: /connect ABC123XYZ
5. Bot confirms connection
6. All notifications go to one direct chat

Customer can mute bot in Telegram directly if needed.
50 max queued if Telegram down · sends when recovered.

---

## 2. Notification Types

### 🟢 TRADE (toggle ON/OFF)
High volume · many users mute this.
Covers BOTH Long and Short equally.
Only label differs (LONG · SHORT).
Profit shown in $ or coin based on bot profit currency setting.

Trade Opened:
🟢 TRADE OPENED
BTC/USDT · MEXC · LONG
Entry: $67,200 · Size: $100
Method: Smart DCA · Bot: My BTC Bot

DCA fired (Long):
🟢 DCA #2
BTC/USDT · MEXC · LONG
Price: $65,000 · Added: $120
Avg cost: $66,100 · Bot: My BTC Bot

Sell fired (Short):
🟢 SELL #2
BTC/USDT · MEXC · SHORT
Price: $69,000 · Sold: 0.002 BTC
Avg sell: $68,100 · Bot: My BTC Bot

Trade Closed with profit in USDT:
🟢 TRADE CLOSED ✅
BTC/USDT · MEXC · LONG
Profit: +$47.20 (+4.2%)
DCAs used: 2 · Hold: 8 days
Fee: $9.44 · Net: +$37.76

Trade Closed with profit in coin:
🟢 TRADE CLOSED ✅
BTC/USDT · MEXC · SHORT
Profit: +0.0007 BTC (+4.2%)
Sells used: 2 · Hold: 8 days
Fee: $9.44 · Net: +0.00056 BTC

Trade Closed with loss:
🔴 TRADE CLOSED ❌
BTC/USDT · MEXC · LONG
Loss: -$12.30 (-1.8%)
DCAs used: 4 · Hold: 22 days
Fee: $0 · Net: -$12.30

---

### 🔴 ALERT (recommended always ON)
One alert per event · never repeated · never annoying.

Reserve low:
🔴 RESERVE LOW
Balance: $5.20 (below threshold)
Bots may pause soon
[Top Up Now]

Reserve empty:
🔴 RESERVE EMPTY
All bots paused · no new trades
[Top Up Now]

Fee debt created:
🔴 FEE DEBT: -$12.30
Reserve insufficient to cover fee
Please top up to resume trading
[Top Up Now]

Deposit confirmed:
🟢 DEPOSIT CONFIRMED
Amount: +$50.00 USDT
Fee debt cleared: $12.30 ✅
Reserve balance: $37.70

API key expiring:
🟡 API KEY EXPIRING
Exchange: Binance
Expires in: 3 days · Please update
[Update Now]

API key invalid:
🔴 API KEY INVALID
Exchange: MEXC
Key rejected · Exchange paused
[Update Key]

ST flag detected:
🔴 ST FLAG DETECTED
Coin: RVN/USDT · MEXC
Position sold immediately
P&L: -$2.30

Bot paused (reserve floor):
🟡 BOT PAUSED
Bot: My BTC Bot
Reserve below floor ($45 < $50)
Resume at: $75

Bot auto-resumed:
🟢 BOT RESUMED
Bot: My BTC Bot
Reserve: $80.00 ✅

Bot subscription expiring:
🟡 BOT EXPIRING SOON
Bot: My BTC Bot · Expires: 3 days
[Renew Now]

Bot subscription expired:
🔴 BOT EXPIRED
Bot: My BTC Bot · Trading paused
[Renew Now]

DCA checkpoint reached:
🟡 DCA CHECKPOINT
BTC/USDT · MEXC · LONG
Max DCA levels reached
[Continue] [Pause] [Sell Now]

Dead coin detected:
🔴 DEAD COIN DETECTED
Coin: XYZ/USDT · MEXC
Position locked · manual review needed
[View Position]

---

### 🟢 INCOME (toggle ON/OFF)

Referral income earned:
🟢 REFERRAL INCOME 🎉
Your friend made a profitable trade!
You earned: +$2.40
Total referral income: $24.80
Reserve balance: $52.40

---

### 📊 REPORT (toggle ON/OFF)

Daily report:
📊 DAILY REPORT · June 3
Closed trades: 3 · Profit: +$47.20
Fees: $9.44 · Net: +$37.76
Open positions: 23

Weekly report:
📊 WEEKLY REPORT · Week 23
Closed: 18 · Profit: +$234.50
Win rate: 72% · Best: BTC +$87.20
Fees: $46.90 · Net: +$187.60

Monthly report:
📊 MONTHLY REPORT · June 2026
Closed: 67 · Profit: +$890.20
Win rate: 69% · Fees: $178.04
Net profit: +$712.16

---

### 📧 EMAIL (toggle ON/OFF)
For important alerts only · not every trade.

New device login (security):
Subject: New login to your Averion account
Someone logged in from: IP · Device · Location
If this was you: ignore this email
If not you: [Secure My Account]

API key invalid (urgent copy of Telegram alert):
Subject: Action required · API key issue
Exchange: MEXC · Key rejected
Please update your API key to resume trading

Deposit receipt:
Subject: Deposit confirmed · Averion
Amount: $50.00 USDT received
New reserve balance: $37.70
Thank you for topping up!

Weekly report (email version):
Subject: Your Averion weekly summary · Week 23
[Same content as Telegram weekly report]

Monthly report (email version):
Subject: Your Averion monthly summary · June 2026
[Same content as Telegram monthly report]

---

## 3. Settings Tab Controls

TELEGRAM:
Status: @AverionBot ✅ [Disconnect]
Or: [Connect Telegram] if not connected

TRADE NOTIFICATIONS (high volume):
Trade opened:          [ON/OFF]
DCA / Sell fired:      [ON/OFF]
Trade closed:          [ON/OFF]

SYSTEM ALERTS (recommended ON):
Reserve low:           [ON ●]
Reserve empty:         [ON ●]
Fee debt:              [ON ●]
Deposit confirmed:     [ON/OFF]
API key expiring:      [ON ●]
API key invalid:       [ON ●]
ST flag detected:      [ON ●]
Bot paused/resumed:    [ON/OFF]
Bot expiring:          [ON ●]
DCA checkpoint:        [ON ●]
Dead coin:             [ON ●]

INCOME:
Referral income:       [ON/OFF]

REPORTS:
Daily report:          [ON/OFF]
Weekly report:         [ON/OFF]
Monthly report:        [ON/OFF]

EMAIL:
Email: user@email.com ✅
Security alerts:       [ON ●]
API key invalid:       [ON ●]
Deposit receipt:       [ON/OFF]
Weekly report:         [ON/OFF]
Monthly report:        [ON/OFF]

---

## 4. Rules (LOCKED)

- ONE Telegram chat only · forever
- Long and Short = same notification format
- Only LONG/SHORT label differs
- Profit in $ or coin based on bot profit currency setting
- Recommended alerts shown with ● and cannot be easily disabled
- Customer can mute bot in Telegram directly
- One alert per event · never repeated
- 50 max queued if Telegram down · sends when recovered
- All controls in Settings tab only · nowhere else
- Email for important/infrequent alerts only
- Never spam customer · quality over quantity

---

## ADMIN TELEGRAM NOTIFICATIONS (LOCKED)

Admin has 3 separate Telegram channels.
Each channel has specific purpose.
Never mix urgent alerts with routine info.

---

## Channel 1 — Alerts (Urgent · Needs Action)

Everything here requires immediate attention.

User reserve empty:
🔴 RESERVE EMPTY
User #5 · user@email.com
All bots paused · no new trades
Outstanding fees: $12.30

User API key rejected:
🔴 API KEY REJECTED
User #3 · MEXC exchange
Bot paused · user notified
[View User]

ST flag detected:
🔴 ST FLAG
Coin: RVN/USDT · User #7 · MEXC
Position sold immediately
P&L: -$2.30 · User notified

Bot crashed:
🔴 BOT CRASHED
Error: [error message]
Auto-restarted at 14:23
[View Logs]

Failed DB backup:
🔴 BACKUP FAILED
Time: 03:00 · Size: N/A
Manual action required
[Check Server]

Exchange API down:
🔴 EXCHANGE DOWN
MEXC API · 5 consecutive failures
All MEXC bots paused
Retrying with backoff

Dead coin detected:
🔴 DEAD COIN
Coin: XYZ/USDT · User #12
Position locked · user notified
[View Position]

Security — failed login attempts:
🔴 SECURITY ALERT
5 failed admin login attempts
IP: 192.168.x.x blocked
[Check Access Log]

Payment webhook failed:
🔴 WEBHOOK FAILED
NOWPayments webhook missed
User #8 · $50 payment
Manual verification needed
[Check NOWPayments]

Short buyback missing:
🔴 BUYBACK MISSING
User #4 · BTC/USDT · MEXC
Limit order not found on exchange
Auto-recovery triggered

Bear circuit breaker fired:
🔴 CIRCUIT BREAKER
Bear champion: E6-2
Max drawdown > 40% in 30 days
Emergency switch: E7-3
[View Research]

All methods distressed:
🔴 ALL METHODS DISTRESSED
All bear methods > 40% drawdown
No qualified replacement
Manual review required
E10 retained as champion

Research champion switched:
🟢 CHAMPION SWITCHED
Regime: Bull
E10-1 → E11-3
RARS: 0.745 vs 0.621 (+20%)
Tier 1 · 4 weeks · 47 trades
[View Report]

---

## Channel 2 — Activity (Info · No Action Needed)

Routine platform activity.

New user registered:
👤 NEW USER
Email: user@email.com
Referral: ABC123 (User #3)
Plan: Free

User topped up reserve:
💰 DEPOSIT
User #5 · $50.00 USDT
Debt cleared: $12.30 ✅
New reserve: $37.70

Fee collected (over $50):
💵 FEE COLLECTED
User #7 · $87.40
Trade: BTC/USDT · LONG +$437
Owner wallet: $4,317

Owner wallet transfer:
💳 TRANSFER COMPLETE
Amount: $2,341.20
To: TRC20 wallet
Owner wallet: $0.00

Referral payout:
🤝 REFERRAL PAID
User #3 earned: $2.40
From: User #12 trade
User #3 total referrals: $24.80

New bot created:
🤖 NEW BOT
User #5 · BTC/USDT · Binance
Method: Smart DCA · Long
Trade limit: 10

Coin reclassified:
📊 RECLASSIFICATION
Coin: LINK/USDT
Mid Cap → Large Cap
$8.2B → $11.4B market cap
3 users affected · new positions only

Research challenger detected:
📊 CHALLENGER DETECTED
Regime: Bull
E13-5 beating E11-3
Week 1 of 4 · RARS +0.043 ahead
Monitoring...

Research report ready:
📊 WEEK 12 RESEARCH REPORT
Bull: E11-3 (no change) ⭐
Bear: E6-2 (no change) ⭐
Sideways: E1-1 (no change) ⭐
Challenger: E13-5 week 2/4
[Download Report URL]

Paper timer auto-closed:
📄 PAPER TIMER
User #9 · paper trades closed
No live trades in 90 days
User notified

---

## Channel 3 — System (Technical · Server)

Daily cron · server health · updates.

Daily cron summary (every morning):
📊 DAILY CRON · June 3 2026

CRON STEPS:
03:00 CoinGecko ✅ 312 coins · 0.8s
03:30 CMC       ✅ 312 coins · 1.2s
04:00 OHLCV     ❌ Failed coin 87 [Re-run]
04:30 Classify  ✅ 3 reclassified
05:00 Research  ✅ Week 12 done

PLATFORM:
Users: 47 | New today: 2
Open positions: 1,847
Trades closed: 234
Fees collected: $456.20

SERVER:
CPU avg: 23% | RAM: 1.8GB/4GB
Loop avg: 1.8s | Uptime: 14d 3h
DB size: 284MB

ALERTS TODAY: 2
→ User #3 API key rejected
→ User #7 reserve low

CCXT: 4.5.57 ✅

Server health threshold crossed:
🔴 SERVER ALERT
CPU: 84% (threshold: 80%)
Current positions: 2,300
Consider upgrading to CX33

Server back to normal:
🟢 SERVER NORMAL
CPU: 31% · RAM: 1.9GB/4GB
Loop avg: 2.1s

Bot started (after restart):
🟢 BOT STARTED
PostgreSQL ✅ Redis ✅
Nginx ✅ PM2 ✅
Paper mode: OFF
Cycle 1: 1.2s ✅

CCXT upgrade result (pass):
🟢 CCXT UPGRADED
4.5.56 → 4.5.57
All 5 tests passed ✅
Bot restarted · running normally

CCXT upgrade result (fail):
🟡 CCXT UPGRADE SKIPPED
Test failed: fetch_balance
Staying on 4.5.56
Will retry next Sunday

Fernet key rotation:
🔐 FERNET KEY ROTATED
47 exchange keys re-encrypted
Part A: .env updated
Part B: Hetzner Secrets updated
Next rotation: July 1

DB backup complete:
✅ BACKUP COMPLETE
Size: 284MB · 03:00
Location: /backups/2026-06-03.sql.gz

DB backup failed:
🔴 BACKUP FAILED
Time: 03:00
Error: disk space low
Manual action required

---

## Admin Telegram Rules (LOCKED)

- 3 separate channels · never mix types
- Channel 1: urgent only · check immediately
- Channel 2: FYI · check when convenient
- Channel 3: technical · check daily
- Daily cron summary always sent to Channel 3
- Server health alerts → Channel 1 if critical
- Server health updates → Channel 3 if routine
- All research alerts → Channel 1 if action needed
- All research info → Channel 2 if informational
- No spam · every message has purpose
- [Copy as Markdown] button in Health tab for AI sharing
