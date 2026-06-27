# Deep System Map (verification in progress)

Every fact below is confirmed directly from running code on this
exact session's date. Nothing here is from memory or assumption -
if a line says "confirmed", it was checked. If a line says
"UNVERIFIED", it's a placeholder still to be checked.

## How the whole platform actually starts (confirmed June 27 2026)

    PM2 "averion-api"      -> api.py            (FastAPI, user-facing endpoints)
    PM2 "averion-research" -> research_engine.py -> run_bot()
                                  |
                                  +-- starts MexcWebSocketPrices() (websocket_prices.py)
                                  |       |
                                  |       +-- starts live_long_dca_engine.start_engine() as background thread
                                  |       +-- starts short_dca_engine.start_engine() as background thread
                                  |       +-- feeds live price ticks to:
                                  |             - scalper_engine.on_price_update (research/paper E58)
                                  |             - scalper_v2_engine.on_price_update (research/paper E58v2)
                                  |             - live_scalper_engine.on_price_update (LIVE S58 scalper)
                                  |
                                  +-- loops run_cycle(r) every ~60s+cycle-time
                                        (research/admin bot entry signals, Smart Queue DCA,
                                         ST flag checks - method LIKE 'DCA%' OR 'E%' only)

KEY FINDING: there is no separate PM2 process per engine. Long-DCA,
Short-DCA run as background threads INSIDE the single
averion-research process, started indirectly via websocket_prices.py.
Scalper (S58) runs via its own class (LiveScalperEngine) whose
on_price_update is wired into the same websocket_prices.py price feed.

bot_loop.py is NOT running anywhere (confirmed: not in pm2 list,
nothing imports it) - dead/legacy code, safe to delete with zero risk.

## CONFIRMED BUG (found via this exact mapping process, not yet fixed)

bot 747 (method='S58', a real live-account Scalper bot) is being
double-processed by TWO conflicting engines simultaneously:
1. live_scalper_engine.py's LiveScalperEngine._load_bots() - correctly
   matches it (WHERE b.method='S58' ...) - this is the intended engine.
2. research_engine.py's try_open_position() - only skips method
   starting with 'E58' (the line: if method and method.startswith('E58'): return)
   - 'S58' does NOT match this check, so it falls through and ALSO
   opens generic DCA-style positions on the same bot/wallet.
Root cause: an incomplete exclusion check, not a file-organization
problem - both engines already lived in separate files before this
was found.

