# Full Lifecycle Sequence — Long / Short / Scalper

5 columns: # | Naming | Long | Short | Scalper

Reconciled June 27 2026: Short was traced independently first (its
own real code, own natural order), then merged into this single
table - new rows were inserted where Short has genuine steps Long
does not have at all (Short's buyback placement/detection/retry),
rather than forcing Short into Long's exact row count.

Legend: ✅ verified | ⚠️ partial/confirmed bug | — confirmed N/A |
TO RESEARCH = not yet checked

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
| **C. Engine startup / bot loading** |
| 11 | bot_loader | ✅ rebuilt | ✅ rebuilt (shared fn, direction param) | TO RESEARCH |
| 12 | champion_loader | ✅ rebuilt | — | TO RESEARCH |
| 13 | long_champion_injection / scalper_champion_injection | ✅ Long-specific | — | TO RESEARCH |
| 14 | long_periodic_loop / short_safety_net_loop | ✅ this IS the primary mechanism for Long | ⚠️ CONFIRMED GENUINELY DIFFERENT ROLE - this is only a backup safety-net for Short, real decisions happen in step 21 (price-tick callback) instead | TO RESEARCH |
| **D. Platform-level gates** |
| 15 | bot_slot_limit | ✅ shared | ✅ confirmed | TO RESEARCH |
| 16 | trade_limit | ✅ shared | ✅ confirmed | TO RESEARCH |
| 17 | global_trading_toggles | ✅ shared | ✅ confirmed | TO RESEARCH |
| 18 | entry_style_toggle | ✅ | ✅ confirmed (own toggle keys) | TO RESEARCH |
| 19 | exchange_toggle | ✅ shared | ✅ confirmed | TO RESEARCH |
| 20 | debt_check | ✅ | ❌ MISSING - real gap | TO RESEARCH |
| 21 | long_floor_pause | ✅ Long-only by design | — confirmed N/A | TO RESEARCH |
| 22 | long_st_check / short_st_check | ⚠️ has own detection gap | ❌ MISSING - needs new design (notify user to sell coin before delisting) | TO RESEARCH |
| 23 | trades_per_bot_limit | ✅ | — confirmed N/A (single-coin design makes this redundant) | TO RESEARCH |
| 24 | trades_per_coin_limit | ✅ | ✅ confirmed | TO RESEARCH |
| **E. Entry decision** |
| 25 | long_entry_branching / short_entry_branching | ⚠️ not fully traced | ⚠️ confirmed 2 separate dimensions (entry_method + parameter_mode), genuinely different structure | TO RESEARCH |
| 26 | wallet_affordability_check | ✅ | ✅ confirmed | TO RESEARCH |
| 27 | exchange_min_order_check | ✅ shared | ✅ confirmed | TO RESEARCH |
| 28 | long_place_buy_order / short_open_position_record | ✅ Long genuinely trades | ⚠️ CONFIRMED DIFFERENT - tracking-only record, no trade, no debit | TO RESEARCH |
| 29 | long_btc_context_snapshot | ✅ | — confirmed not done at Short's open | TO RESEARCH |
| 30 | position_insert | ✅ shared table, different columns | ✅ | TO RESEARCH |
| 31 | long_wallet_debit | ✅ | — (nothing spent yet at this step) | TO RESEARCH |
| 32 | short_immediate_first_sell | — (no equivalent concept - Long's open IS the first buy already) | ✅ CONFIRMED Short-only step: right after the tracking-only open, the real first sell happens immediately via the same sell path as every later one | TO RESEARCH |
| **F. DCA / sell-trigger queue** |
| 33 | load_open_positions | ✅ rebuilt | ✅ confirmed (load_open_short_positions) | — confirmed no DCA |
| 34 | long_needs_dca / short_check_sell_trigger | ✅ rebuilt | ✅ confirmed genuine mirror, inverted direction | — |
| 35 | long_dca_amount_calc / short_compute_sell_amount | ✅ rebuilt | ✅ confirmed + standby_amount carry-forward (Long has no equivalent) | — |
| 36 | dca_priority_scoring | ✅ rebuilt | — confirmed no scoring/queue system at all | — |
| 37 | dca_priority_funding_loop | ⚠️ not yet rebuilt | — | — |
| 38 | long_execute_dca_buy / short_execute_short_sell | ✅ | ✅ confirmed - ALSO immediately places a buyback order as part of this same step (see #39) | TO RESEARCH |
| **G. Short-only: buyback placement and detection (NO Long equivalent at all)** |
| 39 | short_place_buyback_order | — | ✅ confirmed, happens immediately inside execute_short_sell() | — |
| 40 | short_buyback_fill_detection | — | ✅ confirmed - on EVERY price tick (for any position with a pending order_id), directly asks the exchange via check_limit_fill() if it has filled yet. Pure polling, not push-based - a deliberate, accepted tradeoff (real exchange rate-limit risk knowingly accepted in exchange for true zero-delay detection, per explicit June 20 2026 instruction) | — |
| 41 | short_stuck_buyback_retry | — | ✅ confirmed - runs once per 60s safety-net cycle (NOT tick-speed, unlike #40), specifically for positions where the SELL succeeded but the buyback LIMIT ORDER PLACEMENT itself failed (e.g. insufficient USDT because something else used it first) - keeps retrying every cycle per the locked rule that Short buyback funding wins the race for shared-wallet funds until it succeeds | — |
| **H. Take-profit / trailing / close** |
| 42 | check_tp | ✅ verified | — confirmed Short has no arm/peak/trailing concept at all - just a single threshold trigger (#34) | TO RESEARCH |
| 43 | tp_arm_or_immediate | ✅ verified | — | TO RESEARCH |
| 44 | tp_trailing_sell | ✅ verified | — | TO RESEARCH |
| 45 | long_execute_sell / short_handle_buyback_fill | ⚠️ not fully traced (profit_coin logic) | ✅ confirmed - THIS is Short's actual close, triggered by buyback fill (#40), not a direct sell | TO RESEARCH |
| **I. Close — fees & reserve wallet** |
| 46 | performance_fee_calc | ✅ shared | ✅ confirmed same function/rate/exceptions | TO RESEARCH |
| 47 | reserve_wallet_deduct | ✅ shared | ✅ confirmed | TO RESEARCH |
| 48 | fee_audit_log | ⚠️ confirmed often missing - real bug | ⚠️ likely same bug, not independently confirmed | TO RESEARCH |
| 49 | referral_commission | ✅ shared | ✅ likely shared (inside the same fn call) | TO RESEARCH |
| 50 | debt_blocks_new_entries_only | ✅ confirmed correct | ❌ ties to #20, the missing debt check | TO RESEARCH |
| 51 | reserve_deposit_paydown | ✅ shared | TO RESEARCH | TO RESEARCH |
