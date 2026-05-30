# Phase Roadmap

> Averion development phases from proof of life to marketplace.

---

## Phase 1 — Proof of Life ✅ COMPLETE
**Goal:** Connect and place first paper buy

- MEXC via CCXT ✅
- Live BTC price ✅
- Paper buy console ✅
- Code on GitHub ✅

---

## Phase 2 — Paper Bot ✅ COMPLETE
**Goal:** Full DCA engine running 100 coins

- SQLite + WAL ✅
- DCA from LAST BUY PRICE ✅
- Widening spacing ✅
- Trailing TP ✅
- 100 coins MEXC ✅

---

## Phase 3 — Dashboard ✅ COMPLETE
**Goal:** Production web app accessible from any device

- 13 API endpoints ✅
- Home tab: 5 stats + fees + exchange cards ✅
- Exchange Detail: chart + bots ✅
- Bots tab L1+L2: positions + search + filters ✅
- History tab: 6 stats + fees 20% + net + date range ✅
- Settings tab: account info only ✅
- Auto responsive CSS ✅
- Saudi Arabia timezone ✅

---

## Phase 3.5 — Prep Files ✅ COMPLETE
**Goal:** Hetzner ready before server arrives

- requirements.txt ✅
- .env.example ✅
- .gitignore ✅
- README.md ✅
- automation/daily_cron.sh ✅
- automation/weekly_cron.sh ✅
- /docs folder with markdown documentation ✅

---

## Phase 4 — Live Trading ⏳ NEXT
**Goal:** First real order on Hetzner server

### Replit remaining (before Hetzner):
- Item 24: Bots tab flat list redesign
- Item 25: Updated documentation
- Item 26: Dashboard comment markers

### Hetzner Day 1:
- Server setup + security baseline
- Clone GitHub + folder structure
- Create .env file
- pm2 start + startup + save
- Cron jobs installed and tested
- UptimeRobot monitoring
- 3 Telegram channels configured
- GitHub Actions auto-deploy

### Hetzner Day 2:
- Buy averion.app domain
- Nginx reverse proxy
- Let's Encrypt HTTPS
- Test live $1 MEXC order (PAPER_MODE=false)

### Days 3-16:
- Paper trading 24/7
- All 10 entry methods collecting data
- Excel reports generated daily
- Monitor health checks

### Day 17+:
- Upload Excel to Claude → optimize parameters
- Live trading with validated parameters

---

## Phase 5 — Smart Systems
**Goal:** Full adaptive platform

- Smart DCA queue (Loss% ÷ USDT scoring)
- 10 entry methods running simultaneously
- Research system + MoM + decision history
- Auto-classification engine
- Cap protection system
- Volume-weighted parameters
- Bot creation wizard (7 steps)
- Trade limits system
- Reserve wallet system
- Referral system 3%
- Two bot toggles (Trading + DCA)
- Reserve floor + auto-resume
- Recovery buy system
- TradingView webhook

---

## Phase 5.5 — Backtesting
**Goal:** Validate Smart DCA equations

- Grid search coefficients
- Out-of-sample testing
- Walk-forward validation
- MDD optimization
- Per-category tuning

---

## Phase 6 — Full Platform
**Goal:** Multi-user production

- PostgreSQL (migrate from SQLite)
- JWT authentication
- All 7 exchanges fully integrated
- Short trading enabled
- PWA installable
- Docker containerization
- Admin panel full feature set

---

## Phase 7 — Public Launch
**Goal:** Paying subscribers

- Reserve wallet live (NOWPayments)
- Referral system live
- Anti-fraud 5 layers
- Stripe for fiat payments
- KYC/AML basics
- Terms of service
- Risk disclosures

---

## Phase 8 — Marketplace
**Goal:** Strategy providers in dashboard

- Signal provider listing
- Vetting system (win rate · history · drawdown)
- One-click subscribe
- Webhook auto-connected
- Averion takes 10-15% subscription + 20% performance fee

---

## Timeline Estimate

| Phase | Milestone | When |
|-------|-----------|------|
| 4 | Hetzner live | ~10 days (ID verification) |
| 5 | Smart systems | Month 3 |
| 5.5 | Backtesting | Month 6 |
| 6 | Multi-user | Month 9 |
| 7 | Public launch | Month 12 |
| 8 | Marketplace | Year 2 |
