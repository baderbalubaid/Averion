# Infrastructure

> How Averion runs on the server.
> Hetzner setup · maintenance · monitoring · Telegram.

---

## Server

| Item | Detail |
|------|--------|
| Provider | Hetzner Cloud |
| Plan | CX23 |
| Location | Helsinki, Finland |
| OS | Ubuntu 24.04 |
| RAM | 4GB |
| CPU | 2 vCPU |
| Disk | 40GB |
| Cost | €3.99/month |
| Status | Ordered · ID verification pending (~10 days) |

---

## Current Setup (Replit)

- Dashboard URL: https://bbd72f98-d728-46fe-81c6-af97d0011150-00-1c2g4v036wde1.sisko.replit.dev/dashboard
- Bot runs via Replit always-on
- MAX_COINS = 100 (Replit memory limit only)
- Remove MAX_COINS limit on Hetzner

---

## Automated Schedule (LOCKED)

### Every 60 Seconds
- Live prices fetched
- DCA triggers checked
- TP exits checked
- Smart queue executed

### Every Hour
- Health check (CPU · RAM · Disk · PM2 · trades count)
- OHLCV fetch all coins
- ATR recalculate
- Volatility spike guard
- ST flag check on all exchanges
- Alert if any threshold breached

### Daily 3am (Staggered — LOCKED)

#### 03:00 — Infrastructure
- pip install ccxt --upgrade
- pm2 restart averion
- DB backup → /backups/averion_YYYY-MM-DD.db
- Keep last 7 days only

#### 03:30 — Data & Classification
- CoinGecko scan → market cap fetch
- Cap protection formula applied
- Classify/reclassify all coins
- Parameter recalculation (ATR + median bounce)
- Volume-weighted category update

#### 04:00 — Reporting
- Balance snapshot → balance_history table
- metrics/latest.json → pushed to GitHub
- Excel report generation (4 sheets)
- Telegram daily report → Reports channel

#### 04:30 — Sunday Only
- Log cleanup (files >30 days old)
- Disk check (alert if >70%)
- DB VACUUM + ANALYZE
- Weekly Telegram report

### Monthly 1st 5am
- Full system report
- Category performance summary
- Fee summary
- Backup verification

---

## Health Check Thresholds

| Metric | Warning | Critical |
|--------|---------|---------|
| CPU | >80% | >95% |
| RAM | >80% | >95% |
| Disk | >70% | >85% |
| PM2 | Not running | — |
| Bot silent | >5 minutes | — |

All alerts → Telegram Alerts channel immediately

---

## 3 Telegram Channels (LOCKED)

| Channel | Content | Volume Setting |
|---------|---------|---------------|
| Trades | Every buy · sell · DCA · TP | MUTE — check weekly |
| Alerts | Server down · errors · crashes · ST flag · floor hit | MAX VOLUME — NEVER MUTE |
| Reports | Daily · weekly · monthly reports | Normal — morning coffee |

### Config in .env
---

## PM2 Process Manager

- pm2 start main.py --name averion
- pm2 startup → auto-restart on reboot
- pm2 save → saves process list
- pm2 logs averion → view live logs
- pm2 restart averion → manual restart

---

## Daily Telegram Report Example
---

## Maintenance Time Expectations

| Task | Time | Notes |
|------|------|-------|
| Daily check | 30 seconds | Read Telegram Reports |
| Weekly check | 2 minutes | Admin health dashboard |
| Monthly review | 5 minutes | Share research URL → Claude analyzes |
| Code deploy | 30 seconds | git push → auto-deploys |
| API emergency | 15-30 min | SSH → pm2 logs → pip upgrade → restart |

---

## Hetzner Day 1 Checklist
See 16_TODO_HETZNER.md for full step-by-step commands.

---

## Professional Folder Structure (Hetzner Only)
Note: On Replit — keep single file structure (simpler).
Split to professional structure on Hetzner Day 1 only.
