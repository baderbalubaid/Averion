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

#### 03:30 — CoinGecko Fetch
- Fetch all coins market caps (250 per call · dynamic)
- Store raw caps in coin_history (source: coingecko)
- No classification yet · raw data only

#### 04:00 — CoinMarketCap Fetch
- Fetch all coins market caps from CMC API
- Store raw caps in coin_history (source: cmc)
- No classification yet · raw data only

#### 04:30 — Classification
- Average: recorded_cap = (CoinGecko + CMC) / 2
- If only one source: use that source
- If both fail: use last recorded · Telegram alert
- Apply cap protection formula
- Classify all coins into categories
- Reclassify changed coins · Telegram alert per change

#### 05:00 — Reporting
- Generate Excel report (9 sheets · fresh classification)
- Update metrics/latest.json → push to GitHub
- Send daily Telegram to admin (health + stats)
- Send daily Telegram to each customer (their summary)
- Save report to /reports/ folder

#### 1st of Month — Key Rotation
- Generate new Fernet key
- Re-encrypt all exchange API keys
- Delete old key
- Alert admin via Telegram
- Log in fernet_key_versions

#### 05:30 — Sunday Only
- DB VACUUM + ANALYZE
- Delete logs older than 30 days
- Delete Excel reports older than 30 days
- Disk space check → alert if >70%
- Weekly Telegram summary (profit + fees + rankings)
- Check CCXT version → safe upgrade if available

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

## Telegram Setup (LOCKED)

- ONE direct chat with @AverionBot per customer
- Message types labeled clearly in one chat:
 - 🟢 TRADE: every buy · sell · DCA · TP
 - 🔴 ALERT: reserve low · ST flag · errors · urgent
 - 📊 REPORT: daily · weekly · monthly summaries
- Customer toggles each message type ON/OFF independently
- Admin alerts go to admin Telegram separately

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
