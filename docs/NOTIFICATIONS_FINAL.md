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
