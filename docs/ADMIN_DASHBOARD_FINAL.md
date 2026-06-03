## Admin Dashboard — Final Design V2 (LOCKED)

### Two Separate Dashboards
1. Customer Dashboard → what users see
2. Admin Dashboard → what owner sees
Admin is ALSO a user with own trades · own bots · own copies

---

### TOP BAR (always visible)
🟢 Averion · Cycle 4,521 · 1.8s ago
Fees owed to me: -$2,341 (negative = customers owe owner)
[Users: 47] [Bots: 312] [Open: 1,847]

---

### TAB 1 — Dashboard (Home)

ALERTS SECTION (only when needed):
🔴 User #3 · MEXC paused · API key invalid [View]
🟡 User #5 · reserve low $2.30 [View]
🟢 CCXT upgraded 4.5.56 → 4.5.57
Empty = "✅ All systems normal"

PLATFORM OVERVIEW (general stats):
Total users: 47 | Total bots: 312
Open positions: 1,847 | Capital managed: $234,500
Fees collected all time: $12,450
Fees outstanding (owed to me): -$2,341
Owner wallet balance: $4,230

YESTERDAY SUMMARY:
Trades closed: 234 | Fees collected: $456 | New users: 3
[Transfer to Owner Wallet]

CRON STATUS (compact · click to expand):
03:00 ✅ · 03:30 ✅ · 04:00 ❌ · 04:30 ⚠️ · 05:00 ✅
Click → [Re-run] [Logs] [Copy as Markdown]

SERVER STARTUP STATUS:
PostgreSQL: ✅ | Redis: ✅ | Bot Loop: ✅ | Nginx: ✅

EXCHANGES OVERVIEW:
| Exchange | Users | Bots | Open | Volume | Status |
|----------|-------|------|------|--------|--------|
| Binance | 18 | 94 | 423 | $45,230 | 🟢 |
| MEXC | 12 | 67 | 312 | $28,100 | 🟢 |
| KuCoin | 9 | 54 | 234 | $19,800 | 🟡 Slow |

---

### TAB 2 — My Bots

Sub-navigation: [Bots & Queue] [History]

─── BOTS & QUEUE ───

One section per wallet (independent queues):

WALLET 1 — Binance · $1,240 available
Queue (competing bots):
Rank | Coin | Loss% | $ Needed | Trigger Price | Score
1 | ETH | -18% | $45 | $3,651 | 0.400
2 | BTC | -8% | $120 | $65,382 | 0.067
3 | SOL | -12% | $28 | $126 | 0.428
Simulate: [If I add $X] [If I remove $X] [If I turn off coin]

Bots in wallet (collapsed):
▶ ALL COINS Bot · Smart DCA
   Coins active: 47/500 | Open: 312 | Queue: 38 | Closed: 847

▶ BTC Bot · ASAP
   Open: 3 | Queue: 0 | Closed: 44

Click bot → 3 tabs inside:
[Positions] [Queue] [Closed]

POSITIONS TAB:
Filter: [All] [Profitable] [Losing] [Most DCAs]
Search: [coin name]
Sort: any column
Coin | Days | Entry | Current | DCAs | P&L$ | P&L%
Pagination: 25/50/100 per page

QUEUE TAB:
Rank | Coin | Loss% | $ Needed | Trigger Price | Score
Simulate: [Add $X] [Remove $X]

CLOSED TAB:
Filter: [This week] [This month] [All time]
Sort: any column
Coin | Entry | Exit | Days | DCAs | P&L$ | P&L%
Summary: Win rate · Avg DCAs · Avg hold · Total profit

─── HISTORY ───
ALL closed trades across ALL bots ALL exchanges

Stats bar:
Total trades | Win rate | Total profit | Total fees
Avg hold | Avg DCAs | Best trade | Worst trade

Filters:
[Exchange] [Coin] [Date range] [Entry method]
[Profitable only] [Loss only] [This week/month]

Table (sortable):
Date | Exchange | Coin | Entry | Exit | Days | DCAs | P&L$ | P&L% | Fee | Method

Export: [Download CSV] [Download Excel]

---

### TAB 3 — My Copy

MY ACTIVE MIRRORS:
| User | Exchange | Bots Mirrored | Open | P&L$ | [Stop] |
[+ Mirror New User]

MY COPY BOTS:
| Source User | Bot | Coin | Performance | Status |

MIRROR HISTORY:
Log of all past mirrors · start/stop times

---

### TAB 4 — Research

CHAMPION STATUS:
Bull: E11-3 (RARS 0.745) since 2026-03-15 ⭐
Bear: E6-2 (RARS 0.812) since 2026-02-01 ⭐
Sideways: E1-1 (RARS 0.623) since 2026-01-10 ⭐
Auto-Switch: [ON ●]

TRADE COUNT CONTROL:
Trades per bot: [10] [Apply to All 252 bots ✓]
Confirmation popup before applying

RESEARCH BOTS (collapsed by method):
▶ E1 · 12 bots · 847 trades · 65% win · +$4,200
▶ E11 · 9 bots · 723 trades · 71% win · +$6,800 ⭐

Click method → variations:
E11-1 · E11-2 · E11-3 ⭐ BULL CHAMPION

Click variation → detail panel:
[Positions] [Closed] tabs with full trade details
Summary: Win% · Avg DCAs · Avg Days · RARS · Regime

REPORTS:
[Last Weekly Report - Download Markdown]
[Full Report Day 1 to Today - Download Markdown]
[Generate Now]

Full report = all data since launch
Every week · every method · complete history
Share with AIs for deep analysis

---

### TAB 5 — Users

