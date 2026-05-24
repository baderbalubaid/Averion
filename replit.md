# DCA Bot

A Dollar Cost Averaging (DCA) trading bot that connects to the MEXC exchange via the ccxt library.

## Overview

The bot fetches live BTC/USDT prices from MEXC and simulates DCA buy orders (paper trading). No real orders are placed.

## Current Phase

**Phase 1** - Paper trading simulation:
- Connects to MEXC exchange (public API, no keys required)
- Fetches live BTC/USDT price
- Simulates a $1 USDT buy and reports quantity and average cost

## Running

```
python main.py
```

## Dependencies

- `ccxt` - unified crypto exchange library

## User Preferences

- Paper trading mode by default (no real orders)
