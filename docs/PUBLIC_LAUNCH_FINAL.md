## Averion Public Launch Plan — Final (LOCKED)

---

## 1. Launch Philosophy

No fixed timeline · quality over speed.
Personal use first → find bugs naturally.
Soft launch → few trusted users.
Public launch → when platform is proven stable.
Target: few customers in first year · not hundreds.
One person support (owner) · Telegram + email.

---

## 2. Natural Timeline

Phase 4 (Now):
→ Hetzner server setup
→ Paper trading 24/7
→ 261 research bots collecting data
→ Owner using platform personally
→ Fix bugs as discovered naturally

Phase 5 (Month 2-3):
→ Paper stable 30+ days
→ Live trading (owner personally · small amounts)
→ Short DCA implementation
→ All exchanges live simultaneously

Phase 6 (Month 4-6):
→ Live stable 30+ days
→ First trusted customers (friends · family)
→ Word of mouth only
→ Fix issues with real users

Research Champion Timeline:
→ 50 trades per method = confidence gate
→ ~3-6 months depending on market activity
→ When all methods have 50+ trades:
  Tier 1 promotion starts (4 consecutive weeks)
  Champion promoted automatically
  Smart DCA auto-switch enabled
→ Platform fully automatic from this point
→ Research improves champion continuously
→ Owner just monitors health reports

Phase 7 (Month 6-12 · when champion determined):
→ Soft public launch
→ Reddit + X marketing (organic only)
→ averionbot.com fully live
→ Full landing page
→ Legal documents published
→ Platform proven · champion active

No rush · no deadline · launch when ready ✅

---

## 3. Security Checklist Before Public Launch

### Code Security:
□ Switch GitHub repo to PRIVATE
□ Remove ALL tokens from any file
□ Generate new GITHUB_TOKEN · update .env
□ Remove admin URL from all docs
□ Verify no secrets in git history

### Encryption:
□ Split Fernet key (Day 2 Hetzner)
  Part A: .env on server
  Part B: Hetzner Secrets API
□ Monthly rotation confirmed working
□ All user API keys encrypted + verified

### Authentication:
□ bcrypt on all passwords (verified)
□ Rate limiting on all endpoints
□ Session token hashing (Phase 6)
□ CSP headers in Nginx
□ CSRF protection added
□ JWT refresh mechanism working
□ Brute force protection tested (5 attempts → lockout)

### Infrastructure:
□ SSH hardening (port 2847 · no root · keys only)
□ UFW firewall (default deny)
□ Fail2ban active
□ UptimeRobot monitoring (5 min interval)
□ Daily DB backup tested + verified
□ Disaster recovery tested (restore from backup)
□ Staging branch tested before main

### Before First Customer:
□ Paper trading 30+ days stable
□ Live trading 30+ days stable (owner personal)
□ Zero critical bugs open
□ All 7 exchanges tested + verified
□ Security audit log working
□ All Telegram channels working (admin 3 channels)
□ Customer Telegram (@AverionBot) working
□ Email (Resend) working + deliverability verified
□ NOWPayments tested (test deposit)
□ Owner wallet transfer tested

---

## 4. Stripe Removed (LOCKED)

NOWPayments only · forever at this scale.
Crypto payments = simpler · no chargebacks
No bank issues · no KYC required
No Stripe = no fiat complexity
Removed from all phases

---

## 5. Support Plan

Owner only · no hiring needed at start.
Primary: Telegram (fast · personal)
Secondary: Email support@averionbot.com
Response time: best effort · within 24h
When growing: add Telegram group for users

Telegram support flow:
Customer messages @AverionBot or support handle
Owner responds personally
Fix issues same day if critical
Document recurring issues → add to FAQ

---

## 6. Marketing Plan (Organic Only)

### Accounts to create:
□ @AverionBot on X (Twitter)
□ u/AverionBot on Reddit
□ averionbot.com domain

### Reddit communities:
r/CryptoCurrency
r/algotrading
r/CryptoTechnology
r/binance · r/kucoin · r/mexc · r/bybit

### X (Twitter) strategy:
→ Post weekly research results
→ Share champion performance data
→ Transparent · data-driven posts
→ "Our bot publishes research publicly" angle
→ No paid ads · organic only

### Unique marketing angles:
1. Performance fee only = we profit when you profit
  No monthly fee trap
  Aligned incentives = trust

2. Public research system = transparent
  Weekly results pushed to GitHub
  Any AI can verify our claims
  No other platform does this

3. Set and forget = truly automated
  TP always on · auto-resume · true DCA philosophy
  Deposit and walk away

