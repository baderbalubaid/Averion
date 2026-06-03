## Customer Dashboard — Final Design (LOCKED)

### Design Philosophy
- Mobile first · fits one phone screen
- Same tab structure as admin (familiar · consistent)
- Large tap targets · no tiny buttons
- Dark theme · clean · minimal

---

### TOP BAR (always visible)
Open: 23 | Profit Today: +$47.20 | Reserve: $50.00
[🔔 Alerts badge if any]

---

### TAB 1 — Dashboard (Home)

ALERTS SECTION (only when needed):
🔴 Reserve wallet empty · bots paused [Top Up]
🟡 Bot paused · fee debt $12.30 [View]
🟡 API key expiring in 3 days [Fix]
Empty = "✅ All systems normal"

4 QUICK STAT CARDS:
| Open Positions | Profit Today | Fees Today | Reserve |
|----------------|--------------|------------|---------|
| 23 | +$47.20 | $9.44 | $50.00 |

EXCHANGE OVERVIEW (one row per exchange):
Exchange | Capital | Bots | Open | P&L$ | P&L%
MEXC     | $234.50 | 3    | 12   | +$47 | +4.2%
KuCoin   | $567.20 | 5    | 11   | +$23 | +2.1%
Total    | $801.70 | 8    | 23   | +$70 | +3.2%

Tap exchange row → goes to Bots tab filtered by exchange

RECENT ACTIVITY (last 5 closed):
Coin · Profit · Time ago · Result
RVN  · +$4.20  · 2h ago  · ✅
BTC  · +$12.50 · 5h ago  · ✅
ETH  · -$2.10  · 8h ago  · ❌
Tap any → opens position detail

---

### TAB 2 — Bots

Sub-navigation: [Bots & Queue] [History]

─── BOTS & QUEUE ───

FILTER BAR:
[All] [Running] [Stopped] [Live] [Paper]
[All Exchanges ▼] [Sort: P&L ▼]
[+ Create Bot] button

One section per wallet (independent queues):

WALLET 1 — MEXC · $234 available
Queue (competing bots):
Rank | Coin | Loss% | $ Needed | Trigger Price | Score
1    | ETH  | -18%  | $45      | $3,651        | 0.400
2    | RVN  | -24%  | $32      | $0.025        | 0.750
3    | SOL  | -12%  | $28      | $126          | 0.428

Simulate: [If I add $X] [If I turn off bot]

Bots in wallet (collapsed rows):
▶ ALL COINS Bot · Smart DCA · Running 🟢
   Active coins: 47 | Open: 312 | Queue: 38

▶ BTC Bot · ASAP · Running 🟢
   Open: 3 | Queue: 0

▶ ETH Bot · Custom Entry · Stopped 🔴
   Open: 1 | Queue: 0

Per bot row shows:
- Method badge · Status dot · Trade/DCA toggles
- Exchange badge [M][B][K][O][G][By][Bg]
- [⋮ kebab menu]: Edit · Duplicate · Delete

Click bot → 3 sub-tabs:
[Positions] [Queue] [Closed]

POSITIONS SUB-TAB:
Summary: Open: 312 | Invested: $12,400 | P&L: -$521
Filter: [All] [Profitable] [Losing] [Most DCAs]
Search: [coin name]
Sort: any column

Coin | Days | Entry | Current | DCAs | P&L$ | P&L%
BTC  | 7d   | $67.2K| $68.1K  | 1    | +$90 | +1.3%
ETH  | 11d  | $3,840| $3,710  | 2    | -$130| -3.4%
RVN  | 14d  | $0.032| $0.028  | 3    | -$40 | -12%

Tap position → position detail screen:
- Full DCA history
- Entry → DCA levels → TP progress bar
- All fees breakdown
- Pagination: 25/50/100 per page

QUEUE SUB-TAB:
38 coins waiting · $234 available

Rank | Coin | Loss% | $ Needed | Trigger Price | Score
1    | SOL  | -24%  | $28      | $126          | 0.857
2    | DOGE | -18%  | $32      | $0.081        | 0.562

Simulate:
[What if I add $50?] → shows new queue order
[What if I turn off DOGE?] → shows freed capital

CLOSED SUB-TAB:
Filter: [This week] [This month] [All time]
Sort: any column
Coin | Entry | Exit | Days | DCAs | P&L$ | P&L%
Summary: Win rate · Avg DCAs · Avg hold · Total profit

