# Bot Creation Wizard

> 7-step wizard for creating new bots.
> Accessed from Bots tab + Create Bot button.

---

## Overview

- 7 steps total
- Back button available at any step
- Warnings shown in amber
- Errors shown in red (cannot launch until fixed)
- All orders are market orders — locked — cannot change

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
| Smart DCA | Fully automated — recommended default |
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
| Quote Currency | USDT | Also USDC · BTC · ETH |
| Order Type | Market | Locked — cannot change ever |

---

## Step 4 — DCA Settings

### Smart DCA
- All automated — no manual input needed
- Category auto-detected from coin market cap
- Confidence level shown per coin

### Manual Methods (ASAP · Mean-Reversion · TradingView)
| Field | Notes |
|-------|-------|
| DCA Trigger % | % drop from last buy price to fire DCA |
| Spacing Multiplier | Each level widens by this factor |
| Size Multiplier | Each level size increases by this factor |
| Max Trades Per Bot | Default 0 · warning if left at 0 |

### One Pair Per Bot
- Enforced automatically
- Cannot open same coin twice on same bot
- Cross-bot allowed

---

## Step 5 — Profit Settings

### Smart DCA
- TP Mode: Auto (recommended) or Manual
- If Manual: warning shown if TP% - Trail% < 1%
- Trailing safety enforced automatically

### Manual Methods
| Field | Default | Notes |
|-------|---------|-------|
| Take Profit % | 5.0 | % above avg cost to arm trailing |
| Trailing % | 2.0 | % pullback from peak to sell |

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
| Recovery Buy | ON | For positions >30d and >10% down |
| Recovery Amount | $1.00 | Per recovery buy |
| Recovery Max/Month | 3 | Per position per month |

---

## Step 7 — Review and Launch

- Full summary of all settings shown
- Amber warnings (e.g. low balance · max trades = 0)
- Red errors (cannot launch until fixed)
- Coin confidence breakdown: New X · Learning Y · Calibrated Z
- Back button to any previous step
- Launch Bot button

### Pre-Launch Checks
- Exchange connected and API valid
- Sufficient balance for at least 1 base order
- Max trades per bot set (warning if 0)
- Reserve floor < resume threshold
- At least 1 coin qualifies for this bot

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
5. Trailing TP arms when price rises Y% above avg
6. Market sell fires on Z% pullback from peak
7. Capital freed → queue rescans immediately
8. Bot continues forever until stopped manually
