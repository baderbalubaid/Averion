# Averion — AI Review Brief
## Session 7 · June 2026 · All Decisions Locked

---

## HOW TO USE THIS DOCUMENT

This is a review brief for Averion — a crypto DCA trading platform.
Read this + the full spec at:
https://raw.githubusercontent.com/baderbalubaid/Averion/main/averion_COMPLETE.md

Focus: find conflicts · gaps · Day 1 crash risks · missing features.
All locked decisions are FINAL unless a critical conflict is found.

---

## PLATFORM SUMMARY

Averion: automated crypto DCA trading platform
Users: connect exchange API · create bots · platform trades automatically
Fee: 20% performance fee on profits only · no monthly subscription
Exchanges: Binance · MEXC · KuCoin · OKX · Bybit · Gate.io · Bitget
Status: waiting for Hetzner server · paper trading first
GitHub: github.com/baderbalubaid/Averion (public · going private at launch)

---

## CORE PHILOSOPHY (LOCKED · NEVER CHANGE)

1. Survivability first · recovery second · profit third
2. TP always fires (no exceptions ever)
3. DCA always continues (no exceptions ever)
4. Bot never stops trying (keeps retrying every 60s)
5. Set and forget (user deposits · walks away · collects profit)
6. Non-custodial (funds stay on user's exchange always)

---

## KEY LOCKED DECISIONS

### Trading System
Direction: Long DCA + Short DCA (both Day 1)
Order types:
  Long: entry=MARKET · DCA=MARKET · TP=MARKET
  Short: entry=MARKET · DCA=MARKET · buyback=LIMIT only
Trailing: Long only (Short uses fixed limit buyback)
Spacing: per-coin independent (from own 90-day OHLCV data)
TP: per-coin independent + regime multiplier
Window: 25/25/25/25 equal weighted rolling

### Market Regime
5 signals scored daily at 04:30
Scale: -7 to +7
Strong Bull ≥+5 · Bull +2 to +4 · Sideways -1 to +1
Bear -2 to -4 · Strong Bear ≤-5

Long regime multipliers:  1.10 / 1.05 / 1.00 / 0.90 / 0.85
Short regime multipliers: 0.85 / 0.90 / 1.00 / 1.05 / 1.10 (reversed)

### Research System
Long: 261 bots (E1-E26 + E18b + 5 benchmarks) · all coins
Short: 1,305 bots (261 × 5 coins: BTC·ETH·BNB·SOL·XRP)
Total Day 3: 1,566 bot instances
Short research: virtual coin balance (no real coins needed)
Champions: 3 Long (Bull/Bear/Sideways) + 3 Short (independent)
RARS: 35/30/20/15 weighted additive
Promotion: 3-tier system · 4 weeks consecutive

### Reserve Wallet
Minimum deposit: $10
Minimum to trade: NONE (any balance > $0)
When balance = $0: new trades pause only
DCA: always continues regardless of balance
TP: always fires regardless of balance
No debt cap (removed · DCA+TP help recovery)
Auto-resume: when balance > $0 after top-up

### Order Types (FINAL)
Long entry: MARKET
Long DCA: MARKET
Long TP: MARKET (bot detects price · sells immediately)
Short entry: MARKET
Short DCA: MARKET
Short buyback: LIMIT only (reserves USDT · exact price)
ST flag: MARKET (emergency · no choice)
Manual close: MARKET (immediate · no choice)
Trailing: Long only (Short = fixed limit price)

### Infrastructure
Server: Hetzner CX33 from Day 1 (€17.99/mo)
Loop: asyncio single process (LOOP_MODE=asyncio)
PM2: 2 processes (live_loop.py + research_loop.py)
Switch to 7 workers: manual only · never auto
Floating IP: mandatory Day 1 (€3.71/mo)
DB: PostgreSQL + pgBouncer
Cache: Redis (shared prices between processes)
Expected loop: 4-6s (asyncio parallel)

### Coin Selection (Bot Wizard)
Long: ALL COINS · TOP X (10/25/50/100/200) · SPECIFIC
Short: SPECIFIC COIN only (must hold coin)
TOP X: updated daily · dropped coin = existing position continues

### Registration
Steps: username · email · password · confirm · verify email
Phone: optional · admin-triggered only when suspicious
Exchange UID fingerprint: silent · automatic · invisible
Telegram: optional · notifications only

### Data Retention
Trades: 3 years → anonymize → delete year 5
Research scores: 2 years → trim → delete
Financial records: 5 years → anonymize
Logs: 30 days
DB stabilizes: 5-10GB max forever
Tax report: auto-generated January 1st yearly

### Payments
NOWPayments: Custody mode
Addresses: permanent per user (save in Trust Wallet)
Networks: TRC20 · BEP20 (no ERC20)
Fee: 0.5% (user pays)
No monthly cost to platform

### Copy Trade
Follow user: spacing · DCA · TP exactly
Exception: user closes at loss → standalone Smart DCA
Order size: fixed $ (your setting)
Toggle: per bot [Follow ON/OFF] default ON
Remove exchange: all copies → standalone Smart DCA

---

## DOCUMENT SIZES

averion_COMPLETE.md:      22,374 lines (master)
13_LOCKED_DECISIONS.md:    5,751 lines (all decisions)
ADMIN_MANUAL.md:             319 lines (owner guide)
FAILURE_SCENARIOS.md:        194 lines (crash recovery)
PUBLIC_LAUNCH_FINAL.md:      347 lines (launch plan)
TERMS_OF_SERVICE.md:         205 lines
PRIVACY_POLICY.md:           149 lines
RISK_DISCLOSURE.md:          148 lines
ACCEPTABLE_USE_POLICY.md:     65 lines
schema.sql:                  952 lines
DAY1_CHECKLIST.md:           243 lines
research_bots.json:        1,767 lines (261 bots)

---

## QUESTIONS FOR AI REVIEW

### Set 1: Conflicts
1. Are there any conflicts between locked decisions?
2. Does any decision contradict another?
3. Which conflicts would cause Day 1 crashes?

### Set 2: Trading Logic
4. Is the Short DCA logic complete and correct?
5. Does the reserve wallet logic make sense?
   (balance=0 → new trades pause · DCA+TP always continue)
6. Is the order type decision correct?
   (Market always except Short buyback = Limit)
7. Any edge cases in trading not handled?

### Set 3: Research System
8. Is 1,566 bots (261 Long + 1,305 Short) realistic on CX33?
9. Is RARS formula complete for both Long and Short?
10. Are Short regime multipliers correct (reversed from Long)?

### Set 4: Infrastructure
11. Is asyncio sufficient for 1,566 research bots?
12. Is Floating IP setup correctly described?
13. Any crash scenario not covered in FAILURE_SCENARIOS.md?

### Set 5: Customer Experience
14. Is the bot wizard (10 steps) complete?
15. Is onboarding flow (4 steps) missing anything?
16. Is position detail screen sufficient?

### Set 6: Security
17. Are legal documents complete for initial launch?
18. Is registration anti-fraud sufficient?
19. Any security gap that would be exploited immediately?

### Set 7: Day 1 Readiness
20. TOP 3 things most likely to fail on Day 1?
21. What MUST be fixed before any live trading?
22. Is DAY1_CHECKLIST.md complete?

---

## WHAT NOT TO SUGGEST

Do NOT suggest:
→ Stop loss feature (against platform philosophy)
→ Grid bots or futures trading
→ Copy trading changes (already fully spec'd)
→ Changing from Hetzner to AWS/GCP
→ Adding more entry methods (261 is enough)
→ Changing fee structure (20% locked forever)
→ TOTP/2FA at launch (Telegram sufficient)
→ Stripe payments (NOWPayments only)
→ Native mobile app (PWA sufficient for launch)
