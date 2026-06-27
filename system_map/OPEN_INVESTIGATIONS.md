# Open Investigations (auto-tracked, update as found/resolved)

Running list of confirmed-real findings not yet root-caused or fixed.
Add new findings here immediately when found - don't rely on chat
history surviving. Mark RESOLVED with date + commit hash when fixed,
don't delete the line (keeps a record of what was checked).

## OPEN

1. **Wallet committed_usdt mismatch** - bot 746 / wallet 6: committed_usdt
   ($77.95) vs actual sum of open positions' total_invested ($344.00),
   off by $266.05. Found via bot_audit.py. Likely a side-effect of
   today's DCA-starvation fix (positions now genuinely accumulate
   total_invested across many new DCA buys, but committed_usdt may not
   be incrementing to match on each buy).

2. **~50% of bot 746's open positions have no live price in Redis**
   (21 of 42 in one audit run). Found via bot_audit.py. Scale suggests
   a systemic price-feed gap for low-volume coins, not just a few
   delisted/ST coins.

3. **No reserve_wallets row for user_id=1.** Found via bot_audit.py.
   Means deduct_performance_fee() would fail to find a row to update
   - need to confirm whether this is specific to user 1 (possibly the
   original/admin account predating this table) or affects other users.

4. **None of bot 746's last 9 profitable closes have a matching
   fee_debt row.** Found via bot_audit.py. POTENTIALLY SERIOUS - if
   deduct_performance_fee() is never being called on TP-close (not
   just failing due to #3 above), the platform's 20% performance fee
   may not be collected on wins. Needs to confirm: does the TP-close
   code path actually call deduct_performance_fee() at all?

5. **XT marked ST on real MEXC, but our check_st_flag() doesn't detect
   it** (st:MEXC Paper:XT in Redis returns None/not flagged). User-
   reported June 25. Gap in ST-detection logic specifically, separate
   from the DCA-trigger bug found the same day.

6. **Scalper engine's trading_on=FALSE (manual stop) behavior unverified.**
   User confirmed (June 27) the "stopped bot should still DCA/TP existing
   positions" rule applies generally, not just the debt case - confirmed
   already correct for account_in_debt in both Long-DCA and Scalper, and
   for trading_on in Long-DCA (fixed June 25). NOT yet verified for
   trading_on specifically in the Scalper engine.

7. **~17 more live_dca_positions references remain in api.py/database.py**
   (found June 25, not yet fixed) - includes manual close, TP%/trail%
   updates, panic close, bot deletion, and a coin-quantity lookup in
   database.py. Found via grep, listed in chat June 25 but not yet
   addressed file-by-file.

## RESOLVED

- DCA not triggering on bot 745/746 (stale table + starvation bug +
  NULL wallet_id, June 23-25) - fixed, commits 0d777ac/296c0cd/4753ba8/
  [trading_on fix commit].
- research bot_params silently ignored on every entry signal check
  (bot[29] vs bot[30] index bug, June 24) - fixed, commit 296c0cd.
- research positions created with wallet_id=NULL going forward
  (June 24) - fixed, commit 296c0cd.
- /live-positions showing -40% instead of real -12% (same stale
  live_dca_positions table, June 25) - fixed, commit (api.py fix).
