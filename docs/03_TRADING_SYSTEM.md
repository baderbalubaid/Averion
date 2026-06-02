# Trading System

> How Averion executes trades.
> All rules here are LOCKED unless explicitly discussed with Bader.

---

## Core Philosophy
- Survivability first
- Controlled recovery second
- Profit third
- Bot NEVER stops — put money and forget it

---

## Trading Modes

### Long DCA
- Price drops → buy more → lower average cost → sell at TP
- User does not need to hold coin first
- Bot opens position immediately on signal

### Short DCA
- User MUST already hold the coin on exchange
- Price rises → sell portions → raise average sell price
- Price drops back → buy all back cheaper
- Only sell if quantity >= exchange minimum order size
- No borrowing · no margin · no leverage · pure spot only

---

## Order Types
- Market orders are the default — guaranteed execution always
- Limit orders optional per bot: entry + DCA (user selects in wizard)
- Short DCA buyback: limit order only (reserves USDT on exchange)
- Guaranteed execution > perfect price — always

---

## DCA Logic

### Spacing Rule (LOCKED)
- Trigger = percentage drop from LAST BUY PRICE
- Never from average cost
- Never a fixed price threshold
- Always percentage-based check every 60 seconds

### Widening Geometry
- Each level spacing = previous spacing × SPACING_MULTIPLIER (default 1.4)
- Level 1: 7.0% drop
- Level 2: 7% × 1.4 = 9.8% drop
- Level 3: 9.8% × 1.4 = 13.7% drop
- Level 4: 13.7% × 1.4 = 19.2% drop
- Continues indefinitely — no max levels

### Size Escalation
- Each level size = previous size × SIZE_MULTIPLIER (default 1.5)
- Coin base multiplier from category (Mega=1.10x · Large=1.20x · Mid=1.35x · Small=1.50x · Micro=1.65x)
- Per level escalation: L1=1.0x · L2=1.2x · L3=1.4x · L4=1.6x · L5+=2.0x hard cap

---

## Take Profit System

### Trailing TP
- Arms when price reaches TP% above average cost
- Follows price up (locks X% below new peak always)
- Fires market sell when price pulls back TRAIL% from peak
- 100% position exit in one market order — no partial exits

### Trailing Safety Rule (Smart DCA Only)
- If TP% - Trail% < 1% → skip trailing → direct market sell at TP
- Prevents selling at breakeven or loss after fees

### Example
- Position avg cost = $1.00 · TP = 5% · Trail = 2%
- Price hits $1.05 → trailing ARMS
- Price rises to $1.10 → trailing locks at $1.078
- Price drops to $1.078 → MARKET SELL fires ✅

---

## Slippage Handling (LOCKED)

Market order mode: Before every DCA (limit orders handled separately):

1. Check order book depth at target price
2. If available >= $1 minimum → buy at target price ✅
3. If available < $1 minimum → buy $1 market order
4. Maximum slippage exposure = $1 only
5. Never chase more than $1 above target
6. Always executes something — never stuck waiting
7. Recalculate avg cost from actual fill
8. Next DCA from new last buy price

---

## ST Flag — Exchange Suspended Trading (LOCKED)

- Exchange marks coin ST → auto sell immediately (market order)
- Do not open new positions on ST coins
- When ST cleared → resume normally
- Telegram alert when ST detected and cleared
- Checked via CCXT on all 7 exchanges every hour
- This is the ONLY forced close — user controls everything else
- Dead coins without ST flag → nothing we can do · holds position

---

## Profit Coin

- User chooses at bot creation: USDT or base coin
- Works for both Long and Short trades
- Long + USDT: sell all coin → receive USDT
- Long + base coin: sell enough to recover invested USDT · keep profit as coin
- Short + USDT: buy back less coin than sold · difference stays as USDT
- Short + base coin: buy back same USDT value · at lower price = more coin

---

## Current config.py Parameters

| Variable | Value | Description |
|----------|-------|-------------|
| PAPER_MODE | .env file | Never in config.py |
| BASE_ORDER_USDT | 1.0 | First buy amount |
| DCA_PERCENT | 7.0 | % drop from last buy |
| SPACING_MULTIPLIER | 1.4 | Spacing widens each level |
| SIZE_MULTIPLIER | 1.5 | Size increases each level |
| TAKE_PROFIT_PERCENT | 5.0 | % above avg cost to arm TP |
| TRAILING_PERCENT | 2.0 | % pullback from peak to sell |
| AUTO_COINS | True | Auto-fetch all USDT pairs |
| MAX_COINS | 100 | Replit only — remove on Hetzner |
| CHECK_INTERVAL | 60 | Seconds between price checks |

---

## Supported Exchanges (via CCXT)
1. MEXC (live now on Replit)
2. Binance
3. KuCoin
4. OKX
5. Gate.io
6. Bybit
7. Bitget

## TP Recalculation Timing (LOCKED)

- TP target recalculates after EVERY buy automatically
- Formula: TP_target = avg_cost x (1 + TP%)
- Recalculates after: entry buy, every auto DCA, every Add Funds
- TP target is NEVER a fixed price
- Always based on current weighted average cost
- Add Funds shows preview before executing: quantity, new avg cost, new TP target
