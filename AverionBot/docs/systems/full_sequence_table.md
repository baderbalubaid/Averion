# Full Lifecycle Sequence — Long / Short / Scalper

5 columns: # | Naming (standardized name to use when we write the
new code) | Long | Short | Scalper.

Naming rule: ONE shared name when the logic is genuinely identical
across systems that have it. A prefixed name (long_x / short_x /
scalper_x) when the logic genuinely differs between systems, even if
conceptually similar.

Long: fully verified from real code. Short: verified through the
gates/entry/open steps so far - DCA-queue/close/fee sections still
TO RESEARCH. Scalper: TO RESEARCH entirely.

Legend: ✅ = verified | ⚠️ = partially verified or a confirmed bug |
— = confirmed does not apply | TO RESEARCH = not yet checked

| # | Naming | Long | Short | Scalper |
|---|--------|------|-------|---------|
| **A. Daily background jobs (cron)** |
| 1 | coin_classification | ✅ | ✅ shared | TO RESEARCH |
| 2 | exchange_min_orders_refresh | ✅ | ✅ shared | TO RESEARCH |
| 3 | coin_parameter_calculation | ✅ | ✅ shared | TO RESEARCH |
| 4 | rars_scoring | ✅ | TO RESEARCH | TO RESEARCH |
| 5 | champion_promotion | ✅ | — (no champion concept) | TO RESEARCH |
| 6 | paper_timer_check | ✅ user-level, shared | ✅ shared | TO RESEARCH |
| 7 | btc_daily_fetch | ✅ | TO RESEARCH | TO RESEARCH |
| 8 | data_retention_cleanup | ✅ | TO RESEARCH | TO RESEARCH |
| 9 | daily_reports_notifications | ✅ | TO RESEARCH | TO RESEARCH |
| **B. Live price feed** |
| 10 | live_price_feed | ✅ | ✅ shared | TO RESEARCH |
| **C. Main cycle / bot loading** |
| 11 | bot_loader | ✅ rebuilt | ✅ rebuilt (shared function, direction param) | TO RESEARCH |
| 12 | champion_loader | ✅ rebuilt | — | TO RESEARCH |
| 13 | long_champion_injection / scalper_champion_injection | ✅ Long-specific logic | — | TO RESEARCH (confirmed different from Long) |
| **D. Platform-level gates** |
| 14 | bot_slot_limit | ✅ shared | ✅ confirmed - all checked inside the one shared is_new_trade_allowed() call Short already makes | TO RESEARCH |
| 15 | trade_limit | ✅ shared | ✅ confirmed (same as above) | TO RESEARCH |
| 16 | global_trading_toggles | ✅ shared | ✅ confirmed (same as above) | TO RESEARCH |
| 17 | entry_style_toggle | ✅ | ✅ confirmed, uses Short's own toggle keys (short_smart_enabled / short_customized_enabled) inside the same shared function | TO RESEARCH |
| 18 | exchange_toggle | ✅ shared | ✅ confirmed (same as above) | TO RESEARCH |
| 19 | debt_check | ✅ | ❌ MISSING - confirmed real gap, must be added | TO RESEARCH |
| 20 | long_floor_pause | ✅ Long-only by design | — (confirmed not applicable) | TO RESEARCH |
| 21 | long_st_check / short_st_check | ⚠️ exists, has its own detection gap | ❌ MISSING - needs new design (notify user to sell coin before delisting) | TO RESEARCH |
| 22 | trades_per_bot_limit | ✅ | — confirmed genuinely not needed: Short trades exactly one pre-assigned coin, so trades_per_coin already covers the same limit naturally | TO RESEARCH |
| 23 | trades_per_coin_limit | ✅ | ✅ confirmed | TO RESEARCH |
| **E. Entry decision** |
| 24 | long_entry_branching / short_entry_branching | ⚠️ not fully traced | ⚠️ confirmed 2 SEPARATE dimensions (entry_method=asap/not, PLUS parameter_mode=smart/customized) - genuinely different structure from Long, not just different names | TO RESEARCH |
| 25 | wallet_affordability_check | ✅ | ✅ confirmed (bot['wallet']['current_balance'] > 0 check before opening) | TO RESEARCH |
| 26 | exchange_min_order_check | ✅ shared | ✅ confirmed (get_min_order(), cached daily via the same cron job) | TO RESEARCH |
| 27 | long_place_buy_order / short_open_position_record | ✅ Long genuinely trades here | ⚠️ CONFIRMED GENUINELY DIFFERENT - Short's "open" is tracking-only, no trade, no wallet debit at all - the real first sell happens later via the same function used for every later sell | TO RESEARCH |
| 28 | long_btc_context_snapshot | ✅ | — (confirmed Short's open does NOT snapshot BTC context at all) | TO RESEARCH |
| 29 | position_insert | ✅ shared table, different columns | ✅ | TO RESEARCH |
| 30 | long_wallet_debit | ✅ | — (no debit at open - nothing spent yet) | TO RESEARCH |
| **F. DCA / queue logic** |
| 31 | load_open_positions | ✅ rebuilt | TO RESEARCH | — (confirmed no DCA at all) |
| 32 | long_needs_dca / short_check_sell_trigger | ✅ rebuilt | ✅ confirmed genuine mirror of Long's logic - same spacing-multiplier compounding math, just inverted (price must RISE, not drop) | — |
| 33 | long_dca_amount_calc / short_compute_sell_amount | ✅ rebuilt | ✅ confirmed - PLUS a real feature Long does NOT have: partial-fill amounts that don't meet the exchange minimum carry forward as 'standby_amount', added on top of the NEXT level's requirement instead of being lost | — |
| 34 | dca_priority_scoring | ✅ rebuilt | — (confirmed no scoring/queue system at all) | — |
| 35 | dca_priority_funding_loop | ⚠️ not yet rebuilt | — | — |
| **G. Take-profit / trailing / close** |
| 36 | check_tp | ✅ verified | TO RESEARCH | TO RESEARCH |
| 37 | tp_arm_or_immediate | ✅ verified | TO RESEARCH | TO RESEARCH |
| 38 | tp_trailing_sell | ✅ verified | TO RESEARCH | TO RESEARCH |
| 39 | long_execute_sell / short_handle_buyback_fill | ⚠ not fully traced (profit_coin logic) | ⚠️ CONFIRMED GENUINELY DIFFERENT MECHANISM - Short closes via a limit-order buyback FILL callback, not a direct market sell like Long | TO RESEARCH |
| **H. Close — fees & reserve wallet** |
| 40 | performance_fee_calc | ✅ shared | ✅ confirmed same function, same 20% default, same is_research/is_admin/is_zero_fee/fee_override checks | TO RESEARCH |
| 41 | reserve_wallet_deduct | ✅ shared | ✅ confirmed same db.deduct_performance_fee() call | TO RESEARCH |
| 42 | fee_audit_log | ⚠️ confirmed often missing in real data - real bug | ⚠️ likely the same bug, since it is the exact same shared function - not yet independently confirmed for Short specifically | TO RESEARCH |
| 43 | referral_commission | ✅ shared | ✅ likely shared (handled inside the same deduct_performance_fee() call, not visible separately in Short's own code) | TO RESEARCH |
| 44 | debt_blocks_new_entries_only | ✅ confirmed correct | ❌ (ties to #19 - the missing debt check) | TO RESEARCH |
| 45 | reserve_deposit_paydown | ✅ shared | TO RESEARCH (likely shared) | TO RESEARCH |
