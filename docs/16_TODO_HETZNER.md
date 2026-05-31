# TODO — Hetzner Items

> Everything that requires the actual server.
> Do NOT attempt on Replit — server only.
> All commands run via SSH on Hetzner.

---

## Server Details
- Provider: Hetzner Cloud
- Plan: CX23 (4GB RAM · 2 vCPU · 40GB disk)
- Location: Helsinki, Finland
- OS: Ubuntu 24.04
- Cost: €3.99/month
- Status: Ordered · ID verification pending ~10 days

---

## Day 1 — Server Setup & Security

### Step 1 — First Login
### Step 2 — Create Non-Root User
### Step 3 — SSH Key Setup
### Step 4 — Firewall
### Step 5 — Fail2ban
### Step 6 — Install Python + Dependencies
---

## Day 1 — Clone & Setup

### Step 7 — Clone GitHub Repo
### Step 8 — Create .env File
Add all variables:
### Step 9 — PM2 Setup
### Step 10 — Install Cron Jobs
Add:
### Step 11 — UptimeRobot
- Create free account at uptimerobot.com
- Add monitor for http://YOUR_IP:8080
- Alert email + Telegram if down

### Step 12 — GitHub Actions Auto-Deploy
- Create .github/workflows/deploy.yml
- git push → auto-deploys to Hetzner
- No manual SSH for code updates

---

## Day 2 — Domain & HTTPS

### Step 13 — Buy Domain
- Buy averion.app (same day server goes live)
- Point DNS A record to Hetzner IP
- Wait for DNS propagation (1-24 hours)

### Step 14 — Nginx Setup
### Step 15 — HTTPS Certificate
### Step 16 — Test Live Order
- Set PAPER_MODE=false in .env
- Watch 10 second countdown warning
- Confirm red banner in dashboard
- Place $1 test order on MEXC
- Verify order appears on exchange
- Set PAPER_MODE=true again

---

## Day 3-16 — Paper Trading Data Collection

- Bot runs 24/7 collecting data
- All 10 entry methods running simultaneously
- OHLCV data building up per coin
- Excel reports generated daily at 4am
- Monitor Telegram Reports channel daily
- Monitor Telegram Alerts channel (never mute)

---

## Day 17 — Parameter Optimization

- Download Excel report from server
- Upload to Claude: "Analyze this and optimize DCA parameters"
- Share same file with ChatGPT for second opinion
- Compare recommendations
- Apply best parameters to config
- Restart bot with new parameters

---

## Day 18+ — Live Trading

- Set PAPER_MODE=false in .env
- Monitor first 24 hours closely
- Check Telegram Alerts constantly
- Verify real orders on MEXC exchange
- Scale gradually

---

## Hetzner Items 27-46 (Full List)

| # | Task | When |
|---|------|------|
| 27 | Server creation + security baseline | Day 1 |
| 28 | Clone GitHub + folder structure | Day 1 |
| 29 | Create .env with all variables | Day 1 |
| 30 | pm2 start + startup + save | Day 1 |
| 31 | Buy averion.app + DNS | Day 2 |
| 32 | Nginx + HTTPS certificate | Day 2 |
| 33 | Secret admin URL via .env | Day 1 |
| 34 | Fernet API key encryption | Day 1 |
| 35 | GitHub Actions auto-deploy | Day 1 |
| 36 | UptimeRobot monitoring | Day 1 |
| 37 | 3 Telegram channels + .env | Day 1 |
| 38 | Cron jobs installed + tested | Day 1 |
| 39 | ohlcv_hourly table + hourly fetch | Day 1 |
| 40 | Daily aggregation script | Day 1 |
| 41 | metrics/latest.json → GitHub daily | Day 1 |
| 42 | Admin health dashboard (Tab 2) | Day 1 |
| 43 | Excel daily report generator | Day 1 |
| 44 | Server measurement (baseline→500 trades) | Day 1-5 |
| 45 | Test live $1 order on MEXC | Day 2 |
| 46 | Global + per exchange toggles in admin | Day 1 |

## Database Decision (LOCKED)

- Use PostgreSQL from Day 1 (not SQLite)
- PostgreSQL = free software · same server cost
- Much better performance for 21,400+ positions
- No migration headache later
- Install during Day 1 server setup

## Server Scaling Plan (LOCKED)

- Start: CX23 €3.99/mo (4GB RAM · 2 vCPU)
- Test gradually: 10 → 20 → 50 → 100 → 200 trades per bot
- Measure loop time at each step
- If loop time > 30 seconds → upgrade server
- Upgrade path:
  - CX33: €7.49/mo (8GB RAM · 4 vCPU)
  - CX43: €16.49/mo (16GB RAM · 8 vCPU)
  - CX53: €32.99/mo (32GB RAM · 16 vCPU)
- Downgrade when research phase ends
- Goal: know exact CX23 capacity in trades
- This data = valuable for Phase 6 planning

## Frontend Architecture — Separate Files (LOCKED)

Split dashboard.html into separate files on Hetzner Day 1.
Structure evolves — new sections get new files · removed from old files.

### File Structure
frontend/
├── index.html
├── css/
│   ├── base.css
│   ├── layout.css
│   ├── components.css
│   ├── tables.css
│   └── responsive.css
├── pages/
│   ├── login.html
│   ├── dashboard.html
│   └── admin.html
├── tabs/
│   ├── home/home.html + home.js
│   ├── bots/bots.html + bots.js + bot-detail.html + bot-detail.js
│   ├── history/history.html + history.js
│   └── settings/settings.html + settings.js
├── wizard/
│   ├── wizard.html + wizard.js
│   └── steps/step1 through step7.html
├── admin/
│   ├── admin-shell.html
│   └── tabs/overview + health + users + smart-mode + controls
├── components/
│   ├── exchange-card.html
│   ├── bot-row.html
│   ├── position-row.html
│   ├── modal-add-exchange.html
│   └── modal-add-funds.html
└── js/
    ├── api.js
    ├── auth.js
    ├── navigation.js
    ├── notifications.js
    └── utils.js

### Rules
- Each folder = one responsibility
- New section needed = create new file
- Remove from old file after moving
- Claude edits one file at a time
- Never touch multiple sections in one session
- Structure evolves naturally — never forced
