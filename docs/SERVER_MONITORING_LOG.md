# Averion Server Resource Monitoring Log

## Server Specs
- Provider: Hetzner CPX32
- CPU: 4 AMD vCPU
- RAM: 8GB
- Disk: 160GB SSD
- OS: Ubuntu 26.04
- Floating IP: 46.225.251.75
- Date started: June 6 2026

---

## How to Measure (run on server)

### CPU + RAM:
```bash
free -h && echo "---" && top -bn1 | grep "Cpu(s)"
```

### Disk usage:
```bash
df -h / && du -sh /home/averion/Averion/
```

### PostgreSQL DB size:
```bash
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('averion'));"
```

### Bot loop time:
```bash
pm2 logs averion-live --lines 20 | grep "Loop time"
```

### Full snapshot command (run all at once):
```bash
echo "=== RAM ===" && free -h
echo "=== CPU ===" && top -bn1 | grep "Cpu(s)"
echo "=== DISK ===" && df -h /
echo "=== DB SIZE ===" && sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('averion'));"
echo "=== PM2 ===" && pm2 list
```

---

## PHASE A — Baseline (Server ready · no bot running)
Date: June 6 2026
Status: Schema loaded · admin created · no PM2 processes

| Metric | Value |
|--------|-------|
| RAM Used | 589 MB |
| RAM Free | 5.6 GB |
| RAM Available | 7.0 GB |
| CPU % | 0.0% (idle 97.7%) |
| Disk Used | 2.9 GB |
| Disk Free | 141 GB |
| Disk Use% | 2% |
| DB Size | 9.99 MB |
| PM2 Processes | 0 |
| Active Bots | 0 |
| Open Positions | 0 |
| Loop Time | N/A |

Notes: Fresh install · all dependencies · schema loaded · admin created
Healthy baseline · 141GB free · 7GB RAM available ✅

---

## PHASE B — Bot loop started (paper mode · 0 bots)
Date: TBD
Status: PM2 running · no bots created yet

| Metric | Value |
|--------|-------|
| RAM Used | 659 MB |
| RAM Free | 5.5 GB |
| RAM Available | 6.9 GB |
| CPU % | 0.0% (idle 97.7%) |
| Disk Used | 2.9 GB |
| Disk Free | 141 GB |
| DB Size | 9.99 MB |
| PM2 Processes | 1 |
| PM2 Memory | 106.2 MB |
| Active Bots | 0 |
| Open Positions | 0 |
| Loop Time | 0.01s |

Notes: Bot loop running · no bots · cycle every 60s
RAM increase from baseline: +70MB (PM2 + bot loop overhead)
Loop time: 0.01s = excellent ✅

---

## PHASE C — First 10 bots · 1 trade each
Date: TBD
Status: 10 paper bots · max 1 trade per bot

| Metric | Value |
|--------|-------|
| RAM Used | TBD |
| RAM Free | TBD |
| CPU % | TBD |
| Disk Used | TBD |
| Disk Free | TBD |
| DB Size | TBD |
| PM2 Processes | 2 |
| Active Bots | 10 |
| Open Positions | TBD |
| Loop Time | TBD |

Notes: First real load test

---

## PHASE D — 20 bots · 1 trade each
Date: TBD

| Metric | Value |
|--------|-------|
| RAM Used | TBD |
| RAM Free | TBD |
| CPU % | TBD |
| Disk Used | TBD |
| DB Size | TBD |
| Active Bots | 20 |
| Loop Time | TBD |

---

## PHASE E — 261 Long research bots · 1 trade each
Date: TBD
Status: Full Long research batch

| Metric | Value |
|--------|-------|
| RAM Used | TBD |
| RAM Free | TBD |
| CPU % | TBD |
| Disk Used | TBD |
| DB Size | TBD |
| Active Bots | 261 |
| Loop Time | TBD |

Notes: Critical threshold check

---

## PHASE F — 261 bots · 10 trades each
Date: TBD

| Metric | Value |
|--------|-------|
| RAM Used | TBD |
| RAM Free | TBD |
| CPU % | TBD |
| Disk Used | TBD |
| DB Size | TBD |
| Active Bots | 261 |
| Max Trades/Bot | 10 |
| Loop Time | TBD |

---

## PHASE G — 1566 bots (261 Long + 1305 Short)
Date: TBD
Status: Full research system

| Metric | Value |
|--------|-------|
| RAM Used | TBD |
| RAM Free | TBD |
| CPU % | TBD |
| Disk Used | TBD |
| DB Size | TBD |
| Active Bots | 1566 |
| Loop Time | TBD |

Upgrade trigger: Loop > 30s → upgrade to AX41

---

## Upgrade Decision Table

| Loop Time | Action |
|-----------|--------|
| < 15s | Excellent · no action |
| 15-30s | Watch carefully |
| > 30s | Plan upgrade soon |
| > 50s | Urgent · upgrade now |

## Server Upgrade Path
CPX32 (current) → AX41 → AX52 → AX102

---

## DAY 1 PROGRESS LOG

### Completed Today
✅ Server created (CPX32 · Hetzner)
✅ Floating IP configured (46.225.251.75)
✅ System updated + kernel upgraded
✅ All dependencies installed
✅ PM2 + Node.js installed
✅ PostgreSQL + Redis configured
✅ Averion cloned from GitHub
✅ Python packages installed
✅ .env configured
✅ Database schema loaded (all 40 tables)
✅ Admin user created
✅ Bot loop running via PM2
✅ API running via PM2
✅ Telegram connected (AverionsBot)
✅ Admin channel configured
✅ Login working with Telegram verification
✅ Show/hide password
✅ Enter key submits login
✅ Auto-verify on 6-digit code entry

### Bugs Fixed Today
- duplicate profit_coin parameter in database.py
- import telegram as tg missing from main.py
- import database as db missing from main.py
- db.init_pool() not called
- is_suspended wrong index (6→5)
- telegram_chat_id wrong index (3→5)
- send_verification never called in login
- verify route not loading (moved to top)
- timezone comparison error in verify_code
- OWNER_WALLET_TRC20 had space after = in .env
- SECRET_KEY not passed to PM2 processes
- ecosystem.config.js created for env vars

### Still Pending
- BTC price (needs exchange + bots)
- Top right user menu dropdown
- Auto-login without verification bypass
- Add MEXC exchange
- First paper bot
- Domain setup (averionbot.com)
- HTTPS setup
