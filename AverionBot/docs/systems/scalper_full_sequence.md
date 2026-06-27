# Scalper - Full Lifecycle Sequence (verified from real code)

Built independently from Scalper's own code (V1: live_scalper_engine.py,
V2: scalper_v2_engine.py), in Scalper's own natural order. Rebuild
unifies V1+V2's exit logic into one system (see architecture_overview.md
decision log) - this document traces what the OLD code actually does,
not yet the unified rebuild design.

## 1. Engine startup [VERIFIED]
1.1. Class-based (LiveScalperEngine), not function+thread like
     Long/Short. __init__ connects DB pool, Redis, loads bots,
     starts a cleanup thread and a bot-refresh thread.
1.2. NO heartbeat existed at all in the original (gap found and
     logged earlier this session - already fixed in the rebuild's
     heartbeat_service.py).

## 2. Bot loading (_load_bots, runs once at startup + every 60s via
   refresh thread) [VERIFIED]
2.1. Queries bots WHERE method='S58', trading_on=TRUE (CONFIRMED:
     same trading_on bug class found in Long/Short - logged as
     finding #16, 3rd confirmed instance).
2.2. Computes floor_paused per bot - CONFIRMED via discussion this
     does NOT belong in the rebuild (wallet allocation alone already
     prevents new entries once funds are spent; floor-pause's real
     purpose - giving time to DCA back to recovery - doesn't apply
     to a quick-in-quick-out system).
2.3. Computes account_in_debt per bot (db.is_reserve_in_debt) -
     CONFIRMED Scalper genuinely HAS a debt check, unlike Short.
2.4. Loads the current Scalper champion for the active regime
     (narrower single-regime query in the original - already fixed
     in champion_service.py to use Long's fuller all-3-regimes
     pattern instead).
2.5. For Smart-mode bots: injects champion params by directly
     overwriting trigger_pct/window_sec/hold_sec/stop_loss_pct, AND
     also attaches the raw champion object (bot['_champion']) - does
     BOTH, not just one or the other.

## 3. Entry decision (_check_entry, fires on every price tick) [VERIFIED]
3.1. Gate 1: floor_paused check (being removed in rebuild, see above).
3.2. Gate 2: account_in_debt check.
3.3. Gate 3: system_gates.is_new_trade_allowed('scalper', ...) - same
     shared gate Long/Short use.
3.4. CONFIRMED REAL, ALREADY-FIXED RACE CONDITION (June 23 2026):
     the "is this bot+coin already active" check and the actual slot
     reservation used to NOT be atomic - since MEXC and KuCoin feed
     correlated price moves on separate threads, both could pass the
     check before either reserved the slot, opening a duplicate
     position. Fixed by reserving the slot (self.active[key] =
     'RESERVED') atomically with the check, under one lock, released
     cleanly if the signal doesn't actually fire.
3.5. check_entry_signal() (from scalper_signals.py) - the actual
     jump/velocity signal detection - NOT YET traced in detail.
3.6. If signal fires: _open_position(). Otherwise: release the
     reservation.

## 4. Open position (_open_position) [VERIFIED]
4.1. Checks wallet balance >= base_order, deducts immediately
     (no separate reserve/release step like the new wallet_service.py
     - this was the ORIGINAL FOR-UPDATE-locked pattern that motivated
     building reserve_funds() as a shared service for all 3 systems).
4.2. Inserts into live_positions (CONFIRMED separate table from
     `positions` used by Long/Short, and also separate from
     scalper_positions used by some other variant entirely).
4.3. Schedules a threading.Timer for max_hold_sec that calls
     _exit_position(key, 'timer') when it fires - wrapped in a
     try/except specifically so an uncaught error inside the timer
     callback can't leave the position silently stuck open forever.

## 5. Position monitoring (_update_active, fires on every price tick) [VERIFIED for V1]
5.1. Tracks max_profit/max_loss seen on every tick.
5.2. Checks check_stop_loss() - if triggered, calls
     _exit_position(key, 'stop_loss').
5.3. V1 has NO trailing-stop logic at all here - confirmed.
5.4. V2 (scalper_v2_engine.py) DOES track peak_price and exits on a
     % drop from peak - confirmed real, separate mechanism not
     present in V1. REBUILD DECISION: unify both into one system (see
     architecture_overview.md).

## 6. Exit / close (_exit_position) [VERIFIED]
6.1. Calculates exit price from the latest price-history tick (not a
     fresh live lookup at the exact close moment).
6.2. Calculates pnl_pct/pnl_usdt via calc_pnl().
6.3. Updates live_positions: exit_price, max_profit/loss_seen,
     pnl, exit_reason, status='closed'.
6.4. Returns funds to wallet: base_order + pnl_usdt credited back
     (genuinely different capital model from Long/Short, which hold
     an actual asset position rather than a fixed "bet" amount).
6.5. Fee deduction on profit - CONFIRMED same shared
     deduct_performance_fee() function, same 20% default/exceptions
     as Long and Short. Comment confirms this was ADDED June 20 2026
     - Scalper had ZERO fee collection before that, already fixed,
     not a remaining gap.
6.6. Sets a 5-minute cooldown for this bot+coin pair before it can
     re-enter - a concept with NO equivalent in Long or Short at all.

## STILL NOT TRACED
- check_entry_signal() / check_stop_loss() / calc_pnl() internals
  (scalper_signals.py).
- The cleanup thread (_cleanup_stuck_positions) and what "stuck"
  means here.
- Whether Scalper has any trades_per_bot/trades_per_coin-style
  concept at all, or relies purely on the per-bot+coin active-slot
  lock.
- V2's own entry logic in full (E58v2 velocity/acceleration model,
  pump-chase rejection guard - referenced extensively in earlier
  session history but not re-verified from code this session).
