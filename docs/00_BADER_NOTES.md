# Bader Personal Notes

> My thoughts · questions · ideas · reminders.
> Claude reads this and matches with project spec.
> Cross off items when discussed and locked.

---

## Ideas to Discuss

- [x] Daily Telegram report per exchange format
- [x] 3 customer Telegram channels (how customers connect)
- [x] Manual trade entry option in Smart bot
- [x] Manual bot type (separate from Smart)
- [x] PWA install hint with dismiss button
- [x] Short DCA two-way minimum calculation (done in Point 6)

---

## Questions I Have

- [x] How does multi-exchange work — one bot or multiple?
- [x] Can same bot trade on Binance AND MEXC?
- [x] What happens when user deletes a bot with open positions?

---

## Reminders

- [ ] Switch GitHub repo to private when averionbot.com launches
- [ ] Remove token from docs on launch day
- [ ] Generate new token and update .env on Hetzner

---

## Decisions Pending (Not Yet Locked)

- [x] Entry method promotion criteria (Point 7)
- [x] External service outage behavior (Point 11)
- [x] Data retention policy (Point 12)

---

## Recently Locked (Cross Check)

- [x] ST flag = only forced close
- [x] Slippage = $1 max market order
- [x] Short DCA = spot only · user must hold
- [x] Paper mode = unlimited virtual funds
- [x] Recovery buy = REMOVED
- [x] Reclassification = new positions only
- [x] TP recalculates after every buy
- [x] Exchange minimums = bot creates · trading holds
- [x] PAPER_MODE in .env default true
- [x] 3am cron staggered schedule
- [x] Health check every hour
- [x] NOWPayments for reserve wallet
- [x] Transfer threshold $10 admin adjustable
