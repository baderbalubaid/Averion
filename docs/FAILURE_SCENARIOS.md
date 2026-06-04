# Averion Failure Scenarios & Recovery Guide

Purpose: Quick reference for support · debugging · AI review.
Share with AI when investigating platform issues.
Generated: see platform health reports for live data.

---

## Exchange Offline
Symptom: CCXT returns connection error repeatedly
System: exponential backoff · pause that exchange only
Recovery: auto-resumes when exchange recovers
Other exchanges: continue unaffected
Admin: Telegram Channel 1 alert
Customer: Telegram alert (API paused)

---

## Coin Delisted (ST Flag)
Symptom: exchange marks coin ST · orders rejected
System: immediate MARKET sell · position closed
Recovery: automatic · no manual action needed
Admin: Telegram Channel 1 alert
Customer: Telegram alert with P&L

---

## Database Crash (PostgreSQL)
Symptom: connection refused · PM2 restarts
System: PM2 auto-restarts bot · reconnects DB
Recovery: reconcile_orders() runs on startup
         matches all open positions vs exchange
Admin: Telegram Channel 1 alert

---

## Server Reboot (Planned or Unplanned)
Symptom: all processes stopped
Recovery sequence on restart:
1. PM2 starts all processes
2. reconcile_orders() matches DB vs exchange
3. Bot loop resumes from last known state
4. PENDING_BUYBACK positions verified
Admin: Telegram bot started notification

---

## API Key Revoked by User
Symptom: exchange returns 401 unauthorized
System: pause that exchange only
Recovery: user updates API key in Settings
Admin: Telegram Channel 2 notification
Customer: Telegram alert with fix instructions

---

## API Key Expired (90-day expiry)
Symptom: same as revoked
System: alert 7 days · 3 days · 1 day before
Recovery: user creates new key + updates
Admin: sees in Users tab (red indicator)

---

## CoinGecko Outage
Symptom: API returns error or timeout
System: use CMC only for that cycle
Recovery: retry next 03:30
Classification: continues with CMC data only

---

## CMC Outage
Symptom: API returns error or timeout
System: use CoinGecko only for that cycle
Recovery: retry next 04:00

---

## Both CoinGecko + CMC Down
System: freeze classification
Use last recorded market caps
No reclassification until one source recovers
Admin: Telegram Channel 1 alert

---

## Reserve Wallet Empty
Symptom: balance = $0
System: pause new trades
TP: always fires (never blocked)
DCA: pauses (no capital)
Recovery: user tops up via NOWPayments
Admin: sees debt/balance in Users tab

---

## NOWPayments Webhook Failed
Symptom: deposit made but not credited
System: hourly polling as backup check
Recovery: auto-credited within 1 hour maximum
Admin: manual [Match Deposit] button in Controls

---

## Telegram Bot Down
Symptom: notifications not sending
System: queue up to 50 messages
Recovery: sends all queued when Telegram recovers
Fallback: email for critical alerts (API disconnect · debt)

---

## CCXT Upgrade Breaks Exchange
Symptom: validation tests fail after upgrade
System: automatically stays on current version
Recovery: retry next Sunday automatically
Admin: Telegram Channel 3 alert

---

## Fernet Key Rotation Fails
Symptom: rotate_fernet.py crashes mid-rotation
System: stays on old key · no data corruption
Recovery: run rotation manually
Admin: immediate Telegram Channel 1 alert
Risk: old key stays active until fixed

---

## Disk Full (90%+)
Symptom: disk write errors · OHLCV not saving
System: pause OHLCV collection
Recovery: clean old cron logs · upgrade storage
Admin: Telegram Channel 1 alert
Fix: df -h · rm old logs · upgrade to larger Hetzner volume

---

## Loop Time > 30s
Symptom: bot cycle taking longer than 30s
System: continues but logs warning
Recovery: upgrade server
Triggers: CX23 → CX33 (€17.99/mo)
Admin: Telegram Channel 3 + daily health report shows spike

---

## Short DCA Buyback Order Missing
Symptom: limit buy order cancelled on exchange
System: detected within 60 seconds (every loop)
Recovery: immediately re-places limit buy
Admin: Telegram Channel 2 notification
Customer: Telegram alert

---

## PENDING_BUYBACK Deadlock
Symptom: flag stuck TRUE · Long DCA skipping
System: 5-minute timeout clears flag
Recovery: next loop cycle re-evaluates
Admin: health report shows if recurring

---

## Scale Upgrade Path (LOCKED)

100 users:
→ CX33 + pgBouncer ✅

500 users:
→ CX53 + dedicated PostgreSQL server
→ Read replicas for research queries
→ Partition large tables (trades · ohlcv_hourly)

2000 users:
→ Multiple app servers + Nginx load balancer
→ Split bot loop workers per exchange group
→ Worker 1: Binance + MEXC
→ Worker 2: KuCoin + OKX
→ Worker 3: Bybit + Gate.io + Bitget

10000+ users:
→ Full cloud infrastructure
→ TimescaleDB or ClickHouse for OHLCV
→ Redis cluster for caching
→ Multiple API instances
→ Managed PostgreSQL (Hetzner DBaaS)
→ CDN for dashboard assets

Rule: upgrade when ANY of these hit:
→ CPU avg > 60% for 7 consecutive days
→ Loop avg > 15s for 7 consecutive days
→ RAM avg > 3GB for 7 consecutive days