4. 26 entry methods tested simultaneously
  Data-driven champion selection
  Not guessing · not marketing claims · real data

---

## 7. Legal Documents (Owner Writes · AI Helps)

### Documents needed before public launch:
1. Terms of Service
2. Privacy Policy (GDPR aware)
3. Risk Disclosure
4. Cookie Policy (minimal)

### Key points to include:

Terms of Service:
→ Platform is a tool · not financial advice
→ User responsible for own trading decisions
→ 20% performance fee on profitable trades
→ Reserve wallet non-refundable
→ Platform can suspend abusive accounts
→ Disputes: email support@averionbot.com

Risk Disclosure:
→ Crypto trading involves significant risk
→ Past performance not indicative of future results
→ Never trade with funds you cannot afford to lose
→ DCA does not guarantee profit
→ Exchange risks (hacks · downtime · delisting)
→ Platform not responsible for exchange failures

Privacy Policy:
→ What data we collect (email · phone · trade data)
→ How we store it (encrypted · Hetzner EU server)
→ No selling data to third parties
→ GDPR rights (access · delete · export)
→ Retention policy (trade history forever · logs 90 days)

### No registration required at start:
→ No blocked countries initially
→ When scaling → get lawyer review
→ For now → standard template language

---

## 8. Branding

### Owner arranges:
□ Logo design
□ Color scheme
□ Brand identity

### AI writes (landing page content):
□ Hero section: "Automated DCA · Set and Forget"
□ How it works (3 simple steps)
□ Supported exchanges (7 logos)
□ Pricing section (free + add-ons)
□ Research system explainer
□ Performance fee model
□ FAQ section
□ [Get Started] CTA button

---

## 9. Server Cost Testing Plan

After Hetzner live · run 261 research bots 7 days.

Monitor daily (Health Report):
→ CPU avg + max
→ RAM avg + max
→ Loop time avg + max
→ DB size growth per day
→ Network traffic

After 7 days:
→ Share health report markdown with Claude
→ Claude calculates:
  Cost per user estimate
  When to upgrade (CX23 → CX33 at €17.99/mo)
  When to upgrade further
  Projected costs at 10/50/100/500 users

Upgrade triggers:
→ CPU avg > 60% for 7 days → upgrade
→ RAM avg > 3GB for 7 days → upgrade
→ Loop avg > 15s for 7 days → upgrade
→ Any one trigger sufficient → upgrade

---

## 10. Monitoring Stack

### Always running:
UptimeRobot: ping every 5 minutes
→ Alert if down > 1 minute
→ Email + Telegram alert

Admin Telegram Channel 3: daily digest
→ Cron results
→ Server health
→ Loop time
→ Error count

Health Report: daily at 05:00
→ Pushed to GitHub
→ 30-day rolling data
→ AI-ready format

### Alert thresholds (Hetzner CX23):
CPU: >70% warning · >85% critical
RAM: >3GB warning · >3.5GB critical
Loop: >15s warning · >30s critical
Disk: >80% warning · >90% critical
DB backup: fail → immediate critical alert

---

## 11. GitHub Privacy Switch

Currently: PUBLIC (useful for AI reviews)
Switch to PRIVATE when:
→ averionbot.com domain registered AND
→ First real customer about to sign up

Command:
Go to GitHub repo settings → Change visibility → Private
Then: generate new GITHUB_TOKEN · update .env
Remove old token from everywhere

Keep private forever after launch.

---

## 12. NOWPayments Setup (Phase 7)

Already locked:
→ Unique address per user
→ Auto-forward to owner wallet
→ Webhook → instant credit
→ TRC20 + BEP20 only (not ERC20)
→ Minimum deposit: $10
→ 0.5% fee per deposit

Test before launch:
□ Create NOWPayments account
□ Generate test API key
□ Test deposit flow end to end
□ Verify webhook fires correctly
□ Verify balance credited immediately
□ Verify owner wallet receives funds
□ Test with real $1 deposit

---

## 13. Fernet Key Security (LOCKED)

Most dangerous secret in platform.
Encrypts ALL user exchange API keys.
Compromised = attacker can access all exchanges.

Split key protection:
Part A: .env on Hetzner server
Part B: Hetzner Secrets API (separate system)
Both needed to decrypt anything.

Rotation: monthly automatic
→ rotate_fernet.py runs 1st of month
→ New key generated
→ All API keys re-encrypted
→ Both parts updated
→ PM2 restart
→ Telegram notification
→ Old key = useless after rotation

Security: attacker needs server + Hetzner account
Even if both compromised: 30 day maximum window
Then rotation makes key useless
Nearly impossible to exploit ✅