USERS TABLE (sortable · searchable):
ID | Email | Capital | Bots | Open | Profit$ | Profit% | Fees Owed | Status

Click row → LEVEL 1 (user summary):
Email · Joined · Plan · Reserve · Referral income
Server load % | Last active
[Suspend] [Copy Exchanges] [Fee Override] [Delete]

SUSPEND BEHAVIOR:
→ Cannot top up reserve
→ Cannot open new trades
→ Existing positions continue to TP
→ Bot consumes reserve until zero
→ Then pauses (no new entries)
→ User notified via Telegram
→ Not holding any customer money

LEVEL 2 — Per exchange (dropdown):
| Exchange | Bots | Open | Profit$ | Profit% | Fees | [Copy] |

LEVEL 3 — Per bot per exchange (dropdown):
| Bot | Coin | Open | Profit$ | Profit% | Fees | Entry Method |

USER ACTIONS:
[Fee Override: 0%/10%/20%/Custom]
[Trade Limit Override]
[Add Free Trial Credit]
[Suspend] [Unsuspend]
[Delete Account]

---

### TAB 6 — Health

SERVER STARTUP STATUS:
| Service | Status | Uptime | Last Check |
| PostgreSQL | 🟢 | 14d 3h | 1 min ago |
| Redis | 🟢 | 14d 3h | 1 min ago |
| Bot Loop | 🟢 Cycle 4521 | 14d 3h | 1.8s ago |
| Nginx | 🟢 | 14d 3h | 1 min ago |
| PM2 | 🟢 | 5 processes | 1 min ago |

SERVER METRICS (live):
CPU: 23% | RAM: 1.8GB/4GB | Disk: 12GB/40GB
Loop avg: 1.8s | Max: 4.2s | Min: 0.9s
Capacity: 1,847/2,400 positions (77%)

30-DAY ROLLING LOG (chart):
CPU · RAM · Loop time trends
Click any day → see that day details

CRON DETAILED LOG:
[Today] [Yesterday] [Last 7 days]
Each step: Time · Duration · Status · Records processed
[Copy] [Re-run] buttons per step

FETCH STATUS:
03:00 CoinGecko [✅ 312 coins · 0.8s] [Re-run]
03:30 CMC [✅ 312 coins · 1.2s] [Re-run]
04:00 OHLCV [❌ Failed at coin 87] [Re-run]
04:30 Classify [⚠️ 3 coins reclassified] [Re-run]
05:00 Research [✅ Week 12 report] [View]

PERFORMANCE LOG (what is slow):
| Operation | Avg Time | Max Time | Frequency |
| OHLCV fetch | 2.1s | 8.4s | Hourly |
| Bot loop | 1.8s | 4.2s | Every 60s |
| DB query | 0.3s | 1.2s | Per loop |

COPY AS MARKDOWN button:
Generates structured health report:
---
# Averion Server Health Report
Generated: 2026-06-03 14:30
Server: Hetzner CX23 (2 vCPU · 4GB RAM)
Purpose: Review server performance.
Share with AI for recommendations.

## Current Status
[all services]

## Last 30 Days Rolling Data
[daily metrics table]

## Slowest Operations
[ranked list]

## Notes
[blank · AI fills after review]
---
Auto-updates server specs if upgraded

BACKUP STATUS:
Last: 2026-06-03 03:00 · 284MB ✅
[Backup Now] [Download]

---

### TAB 7 — Trading

EXCHANGES MANAGEMENT:
| Exchange | Users | Status | API Health | [Toggle] |
Per exchange: maintenance note when OFF

COIN CLASSIFICATION:
Search: [BTC/USDT ▼]
Shows: Category · Cap · Confidence · Spacing · TP · Trail
Last updated timestamp

CATEGORY TABLE:
Current regime: SIDEWAYS
| Category | Spacing Min/Max | TP Min/Max | Trail | [Edit] |
[Dynamic limits: ON/OFF]

SMART DCA CHAMPIONS:
Bull: E11-3 [Change] [Toggle Auto]
Bear: E6-2 [Change] [Toggle Auto]
Sideways: E1-1 [Change] [Toggle Auto]

REGIME DETECTION:
Today score + all 5 signals breakdown

---

### TAB 8 — Controls

BOT CONTROLS:
[Start] [Pause New] [Stop All] [Restart] [Force Reconcile]

COMPONENT TOGGLES:
CoinGecko · CMC · OHLCV · Telegram · Excel
Email · Research bots · Auto-switch champion

OWNER WALLET:
Outstanding: $2,341 | Threshold: $10
[Transfer Now] [History]
Wallet addresses (TRC20 · BEP20) [Edit]

ANTI-FRAUD & SECURITY:
Failed logins · Active sessions · Suspicious IPs
[View sessions] [Revoke all]

REFERRAL MANAGEMENT:
Active codes · Total payouts · Avg rate

NOWPAYMENTS:
Webhook status · Last payment · Failed webhooks

BACKUP & MAINTENANCE:
[Backup Now] [Download] [Force CCXT Upgrade]

---

### TAB 9 — System

ACCOUNT:
[Change Password] [Change Email]
Telegram 2FA: ✅ [Test] [Regenerate]

ACCESS LOG:
Time · IP · Action · Status (last 30 entries)

API TOKENS:
Hetzner · GitHub · Resend [Rotate each]

PLATFORM SETTINGS:
Default fee: 20% | Paper limit: 30 | Bot slots: 3
Support email | Platform name

DOCUMENTATION:
[View averion_COMPLETE.md on GitHub]
[Download Research Brief]
[Download DCA Parameter Brief]

DANGER ZONE:
[Reset paper trades]
[Clear research data] ⚠️
[Factory reset] ⚠️
