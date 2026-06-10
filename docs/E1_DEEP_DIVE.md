# Averion E1 Deep Dive Report
> Generated: 2026-06-10 16:32 · Paper trading · MEXC

---

## E1 — RSI Oversold + VWAP Drop + ATR Spike + Bounce

**Strategy logic:** Buy when RSI below threshold, price dropped X% below VWAP, ATR spikes, bounce recovery confirmed.

## Parameter Variants

| Bot | ATR Mult | VWAP% | Bounce% | RSI Threshold |
|-----|----------|-------|---------|---------------|
| E1-1 | 1.5 | 4.0% | 65% | 25 |
| E1-10 | 1.3 | 3.0% | 65% | 30 |
| E1-11 | 1.5 | 3.0% | 55% | 30 |
| E1-12 | 1.3 | 2.0% | 55% | 35 |
| E1-2 | 1.5 | 4.0% | 65% | 30 |
| E1-3 | 1.5 | 4.0% | 65% | 35 |
| E1-4 | 1.5 | 3.0% | 65% | 25 |
| E1-5 | 1.5 | 3.0% | 65% | 30 |
| E1-6 | 1.5 | 3.0% | 65% | 35 |
| E1-7 | 1.5 | 2.0% | 65% | 25 |
| E1-8 | 1.5 | 2.0% | 65% | 30 |
| E1-9 | 1.5 | 2.0% | 65% | 35 |

## Overall Performance

| Metric | Value |
|--------|-------|
| Total positions | 67 |
| Currently open | 60 |
| Closed trades | 7 |
| Win rate | 100.0% |
| Avg P&L per trade | $6.04 |
| Total P&L | $42.29 |
| Best trade | $6.04 |
| Worst trade | $6.04 |
| Avg DCA needed | 1.00 |
| Avg hold time | 3.6h |

## Per-Bot Performance

| Bot | Closed | Win% | Avg P&L | Total P&L | Avg DCA | Hold | Open Now |
|-----|--------|------|---------|-----------|---------|------|----------|
| E1-3 | 1 | 100.0% | $6.04 | $6.04 | 1.00 | 3.6h | 5 |
| E1-7 | 1 | 100.0% | $6.04 | $6.04 | 1.00 | 3.6h | 5 |
| E1-5 | 1 | 100.0% | $6.04 | $6.04 | 1.00 | 3.6h | 5 |
| E1-9 | 1 | 100.0% | $6.04 | $6.04 | 1.00 | 3.6h | 5 |
| E1-6 | 1 | 100.0% | $6.04 | $6.04 | 1.00 | 3.6h | 5 |
| E1-10 | 1 | 100.0% | $6.04 | $6.04 | 1.00 | 3.6h | 5 |
| E1-8 | 1 | 100.0% | $6.04 | $6.04 | 1.00 | 3.6h | 5 |
| E1-11 | 0 | 0% | $None | $None | None | Noneh | 5 |
| E1-2 | 0 | 0% | $None | $None | None | Noneh | 5 |
| E1-1 | 0 | 0% | $None | $None | None | Noneh | 5 |
| E1-12 | 0 | 0% | $None | $None | None | Noneh | 5 |
| E1-4 | 0 | 0% | $None | $None | None | Noneh | 5 |

## Top 15 Coins for E1

| Coin | Category | Trades | Avg P&L | Total P&L | Avg DCA |
|------|----------|--------|---------|-----------|----------|
| PVT | micro | 7 | $6.04 | $42.29 | 1.00 |

## Questions for AI Analysis

1. Which parameter combo (ATR/VWAP/Bounce/RSI) shows best edge?
2. Is tighter RSI (25) better than looser (35)?
3. Does larger VWAP drop (4%) filter better than smaller (2%)?
4. Which coin categories respond best to E1?
5. What parameter changes would you recommend?
6. Any signs of overfitting or luck?
