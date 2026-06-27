# Short-DCA Bot - Full Lifecycle Sequence (verified from real code)

Built independently from Short's own code, in Short's own natural
order - NOT mapped row-by-row against Long's sequence. Reconciling
the two into one shared table is a separate, later step.

## 1. Daily background jobs [shared with Long, confirmed]
1.1. Coin Classification, Exchange Min Orders, Coin Parameters - all
     confirmed genuinely shared (coin-level data, not direction-
     specific) via short_dca_engine.py's own imports/calls.
1.2. RARS Scoring, BTC Daily Fetch, Data Retention, Reports/
     notifications - NOT YET independently verified for Short
     specifically (these are generic, platform-wide cron scripts not
     touching short_dca_engine.py at all, so likely apply
     identically - still need to confirm none of them branch by
     direction internally).

## 2. Engine Startup [VERIFIED]
2.1. start_engine() / is_engine_alive() - structurally identical
     pattern to Long (same non-daemon-thread reasoning).
2.2. CRITICAL STRUCTURAL DIFFERENCE from Long: the periodic
     run_cycle() loop is NOT where the real decisions happen anymore.
     Per an explicit code comment (dated June 20 2026): new-slot
     opening and sell-trigger checks moved to on_price_update() for
     true zero-delay reactive behavior. run_cycle() is now ONLY a
     safety-net backup (in case a tick was somehow missed) plus
     genuinely periodic bookkeeping (buyback-fill safety check,
     stuck buyback retries).

## 3. on_price_update() - the REAL primary path [VERIFIED through entry+sell-check, PARTIAL on buyback-fill section]
3.1. Fires on every single websocket price tick. Fast no-op for
     coins with no matched Short bot.
3.2. Reads the bot+positions for this exact coin from an in-memory
     cache (_short_bots_by_coin / _short_positions_by_coin) -
     refreshed separately, NOT a fresh DB read on every tick.

3.3. New-slot opening (only if entry_method == 'asap'):
     - Checks: bot trading_on, under trades_per_coin cap, wallet
       balance > 0.
     - Calls open_short_position_record() - creates a TRACKING-ONLY
       position row (no trade, no debit - the user already holds
       the coin; this just records a reference price).
     - Immediately computes and executes the FIRST sell via
       compute_sell_amount() + execute_short_sell() - the position's
       very first real trade happens right here, through the exact
       same sell path used for every later DCA-style sell.

3.4. Sell-trigger check (every existing position for this coin):
     - check_sell_trigger() - mirrors Long's needs_dca() inverted:
       price must RISE (not drop) by a compounding spacing % since
       the last sell (or since avg_sell_price before the first sell).
     - If triggered: compute_sell_amount() determines how much to
       sell - genuinely more complex than Long's DCA amount calc,
       because it must respect the exchange's real minimum order size
       and can carry forward a partial amount as 'standby_amount' for
       the next level rather than losing it.
     - execute_short_sell() places the actual limit order.

3.5. Buyback fill check (tick-speed, for both paper and live) -
     NOT YET FULLY TRACED - this is the step that detects a
     previously-placed buyback limit order has filled, which is what
     actually CLOSES the position (see handle_buyback_fill(), already
     verified separately for its fee logic, but the detection/polling
     mechanism that calls it has not been read in full yet).

## 4. execute_short_sell() [VERIFIED]
4.1. Calls system_gates.is_new_trade_allowed('short', ...) - same
     shared gate Long uses, with Short's own entry_method/toggle keys.
4.2. Places the actual sell order via the executor.
4.3. Updates the position: increments dca_count, records
     last_sell_price, recalculates avg_sell_price across all sells so
     far, increments total_sold_usdt.
4.4. Immediately attempts to place a BUYBACK limit order for the
     same quantity, at a price calculated to lock in the target
     profit - this is fundamentally different from Long, where there
     is no separate "buyback" concept at all; Long's close IS the
     sell. For Short, the sell is the entry into a queue, and the
     buyback fill (step 3.5/4.5) is the actual close.
4.5. If the buyback order placement itself fails or gets stuck, a
     separate retry mechanism exists (referenced in run_cycle()'s
     safety-net role) - NOT YET fully traced.

## 5. handle_buyback_fill() - the actual CLOSE [VERIFIED]
5.1. Credits the bought-back coin to the wallet (paper only - live
     syncs externally from the real exchange).
5.2. Calculates realized P&L: total_sold_usdt minus the cost to buy
     it back.
5.3. Marks the position closed.
5.4. On profit: same shared deduct_performance_fee() Long uses (same
     20%, same admin/research/zero-fee/fee_override checks).

## 6. Confirmed REAL gaps for Short (not yet fixed, logged separately
   in OPEN_INVESTIGATIONS.md #14/#15)
6.1. No debt check before opening a new position slot (Long has this).
6.2. No ST-flag/delisting check at all (Long has this, with its own
     separate detection gap).
6.3. No floor-pause concept - CONFIRMED genuinely not applicable to
     Short's design, not a gap.
6.4. No trades_per_bot-style cap - CONFIRMED genuinely redundant given
     Short's single-pre-assigned-coin design, not a gap.

## STILL NOT TRACED AT ALL
- The buyback-fill DETECTION mechanism itself (how/when the system
  notices a placed buyback order has filled - tick-based per the
  comments, but the actual code reading this has not been viewed).
- Stuck buyback retry logic in run_cycle().
- Whether Short bots ever get assigned via Smart mode in a way that
  matches Long's champion system, or genuinely never (confirmed no
  champion_history usage at all, but parameter_mode='smart' still
  exists - what does Smart mode actually DO for Short if not
  champions? Reuses coin_parameters per get_short_params(), already
  partially seen, not fully traced).
