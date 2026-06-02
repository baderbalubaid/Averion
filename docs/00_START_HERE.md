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
2. Market orders are the default for guaranteed execution — exceptions: Short DCA buyback uses limit order · users may enable limit entry/DCA per bot in wizard
3. 20% fee on REALIZED profits only — loss months = $0
4. User funds ALWAYS on their exchange — Averion never holds
5. Paper stays paper FOREVER — live stays live — no conversion
6. Settings tab = account info ONLY — bot config in wizard
7. Cap protection: +10% max upward per day — full drop immediately
8. Classification automated daily — CoinGecko + CMC averaged
9. NO max DCA levels — smart queue handles capital forever
10. Bot NEVER stops — put money and forget it
11. Reclassification affects NEW positions only — existing positions keep original params FOREVER (Option A · LOCKED)
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
