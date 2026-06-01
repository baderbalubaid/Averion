# Bot Creation Wizard

> 7-step wizard for creating new bots.
> Accessed from Bots tab + Create Bot button.

---

## Overview

- 7 steps total
- Back button available at any step
- Warnings shown in amber
- Errors shown in red (cannot launch until fixed)

---

## Step 1 — Basic Setup

| Field | Type | Notes |
|-------|------|-------|
| Bot Name | Text input | User defined |
| Exchange | Dropdown | Pre-filled from selected exchange |
| Direction | Radio | Long or Short |

### Short DCA Requirements
- User must already hold the coin on exchange
- Bot checks holdings before opening position
- Only sells if quantity >= exchange minimum order size

---

## Step 2 — Trading Method

| Method | Description |
|--------|-------------|
| Smart DCA | Fully automated · recommended default |
| ASAP | Opens immediately on any qualifying coin |
| Mean-Reversion | RSI + VWAP + ATR + bounce probability |
| TradingView | External signal via webhook |

### Smart DCA
- Coin selection: All / Top X by volume / Custom list
- All parameters automated from 90-day data

### Mean-Reversion
- Auto — qualifying coins only
- All 4 conditions must be true simultaneously

---

## Step 3 — Order Settings

| Field | Default | Notes |
|-------|---------|-------|
| Base Order ($) | 1.00 | Validated against exchange minimum |
| Quote Currency | USDT or BTC | Selected at bot creation · cannot change |
| Entry Order Type | Market | Market or Limit · user selects |
| DCA Order Type | Market | Market or Limit · user selects |

### Order Type Rules
- Market entry + Market DCA: standard behavior
- Limit entry: places limit buy at current price · waits for fill
- Limit DCA: places limit buy at DCA trigger price · next level only
- Trailing TP: auto-hidden when Limit DCA selected (not compatible)
- Can switch Market/Limit ON/OFF anytime · even mid-trade
- Limit ON: bot places limit order on exchange immediately
- Limit OFF: cancels all pending limit orders · USDT returned to wallet

### Limit DCA Partial Fill Behavior
- $10 DCA · $2 fills → avg cost + TP recalculate
- $7.50 more fills → avg cost + TP recalculate again
- $0.50 remaining < minimum order → added to next DCA level
- TP fires → pending limit cancelled → USDT freed automatically

---

## Step 4 — DCA Settings

### Smart DCA
- All automated · no manual input needed
- Category auto-detected from coin market cap
- Confidence level shown per coin

### Manual Methods (ASAP · Mean-Reversion · TradingView)
| Field | Notes |
|-------|-------|
| DCA Trigger % | % drop from last buy price to fire DCA |
| Spacing Multiplier | Each level widens by this factor |
| Size Multiplier | Each level size increases by this factor |

### Trade Volume Settings
| Field | Default | Notes |
|-------|---------|-------|
| Trades per Bot | 1 | Max concurrent open trades from this bot |
| Trades per Coin | 1 | How many times same coin repeats in this bot |

### Sequential Trade Gates
Controls when next trade on same coin opens:

| Gate | Default | Notes |
|------|---------|-------|
| DCA Trigger Gate | OFF | Opens next trade when current hits DCA level |
| Timer Gate | OFF | Opens next trade after X hours from last opened |
| Timer Hours | 5 | Hours to wait before opening next trade |

Gate rules:
- Both OFF: only 1 trade per coin (default)
- DCA trigger ON: next trade opens when current position hits DCA
- Timer ON: next trade opens after X hours from last opened trade
- Both ON: whichever comes first opens next trade
- Last opened trade = always the gate reference
- When reference closes → previous becomes reference → sequence continues
- Can switch ON/OFF anytime · even mid-trade

Example:
Trades per bot: 20 · Trades per coin: 3 · Gate: both (DCA + 5h)
→ Bot opens max 20 trades total across all coins
→ Any single coin max 3 concurrent trades
→ Each coin's trades open sequentially via gate
→ All trades use same bot parameters

---

## Step 5 — Profit Settings

### Smart DCA
- TP Mode: Auto (recommended) or Manual
- If Manual: warning shown if TP% - Trail% < 1%
- Trailing safety enforced automatically
- Trailing TP hidden if Limit DCA selected

### Manual Methods
| Field | Default | Notes |
|-------|---------|-------|
| Take Profit % | 5.0 | % above avg cost to arm trailing |
| Trailing % | 2.0 | % pullback from peak to sell |

Note: Trailing % field hidden when Limit DCA mode ON

### Profit Currency
- USDT: sell all coin → receive USDT
- Base coin: keep profit as the coin itself
- Works for both Long and Short

---

## Step 6 — Safety Settings

| Field | Default | Notes |
|-------|---------|-------|
| Reserve Floor ($) | 50.00 | Minimum USDT always untouched |
| Resume Threshold ($) | 75.00 | Must be higher than floor |
| Auto-Resume | ON | Restores bot automatically |
| Min Daily Volume ($) | 100,000 | Skips illiquid coins |

---

## Step 7 — Review and Launch

- Full summary of all settings shown
- Amber warnings (e.g. low balance)
- Red errors (cannot launch until fixed)
- Coin confidence breakdown: New X · Learning Y · Calibrated Z
- Minimum order size warnings per coin:
  ✅ Will trade · ⚠️ Needs more funds · ❌ Cannot trade
- Back button to any previous step
- Launch Bot button

### Pre-Launch Checks
- Exchange connected and API valid
- Sufficient balance for at least 1 base order
- Reserve floor < resume threshold
- At least 1 coin qualifies for this bot
- If trades per coin > 1: gate settings configured

---

## Duplicate Bot Feature

- Available in Bots tab kebab menu
- Opens wizard with all settings pre-filled
- User can modify any step before launching
- Creates completely new independent bot
- Does not affect original bot

---

## Bot Lifecycle After Launch

1. Bot starts scanning qualifying coins
2. Entry signal detected → opens position
3. Position enters smart queue
4. DCA fires when price drops X% from last buy
5. Sequential gate triggers next trade if configured
6. Trailing TP arms when price rises Y% above avg
   (skipped if Limit DCA mode ON)
7. Market or limit sell fires based on order type
8. Capital freed → queue rescans immediately
9. Bot continues forever until stopped manually
