# Admin System

> Admin panel · all 5 tabs · controls · security.
> Completely separate from user dashboard.

---

## Access

- Secret URL stored in .env only — never in code — never on GitHub
- Format: averion.app/ops-XXXX (random string set in .env)
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
