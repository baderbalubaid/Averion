## Averion Pricing System — Final (LOCKED)

---

## 1. Free Tier (Forever)

Every registered user gets:
- Unlimited exchange connections
- 5 bots total (across all exchanges)
- 100 open trades MAX (hard cap · always)
- 30 paper trades max (server cost · 0 profit)
- Long + Short DCA both included equally
- $5 trial credit on registration (real trading)
- 20% performance fee on profitable trades

Paper trade rules:
- 30 max per customer always
- After 90 days no live trade → auto-close all paper trades
- Reason: consumes server · platform gets 0 profit
- Forgotten forever without auto-close

Trade limit clarification:
- 100 open trades = hard cap · not a bundle
- No trades included in free tier beyond the 100 cap
- Want more than 100 open simultaneously → buy bundle

---

## 2. Add-On Products

Stored in DB table: platform_pricing
Admin changes prices/adds products anytime · zero code changes.

| Product ID | Name | Type | Description |
|-----------|------|------|-------------|
| BOT_SLOT | Extra Bot Slot | monthly | 1 additional bot slot |
| BUNDLE_200 | Trade Bundle 200 | monthly | Raises open trade limit to 200 |
| BUNDLE_500 | Trade Bundle 500 | monthly | Raises open trade limit to 500 |
| BUNDLE_1000 | Trade Bundle 1000 | monthly | Raises open trade limit to 1000 |
| BUNDLE_UNLIMITED | Unlimited Trades | monthly | No open trade limit |

Prices: TBD · admin sets in dashboard · changeable anytime

Admin can:
→ Change any price anytime
→ Add new bundle anytime
→ Remove bundle anytime
→ Rename any product anytime
→ Zero code changes needed ever

---

## 3. Billing Rules

### Default = One-Time (LOCKED)
Customer buys product → pays for 30 days
Expiry date shown clearly: "Expires: July 3 2026"
When expires → product deactivates
Bot expires → existing positions continue to TP · no new positions
Customer must manually renew

### Auto-Renewal = Opt-In Only (LOCKED)
Default is always OFF
Customer manually switches ON per product
When ON → deducts from reserve 1 day before expiry
Customer can switch back OFF anytime

### Customer View Per Item:
Extra Bot · Expires July 3 2026
[Renew $X] [Auto-renewal: OFF ↔ ON]

Trade Bundle 500 · Expires July 3 2026
[Renew $X] [Auto-renewal: OFF ↔ ON]

### Reminders:
Telegram alert 3 days before expiry (always)
Both one-time and auto-renewal users notified
If reserve insufficient for auto-renewal:
→ Item expires · user notified
→ Existing positions continue to TP

### Deduction:
From reserve wallet always
Bot/bundle fees: on purchase date or renewal date
Performance fee: immediately on every profitable trade

---

## 4. Performance Fee (LOCKED)

Rate: 20% of net profit
Timing: immediate after every profitable trade closes
Net profit: realized profit after exchange trading fees
Loss trades: $0 fee always · never charged on losses
Fee debt: if reserve empty when fee due → debt recorded
Debt cleared: next time user tops up reserve

---

## 5. Referral System (LOCKED)

Rate: 2.5% of 20% performance fee → referrer reserve wallet
Duration: forever · no time limit
Referral math:
 User profit: $1,000
 Fee: $200 (20%)
 Referrer gets: $5.00 (2.5% of $200)
 Owner gets: $195.00 (97.5% of $200)

Rules:
→ Code entered at registration ONLY
→ Cannot add or change after registration
→ Referred user always pays full 20% (referral invisible)
→ Self-referral blocked by anti-fraud
→ Loss trades = $0 referral income
→ Referrer deleted → owner gets full 20%

---

## 6. Reserve Wallet (LOCKED)

Purpose: holds customer funds for fee payments
Minimum top-up: $10
Gateway: NOWPayments (0.5% fee per deposit)
Networks: TRC20 · BEP20 (ERC20 not supported · too expensive)
No withdrawal: funds used for trading fees only

Fee payment order (when reserve deducted):
1. Performance fees (immediate on trade close)
2. Bot slot fees (on purchase/renewal date)
3. Trade bundle fees (on purchase/renewal date)

If reserve insufficient:
→ Fee debt recorded (performance fee)
→ Product expires (bot/bundle)
→ Existing positions continue to TP
→ No new positions until topped up

---

## 7. Owner Wallet (LOCKED)

Definition: your personal real USDT crypto wallet
Where platform fees are sent to (outside platform)

Flow:
User pays fee → accumulates in platform DB
When total >= $10 threshold → auto-sends to your TRC20 address
Month-end: force transfer regardless of threshold

Admin dashboard shows:
→ Pending accumulated fees
→ Transfer threshold (adjustable)
→ Your wallet addresses (TRC20 · BEP20)
→ Transfer history
→ [Transfer Now] manual button

---

## 8. Anti-Fraud (LOCKED)

5 layers:
1. Email + phone verification
2. Exchange API UID fingerprint (most powerful)
3. Reserve wallet minimum $10
4. IP + device fingerprint
5. Cross-exchange blacklist

Layer 2 detail:
Exchange UID never changes even with new API keys
Same exchange account cannot be added twice
Cannot bypass without new exchange account (requires exchange KYC)

---

## 9. Future Monetization (Phase 8)

Strategy Marketplace:
→ Signal providers with verified track record
→ >55% win rate · >6 months history · <30% drawdown
→ One-click subscribe
→ Averion takes 10-15% subscription + 20% performance fee
→ Prices TBD at Phase 8
