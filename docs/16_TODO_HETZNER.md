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
| research_bots.json | ✅ Ready | 144 paper bots configured |
| launch_research_bots.py | ✅ Ready | Launch all 144 bots |
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

- 144 research bots running simultaneously
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
