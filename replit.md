# DCA Bot

A Dollar Cost Averaging (DCA) trading bot that connects to the MEXC exchange via the ccxt library.

## Overview

The bot fetches live prices, manages positions in a local SQLite database, applies DCA logic when price drops, and takes profit with a trailing stop when the target is hit.

## Files

- `main.py` — main bot loop (price fetching, position management)
- `config.py` — all tunable settings
- `dca_logic.py` — pure functions for DCA/TP calculations
- `database.py` — SQLite setup and connection helper
- `dcabot.db` — auto-created SQLite database

## Configuration (`config.py`)

| Setting | Default | Description |
|---|---|---|
| `COIN` | `BTC/USDT` | Trading pair |
| `PAPER_MODE` | `True` | Paper trade (no real orders) |
| `BASE_ORDER_USDT` | `1.0` | USDT per buy order |
| `DCA_PERCENT` | `10.0` | % drop from avg to trigger DCA |
| `TAKE_PROFIT_PERCENT` | `5.0` | % gain from avg to arm take profit |
| `TRAILING_PERCENT` | `2.0` | % trailing stop below peak |
| `CHECK_INTERVAL` | `60` | Seconds between price checks |
| `MAX_DCA_ORDERS` | `5` | Max DCA buys per position |

## Bot Logic

1. On start: opens a new position at the current price
2. Every `CHECK_INTERVAL` seconds: fetches price
3. If price drops `DCA_PERCENT`% below avg cost → buys another order (up to `MAX_DCA_ORDERS`)
4. If price rises `TAKE_PROFIT_PERCENT`% above avg cost → arms trailing stop
5. If price pulls back `TRAILING_PERCENT`% from the trailing high → closes position for profit

## Running

```
python3 main.py
```

## User Preferences

- Paper trading mode by default (`PAPER_MODE = True`)