─── HISTORY ───
ALL closed trades across ALL bots ALL wallets

STATS BAR:
Closed: 1,247 | Win rate: 67% | Total profit: +$8,470
Total fees: $1,694 | Avg hold: 11.3d | Avg DCAs: 2.1

FILTERS:
[Exchange ▼] [Coin ▼] [Date range] [Entry method ▼]
[All] [This week] [This month] [Wins only] [Losses only]

TABLE (sortable all columns):
Date | Exchange | Coin | Entry | Exit | Days | DCAs | P&L$ | P&L% | Fee | Method

Tap row → position detail screen

EXPORT: [Download CSV] [Download Excel]
Pagination: 50 per page

---

### TAB 3 — Settings

SECTION 1 — Profile:
Email · Phone · [Change Password]
Account created · Referral code: ABC123
[Copy referral link]

SECTION 2 — Exchanges:
Per exchange row:
Name · Status · Last connected
[Test Connection] [Edit] [Delete]

Test shows:
✅ Connected · Balance: $234.50
❌ Invalid key / IP not whitelisted / Wrong passphrase

[+ Add Exchange] button
Form: Name · API Key · Secret · Passphrase · IP whitelist ☑

SECTION 3 — Notifications:
Telegram: @AverionBot ✅ [Disconnect]
If not connected: [Connect Telegram]
Toggles (independent ON/OFF):
Trade opened · Trade closed · DCA fired
Alert · Daily report · Weekly report · Monthly report

SECTION 4 — Reserve Wallet:
Balance: $50.00
Fee debt: $0 (red if debt exists)
Last 10 deposits history
[Top Up] → NOWPayments flow
No withdrawal · funds used for trading only

SECTION 5 — Subscription & Billing:

Free plan (always):
5 bots · 100 trades/month · forever

Per Bot billing:
Bot Name | Expires | Auto-renew | [Renew]
Each bot has own expiry
Auto-renew: deducts from reserve 3 days before
Telegram reminder 3 days before expiry
[+ Add Bot Slot $1/month]

Per Trade Bundle:
Current: X used · Y remaining · expires Z
[+ Buy Bundle]: 200=$3 · 500=$5 · 1000=$8 · Unlimited=$15/mo
Bundles stack · current used first
Auto-renew toggle per bundle

SECTION 6 — Security:
Last login: date · IP · device
Active sessions list
[Log Out All Devices]
2FA via Telegram toggle

---

### Bot Creation Wizard (7 Steps)

Step 1 — Basic Setup:
Bot Name · Exchange · Direction (Long/Short)

Step 2 — Trading Method:
○ Smart DCA (recommended · fully automated)
○ ASAP (buy immediately)
○ Custom Builder (up to 3 conditions):
  [indicator ▼] [operator ▼] [value]
  + [Add condition] (max 3)
  Preview: "RSI < 35 AND VWAP distance > 3%"
  [Test: fires X times in last 30 days]
○ TradingView webhook

Step 3 — Order Settings:
Base Order ($) · Quote Currency
Entry Order Type: Market/Limit
DCA Order Type: Market/Limit

Step 4 — DCA Settings:
Smart DCA: automated (show coin confidence)
Manual: DCA Trigger% · Spacing Mult · Size Mult
Trades per Bot · Trades per Coin
Sequential Gates: DCA trigger · Timer

Step 5 — Profit Settings:
Smart DCA: Auto TP (recommended) or Manual
Manual: Take Profit% · Trailing%
Profit Currency: USDT or Base coin

Step 6 — Safety Settings:
Reserve Floor ($) · Resume Threshold ($)
Auto-Resume toggle · Min Daily Volume

Step 7 — Review & Launch:
Full summary · Amber warnings · Red errors
Coin confidence breakdown
Min order size per coin: ✅ ⚠️ ❌
[Back to any step] [Launch Bot]

---

### Bot Edit (from kebab menu):
Same as wizard but pre-filled
Changes apply to NEW trades only
Existing open trades keep original params (LOCKED)

---

### Duplicate Bot:
Opens wizard pre-filled
Modify any step
Creates new independent bot
Original bot unaffected

---

### Position Detail Screen:
Position ID · Coin · Exchange · Bot · Entry method
Progress bar: Entry → DCA levels → Exit
Full DCA history:
Level | Date | Price | Amount | Qty | Cumulative avg
Summary: Total invested · Avg cost · Exit price
Fees breakdown: Exchange fees · Performance fee 20%
Net profit after all fees
