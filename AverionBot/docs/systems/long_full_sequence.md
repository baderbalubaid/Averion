# Long-DCA Bot - Full Lifecycle Sequence (verified from real code)

Every step below was checked directly against the running code on
June 27 2026, not written from memory. Steps marked VERIFIED were
read in full. Steps marked PARTIAL were seen but not traced
completely. Nothing here describes intended/planned behavior unless
explicitly marked as such.

## 1. Coin Classification [VERIFIED]
1.1. classify_coins.py runs once per day (triggered via a Redis key
     check in research_engine.py's main cycle).
1.2. Pulls the live coin list from Redis price keys
     (price:MEXC*:*/USDT).
1.3. Fetches real market cap data from CoinGecko's public API.
1.4. Sorts each coin into one category by cap size:
     mega (>=$100B) / large (>=$10B) / mid (>=$1B) / small (>=$100M)
     / micro (anything smaller).
1.5. Writes one row per coin into coin_history (coin, category,
     recorded_cap, volume, source, timestamp).

## 2. Coin Parameter Calculation [NOT YET TRACED]
2.1. calculate_coin_params.py reads coin_history and produces
     per-coin dca_spacing/take_profit_pct/trailing_pct/tradeable/
     size_mult, written into coin_parameters.
2.2. NOT YET VERIFIED: the exact formula/logic that turns a coin's
     category+volatility into these specific numbers.

## 3. Live Price Feed [VERIFIED]
3.1. websocket_prices.py (MexcWebSocketPrices) connects to the
     exchange's live websocket feed.
3.2. On every single tick, the price is written into Redis
     (price:{exchange}:{coin}/USDT) AND immediately pushed to every
     registered callback (Long, Short, Scalper variants) - this is
     the zero-delay, push-based mechanism, already correct and not
     part of any per-bot decision logic.

## 4. Bot Loading [VERIFIED - rebuilt in bot_loader.py]
4.1. Every ~60s+cycle-time, load_bots('long', ...) queries all
     active Long bots (is_research=FALSE, is_template=FALSE,
     direction='long', status='open', method LIKE 'DCA%' OR 'E%').
4.2. FIXED in the rebuild: removed an incorrect trading_on=TRUE
     filter that was silently freezing DCA/TP for stopped bots in
     the original code.

## 5. Champion Loading (Smart-mode only) [VERIFIED - rebuilt in champion_service.py]
5.1. load_champions('DCA') fetches the current best-performing
     method+params for each of 3 market regimes (bear/bull/sideways)
     from champion_history.
5.2. get_current_regime() reads which regime is currently active
     from a Redis cache research_engine.py maintains.
5.3. For each loaded bot with entry_method='dca_smart', the matching
     regime's champion is attached to the bot dict for use during
     entry decisions (step 6).

## 6. Entry Decision [PARTIAL - not fully traced yet]
6.1. Each bot's entry_method is one of: 'dca_asap' (no decision
     logic, opens whenever eligible), 'dca_smart' (uses the
     champion's parameters from step 5), or 'dca_templates'
     (uses the bot's own saved/customized parameters).
6.2. NOT YET FULLY VERIFIED: the exact branching logic inside
     open_position() / the ASAP-specific fast path that decides
     which coin to enter and when, for each of these 3 methods.

## 7. Open Position [PARTIAL]
7.1. Checks system_gates.is_new_trade_allowed() (reserve debt,
     floor-pause, and other platform-level gates).
7.2. Loads the wallet, checks it can afford base_order.
7.3. Checks the exchange's real minimum order size for this coin.
7.4. Places the actual buy order via the executor (paper or live).
7.5. Snapshots BTC market context (price/regime/24h change/
     dominance/SMA50) at the moment of entry.
7.6. Inserts the new row into positions (direction='long').
7.7. Logs the debit into wallet_transactions.

## 8. DCA Queue (per cycle) [VERIFIED - rebuilt through the scoring step in long_engine.py]
8.1. load_open_positions() gets every open position for this bot.
8.2. For each position, needs_dca() checks if price has dropped
     pos_dca_pct% since the last buy (or since avg_cost if no DCA
     has happened yet).
8.3. If yes, the next DCA amount is base_order x size_mult^(dca_count+1),
     minimum $5.
8.4. score_position() ranks all candidates by loss% per dollar
     needed - highest-loss-per-dollar gets priority.
8.5. NOT YET REBUILT: the actual funding loop (reserve_funds() from
     the new wallet_service.py, then execute the buy, for every
     affordable candidate in priority order - confirmed June 23 2026
     this must process ALL affordable candidates, not stop after the
     first one, or lower-priority positions can be starved
     indefinitely).

## 9. Take-Profit / Trailing Check [VERIFIED the trigger logic, NOT YET the sell execution]
9.1. check_tp() fires on every price tick for every open position.
9.2. TP price = avg_cost x (1 + pos_tp_pct/100).
9.3. If price reaches TP price and trailing gap is very tight
     (tp_pct - trail_pct < 1.0), sell immediately - no trailing wait.
9.4. Otherwise, TP "arms" (tp_armed=TRUE, peak_price recorded), then
     tracks the highest price reached (peak_price) on every
     subsequent tick.
9.5. Sells once price drops trail_pct% from that peak - WITH a
     safety check: never actually sell at a real loss
     (price <= avg_cost x 1.005 blocks the sell even if trailing
     would otherwise fire).
9.6. NOT YET FULLY TRACED: the rest of execute_tp_sell()'s body
     (profit_coin partial-sell logic, fee triggering, wallet credit).

## 10. Fee Collection [VERIFIED from earlier investigation this session]
10.1. On a profitable close, deduct_performance_fee() calculates 20%
      of the realized profit.
10.2. Deducts this amount from the user's reserve_wallets.balance_usdt
      - this can go negative (visible debt), by deliberate locked
      rule, rather than being hidden.
10.3. Logs an audit row in fee_debt (position_id, amount, profit,
      paid_at=NULL until covered by a future deposit).
10.4. If the user was referred by someone, 2.5% of the fee amount is
      credited to the referrer as commission.
10.5. CONFIRMED REAL BUG (logged in OPEN_INVESTIGATIONS.md, not yet
      fixed): bot_audit.py found multiple real, profitable closes on
      live bots with NO matching fee_debt row at all - meaning this
      step may not be firing correctly on the actual TP-close path.

## 11. Reserve Wallet / Debt [VERIFIED from earlier investigation this session]
11.1. credit_reserve() is the deposit function (manual today, built
      so a future NOWPayments webhook integration can call the exact
      same function later with zero rework).
11.2. A deposit first pays down any existing negative balance (debt)
      before counting as new available balance.
11.3. Reserve alert levels (none/warning/critical/empty) only
      re-trigger when CROSSING into a worse level than before, not
      on every single fee deduction while already below a threshold.
11.4. CONFIRMED LOCKED RULE (this session): when balance < 0
      (debt), NEW positions/entries should be blocked for that
      user's bots - but DCA and TP on already-open positions must
      keep working normally. This rule was already correctly
      implemented for account_in_debt in the original code (verified
      June 27), unlike the separate trading_on=FALSE bug found and
      fixed the same week.
