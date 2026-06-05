# AI Reviews and Resolutions

> External AI feedback on Averion v4.6 spec.
> Our responses and final decisions.
> Do NOT re-raise resolved points.

---

## Review Date: May 2026
## AIs: DeepSeek · Gemini · ChatGPT · Grok · Perplexity

---

## Point 1 — GitHub Token in PDF
**Raised by:** All AIs
**Concern:** Live token exposed in PDF is security risk.
**Resolution:** ACKNOWLEDGED — keeping token in docs temporarily.
Token needed for new Claude to auto-fetch code.
Will remove when averionbot.com launches publicly.
**Status:** ✅ Resolved — intentional decision

---

## Point 2 — Dead Coin Scenario
**Raised by:** ChatGPT · Grok
**Concern:** No max DCA levels means bot throws money at dead coins forever.
**Resolution:** LOCKED
- ST flag from exchange = ONLY forced close
- If exchange marks coin ST → auto sell immediately via CCXT
- Dead coins without ST flag = nothing we can do (position holds)
- Smart queue handles capital priority naturally
- User always controls their own exit
- Works on all 7 exchanges via CCXT
**Status:** ✅ Resolved — ST flag is the solution

---

## Point 3 — Reclassification Mid-Ladder
**Raised by:** Gemini
**Concern:** Reclassification could trigger phantom DCA buy at 3am.
**Resolution:** NOT A BUG
- Our trigger = percentage drop from last buy price (not fixed threshold)
- Price already dropped MORE than new spacing = DCA fires correctly at better price
- Market order at current price = always best available
- Smart queue rescores after every buy
- Gemini misunderstood our percentage-based trigger logic
**Status:** ✅ Resolved — not a bug in Averion

---

## Point 4 — Slippage on Microcaps
**Raised by:** Gemini · ChatGPT · Grok
**Concern:** Market orders on thin order books = massive slippage.
**Resolution:** LOCKED — new slippage handling rule:
1. DCA triggers → check order book depth
2. If available at target price >= $1 minimum → buy at target price
3. If available < $1 minimum → buy $1 market order
4. Maximum slippage exposure = $1 only
5. Never chase more than $1 above target
6. Always executes something — never stuck
7. ALL orders are market orders always
**Status:** ✅ Resolved — $1 max slippage rule locked

---

## Point 5 — State Machine Definition
**Raised by:** ChatGPT
**Concern:** No formal state machine = race conditions and bugs.
**Resolution:** NOT NEEDED for Averion
- Last buy price updates after every buy → next trigger always moves
- Cannot fire twice — percentage trigger naturally prevents duplicates
- Single sequential loop → no race conditions possible
- Smart queue rescores automatically after every action
- ChatGPT assumed complex multi-threaded system
- Averion uses single sequential loop — much simpler
**Status:** ✅ Resolved — not needed

---

## Point 6 — 3am Cron Staggering
**Raised by:** Gemini
**Concern:** All maintenance at 3am = massive I/O spike = DB lock risk.
**Resolution:** LOCKED — new staggered schedule:
- Every hour: health check + OHLCV + ATR
- 03:00 Infrastructure: CCXT upgrade · restart · backup
- 03:30 Data & Classification: CoinGecko · classify · recalculate · volume-weighted
- 04:00 Reporting: snapshot · metrics · markdown reports · Telegram
- 04:30 Sunday only: cleanup · disk · DB VACUUM · weekly report
**Status:** ✅ Resolved — schedule locked

---

## Point 7 — PAPER_MODE as Environment Variable
**Raised by:** DeepSeek
**Concern:** PAPER_MODE in config.py = accidental live trading risk.
**Resolution:** LOCKED
- PAPER_MODE moves to .env file (never in config.py)
- Default = true always (safe by default)
- 10 second countdown warning when switching to LIVE mode
- Red banner across full topbar in LIVE mode
- No conflict with customer paper trades (90-day auto-close handles that)
**Status:** ✅ Resolved — locked

---

## Point 8 — Reserve Wallet Blockchain Listener
**Raised by:** Gemini
**Concern:** No mechanism defined for detecting user deposits.
**Resolution:** LOCKED — use NOWPayments gateway
- 0.5% fee per deposit
- Unique address per user (no memo confusion)
- Funds auto-forward to owner USDT wallet
- TRC20 recommended (cheapest ~$1 network fee)
- $10 minimum top-up
- $5 free trial credit for new users
- Phase 7 start with NOWPayments → switch to HD wallet when scaling
**Status:** ✅ Resolved — NOWPayments locked for Phase 7

---

## Point 9 — Short DCA Mechanics
**Raised by:** ChatGPT · Perplexity
**Concern:** Short on spot exchanges undefined · may require margin.
**Resolution:** LOCKED
- Pure spot only — no margin · no borrowing · no leverage
- User must already hold the coin on exchange
- Only sell if quantity >= exchange minimum order size
- Profit coin = USDT or base coin — works for both Long and Short
- Works on all spot exchanges via CCXT
**Status:** ✅ Resolved — spot only locked

---

## Point 10 — Crash Detection
**Raised by:** All AIs
**Concern:** No crash detection defined (X% in Y minutes undefined).
**Resolution:** NOT NEEDED
- Smart queue IS the crash protection
- Queue executes ONE DCA at a time
- Capital depletes gradually — never dumps all at once
- Natural brake through capital limitation
- ST flag handles true emergencies
- Queue + capital limit = sufficient protection
- No special crash detection feature needed
**Status:** ✅ Resolved — smart queue handles it

---

## Points Deliberately Rejected

| Point | Reason |
|-------|--------|
| Add max DCA levels | Conflicts with Never Stuck philosophy |
| Use limit orders | Conflicts with market orders philosophy |
| Add high water mark | Intentional simplicity — monthly fresh start |
| 60s interval too slow | Intentional — DCA swing not scalping |
| One DCA per cycle too slow | Intentional — predictable over speed |
| PostgreSQL now | Phase 6 — not needed for MVP |
| Full AML/KYC now | Phase 7 — premature |
| Prometheus/Grafana | Not needed for personal bot |
| Geographic redundancy | Way too early |
| Referral 7-day change | Intentional lock — prevents abuse |

---

## Key Lesson From Reviews

When spec clearly explains:
- Percentage-based trigger (not fixed threshold)
- Last buy price always updates after every buy
- Single sequential loop (not multi-threaded)
- Smart queue scoring logic

AIs give relevant recommendations instead of wrong ones.
Clear spec = better AI advice.
This is why markdown documentation exists.
