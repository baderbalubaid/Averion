# Business Model

> How Averion makes money.
> All rules here are LOCKED unless explicitly discussed with Bader.

---

## Performance Fee

- Rate = 20% of realized profits only
- Realized = fully closed positions only
- Open positions = NOT counted ever
- Loss months = $0 fee — no charge — no rollover
- No high water mark — every month starts fresh
- Fee deducted automatically from reserve wallet per winning trade

---

## Fee Examples

| Month | Realized P&L | Fee 20% | Result |
|-------|-------------|---------|--------|
| January | +$500 | $100 | Deducted from reserve ✅ |
| February | -$200 | $0 | No charge — loss month ✅ |
| March | +$300 | $60 | Deducted from reserve ✅ |
| April | $0 | $0 | No closed trades — no charge ✅ |
| May | +$1,200 | $240 | Deducted from reserve ✅ |

---

## Account Types

| Type | Fee | Reserve Needed | Notes |
|------|-----|---------------|-------|
| Regular customer | 20% | Yes | Standard |
| 0% account | 0% | No | Relatives · selected by admin |
| Admin account | 0% | No | All income to owner wallet |

---

## Reserve Wallet System (LOCKED)

### Concept
User deposits USDT into reserve wallet.
Bot trades using exchange funds — reserve not touched for trading.
After each winning trade → 20% fee auto-deducted from reserve.
True set and forget — no monthly invoices.

### How It Works
1. User deposits $10 USDT to their reserve wallet
2. Bot trades normally using exchange funds
3. Winning trade closes — profit $1.00 — fee $0.20
4. $0.20 auto-deducted from reserve → balance $9.80
5. Loss trade closes → $0 deducted → reserve untouched
6. Reserve reaches $0 → new positions pause
7. User tops up → bot resumes within 60 seconds

### Reserve Alerts
- Balance < $5.00 → ⚠️ Telegram warning
- Balance < $2.00 → 🔴 Telegram critical
- Balance = $0 → ❌ New positions paused · Telegram alert
- After top-up → ✅ Bot resumed automatically

### Networks
- TRC20 (Tron) recommended — cheapest ~$1 per transaction
- BEP20 (BSC) alternative — ~$0.50 per transaction
- ERC20 NOT supported — too expensive ($10-30 per transaction)

### Minimum Top-Up
- $10 minimum — prevents micro-deposits
- $5 free trial credit for new users (real trading · no card needed)

---

## NOWPayments Integration (LOCKED)

- Gateway: NOWPayments (0.5% fee per deposit)
- Unique address per user — no memo confusion
- Funds auto-forward to owner USDT wallet (non-custodial mode)
- Webhook notification = instant credit to user balance
- No manual action needed — fully automatic
- Start Phase 7 with NOWPayments → switch to HD wallet when scaling

---

## Owner Wallet — Fee Collection

### Transfer Rules (LOCKED)
- Fees accumulate in DB — not transferred daily
- Auto-transfer when accumulated >= threshold
- Default threshold = $10 (admin adjustable in panel)
- Month-end force transfer regardless of threshold
- Transfer via TRC20 (cheapest network fees)
- [Transfer Now] button in admin panel for manual transfer

### Admin Panel — Owner Wallet Section
- Your wallet address TRC20 + BEP20 (editable)
- Transfer threshold (adjustable anytime)
- Pending balance display
- Transfer history log
- [Transfer Now] button

---

## Referral System (LOCKED)

### How It Works
- Rate = 3% of the 20% performance fee → referrer reserve wallet
- Duration = forever — no time limit
- Referred user still pays full 20% — no discount ever

### Math Example
- Ahmed makes $1,000 profit
- Ahmed pays $200 fee (20%)
- Khalid (referrer) gets $6.00 (3% of $200)
- Owner gets $194.00 (97% of $200)

### Rules
- Code entered at registration ONLY — cannot add or change after
- Regular customers always pay 20% — referral invisible to them
- Self-referral blocked by anti-fraud system
- Loss months = $0 referral income (correct)
- 0% accounts = $0 fee = $0 referral income
- Referrer deleted → referred user reverts to normal 20% to owner

---

## Anti-Fraud System — 5 Layers

| Layer | Method | Catches |
|-------|--------|---------|
| 1 | Email + Phone KYC | Duplicate identities |
| 2 | Exchange API UID fingerprint | Same exchange account |
| 3 | Stripe payment method | Same card/bank |
| 4 | IP + Device fingerprint | Same device (admin review) |
| 5 | Cross-exchange blacklist | All exchanges blocked |

Layer 2 most powerful: Exchange UID never changes even with new API keys.

---

## Future Monetization

- Phase 8: Strategy Marketplace
- Signal providers listed with verified track record
- One-click subscribe → webhook auto-connected
- Averion takes 10-15% subscription fee + 20% performance fee
- Provider vetting: >55% win rate · >6 months history · <30% drawdown
