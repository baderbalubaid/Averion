# Averion — Complete AI Review Brief
## Session 5 · June 2026

---

## What Averion Is

Automated crypto DCA trading platform.
Users connect exchange APIs · create bots · platform trades automatically.
20% performance fee on profits · reserve wallet system.
Currently: waiting for Hetzner server (ID verification pending).
Code: github.com/baderbalubaid/Averion (public)

---

## What Has Been Built and Locked Since Last Review

### 1. Research System V3 (FINAL)
26 entry methods (E1-E26) · 252 Long research bots
RARS scoring: 35/30/20/15 weighted additive
3 regime champions (Bull · Bear · Sideways)
3-tier promotion · bear circuit breaker 40%
Auto-switch toggle · weekly markdown report
docs/AI_RESEARCH_SYSTEM_BRIEF_FINAL.md

### 2. Coin Classification (FINAL)
5 categories by market cap
Per-coin independent spacing + TP + trailing
25/25/25/25 weighted rolling window
Cap protection: +10% max upward · immediate downward
Regime TP multiplier: 1.10/1.05/1.0/0.90/0.85
docs/COIN_CLASSIFICATION_BRIEF_FINAL.md

### 3. DCA Parameter System (FINAL)
Dynamic ATR scalar per coin volatility (1.2-3.0)
20% daily change limit spacing/TP · 10% size multiplier
10th-90th percentile own data ranges
Weighted median for spacing · trimmed mean for TP
docs/DCA_PARAMETER_SYSTEM_FINAL.md

### 4. Entry Methods (FINAL)
E1-E14 original + E15-E26 new:
E15: OBV Divergence
E16: RSI Divergence
E17: Liquidity Sweep Reversal
E18: ADX Trend Pullback
E19: Fibonacci Retracement
E20: VPOC Volume Profile
E21: Fair Value Gap
E22: Hammer/Engulfing at Support
E23: Relative Strength vs BTC
E24: Funding Rate Extreme
E25: Supertrend + RSI
E26: Ichimoku Cloud Simplified
Total: 252 bots + 5 benchmarks
docs/ENTRY_METHODS_BRIEF.md

### 5. Admin Dashboard (FINAL)
9 tabs:
Tab 1: Dashboard (alerts · overview · exchanges)
Tab 2: My Bots (queue per wallet · positions · history)
Tab 3: My Copy (mirrors · copy bots)
Tab 4: Research (252 bots · champions · reports)
Tab 5: Users (3-level dropdown · suspend · actions)
Tab 6: Health (server · cron · fetch · markdown export)
Tab 7: Trading (exchanges · classification · Smart DCA)
Tab 8: Controls (toggles · owner wallet · security)
Tab 9: System (password · settings · danger zone)
docs/ADMIN_DASHBOARD_FINAL.md

### 6. Customer Dashboard (FINAL)
3 tabs: Dashboard · Bots · Settings
Same structure as admin for consistency
Queue per wallet · bot detail 3 sub-tabs
Custom entry builder (up to 3 conditions)
History = closed trades only
docs/CUSTOMER_DASHBOARD_FINAL.md

### 7. Notifications (FINAL)
Customer: 1 Telegram chat + email
Admin: 3 separate Telegram channels
Long/Short same notification format
Profit in $ or coin based on bot setting
Types: TRADE · ALERT · INCOME · REPORT · EMAIL
docs/NOTIFICATIONS_FINAL.md

### 8. Reporting System (FINAL)
Excel removed · replaced with markdown
3 reports: Daily health · Weekly research · Monthly summary
All AI-ready: context header + attention section + notes blank
All pushed to GitHub · shareable via URL
docs/REPORTING_SYSTEM_FINAL.md

### 9. Pricing System (FINAL)
Free: unlimited exchanges · 5 bots · 100 trades max · 30 paper
$5 trial credit · 20% performance fee immediate
Add-ons: extra bots + trade bundles (prices TBD · DB controlled)
Billing: one-time default · auto-renewal opt-in · expiry shown
Referral: 2.5% of 20% fee forever · registration only
Reserve: $10 minimum · NOWPayments · TRC20/BEP20
docs/PRICING_FINAL.md

---

## Key Locked Rules (Summary)

| Topic | Rule |
|-------|------|
| RARS weights | 35/30/20/15 |
| Window weights | 25/25/25/25 equal |
| Regime TP mult | 1.10/1.05/1.0/0.90/0.85 |
| ATR scalar | 1.2-3.0 dynamic |
| Bear circuit breaker | 40% DD · live query · 30d cooldown |
| Trade limit | 100 hard cap · bundles raise it |
| Paper limit | 30 max · 90d auto-close |
| Referral | 2.5% of 20% fee |
| Billing | One-time default · opt-in renewal |
| Research bots | 252 total (E1-E26 + 5 benchmarks) |
| Entry methods | 26 total |
| Admin tabs | 9 tabs |
| Customer tabs | 3 tabs |
| Notifications | Customer: 1 chat · Admin: 3 channels |
| Excel | REMOVED · replaced with markdown |
| Long vs Short | Equal · same format · same features |
| DCA off then on | Queue handles · spacing from daily calc |
| Bot edit | New trades only · existing unchanged forever |

---

## 12 Questions for AI Review

1. Looking at ALL locked decisions together:
  Are there any CONFLICTS between systems?
  Example: research scoring vs DCA parameters vs classification

2. Are there any GAPS in the platform design?
  Features mentioned somewhere but never fully designed?

3. Security review:
  Bcrypt · Fernet split key · API validation · IP whitelist
  Is security comprehensive or did we miss anything critical?

4. Research system: 26 methods · 252 bots
  Any entry method that will NEVER fire in practice?
  Any method overlapping too much with another?
  Any method that cannot be calculated from hourly OHLCV?

5. Pricing system:
  Free: unlimited exchanges · 5 bots · 100 trades
  Is this sustainable for server costs?
  Too generous? Not generous enough for acquisition?

6. Admin dashboard 9 tabs:
  Anything critical missing that admin needs daily?

7. Customer dashboard 3 tabs:
  Anything missing that customer needs daily?
  Anything that would frustrate a customer?

8. Notification system:
  Any important notification we missed?
  Any that would be annoying or too frequent?

9. DCA parameter system:
  25/25/25/25 weighted window · per-coin independent
  Any edge case that breaks the calculation?
  Any coin behavior not handled?

10. Overall platform readiness:
   TOP 3 things most likely to fail on Day 1 live trading?
   What must be fixed before going live?

11. What is completely missing that a serious
   DCA trading platform MUST have?
   Any feature competitors have that we lack?

12. If you were a customer using this platform:
   What would frustrate you most?
   What would impress you most?
   Would you pay for it?
