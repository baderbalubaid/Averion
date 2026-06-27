# Full Lifecycle Sequence — Long / Short / Scalper

Long column fully verified from real code (June 27 2026). Short and
Scalper columns marked TO RESEARCH - will be filled in with the same
verification process before this table is considered complete.

Legend: "—" means this step genuinely does not apply to that system
(confirmed, not just unchecked). "TO RESEARCH" means not yet checked.

| # | Step | Long | Short | Scalper |
|---|------|------|-------|---------|
| **A. Daily background jobs (cron)** |
| 1 | Coin Classification (market-cap category) | ✅ shared | TO RESEARCH | TO RESEARCH |
| 2 | Exchange Minimum Orders refresh | ✅ shared | TO RESEARCH | TO RESEARCH |
| 3 | Coin Parameter Calculation (spacing/TP/trailing) | ✅ shared | TO RESEARCH | TO RESEARCH |
| 4 | RARS Scoring | ✅ shared | TO RESEARCH | TO RESEARCH |
| 5 | Champion Promotion | ✅ | — (confirmed no champion concept) | TO RESEARCH |
| 6 | Paper Timer check (90-day no-live-trade auto-close) | ✅ user-level, shared | TO RESEARCH | TO RESEARCH |
| 7 | BTC Daily Fetch | ✅ shared | TO RESEARCH | TO RESEARCH |
| 8 | Data Retention cleanup | ✅ shared | TO RESEARCH | TO RESEARCH |
| 9 | Report generation + notifications | ✅ shared | TO RESEARCH | TO RESEARCH |
| **B. Live price feed** |
| 10 | Websocket tick → Redis + instant push (zero-delay) | ✅ shared | TO RESEARCH | TO RESEARCH |
| **C. Main cycle / bot loading** |
| 11 | Load active bots | ✅ rebuilt in bot_loader.py | TO RESEARCH | TO RESEARCH |
| 12 | Load champions per regime + current regime | ✅ rebuilt in champion_service.py | — | TO RESEARCH |
| 13 | Attach champion to Smart-mode bots | ✅ Long-specific logic | — | TO RESEARCH |
| **D. Platform-level gates (before any new entry)** |
| 14 | Bot-slot limit (5 free) | ✅ shared (system_gates.py) | TO RESEARCH | TO RESEARCH |
| 15 | Trade limit (100 total / 30 paper sub-cap) | ✅ shared (system_gates.py) | TO RESEARCH | TO RESEARCH |
| 16 | Emergency halt / global trading toggles | ✅ shared (system_gates.py) | TO RESEARCH | TO RESEARCH |
| 17 | Entry-style toggle (per method) | ✅ | TO RESEARCH | TO RESEARCH |
| 18 | Exchange toggle (MEXC/KuCoin) | ✅ shared (system_gates.py) | TO RESEARCH | TO RESEARCH |
| 19 | Reserve-wallet debt check (blocks NEW entries only) | ✅ | TO RESEARCH | TO RESEARCH |
| 20 | Floor-pause check (blocks NEW entries only) | ✅ | TO RESEARCH | TO RESEARCH |
| 21 | ST-flag check (coin suspended/delisted) | ✅ (confirmed real detection gap exists) | TO RESEARCH | TO RESEARCH |
| 22 | trades_per_bot limit (total open positions cap) | ✅ wizard-configured | TO RESEARCH | TO RESEARCH |
| 23 | trades_per_coin limit (per-coin cap) | ✅ wizard-configured | TO RESEARCH | TO RESEARCH |
| **E. Entry decision** |
| 24 | Branch by entry_method (ASAP/Smart/Customized) | ⚠️ not fully traced yet | TO RESEARCH | TO RESEARCH |
| 25 | Wallet affordability check | ✅ | TO RESEARCH | TO RESEARCH |
| 26 | Exchange minimum order check | ✅ shared | TO RESEARCH | TO RESEARCH |
| 27 | Place buy order | ✅ | TO RESEARCH | TO RESEARCH |
| 28 | Snapshot BTC market context at entry | ✅ | TO RESEARCH | TO RESEARCH |
| 29 | Insert position row | ✅ rebuild target: position_loader.py / position_service.py | TO RESEARCH | TO RESEARCH |
| 30 | Log wallet debit (wallet_transactions) | ✅ | TO RESEARCH | TO RESEARCH |
| **F. DCA / queue logic** |
| 31 | Load open positions | ✅ rebuilt in position_loader.py | TO RESEARCH | — (confirmed no DCA at all) |
| 32 | Check DCA eligibility (price move vs threshold) | ✅ needs_dca() rebuilt | TO RESEARCH | — |
| 33 | Calculate next DCA amount | ✅ rebuilt | TO RESEARCH | — |
| 34 | Rank candidates by priority (loss-per-dollar) | ✅ score_position() rebuilt | — (confirmed no scoring/queue system) | — |
| 35 | Fund every affordable candidate (not just first) | ⚠️ not yet rebuilt (logic confirmed, wiring pending) | — | — |
| **G. Take-profit / trailing (real-time)** |
| 36 | Check TP target reached | ✅ check_tp() verified | TO RESEARCH | TO RESEARCH |
| 37 | Immediate sell OR arm + track peak | ✅ verified | TO RESEARCH | TO RESEARCH |
| 38 | Sell on trailing drop (never below real cost) | ✅ verified | TO RESEARCH | TO RESEARCH |
| 39 | Execute sell (incl. partial "keep coin" option) | ⚠️ not fully traced (profit_coin logic) | TO RESEARCH | TO RESEARCH |
| **H. Close — fees & reserve wallet** |
| 40 | Calculate 20% fee on profit | ✅ shared (deduct_performance_fee) | TO RESEARCH | TO RESEARCH |
| 41 | Deduct from reserve wallet (can go negative) | ✅ shared | TO RESEARCH | TO RESEARCH |
| 42 | Log fee audit row | ⚠️ confirmed often missing in real data - real bug | TO RESEARCH | TO RESEARCH |
| 43 | Pay referral commission (2.5% of fee) | ✅ shared | TO RESEARCH | TO RESEARCH |
| 44 | Block new entries only while in debt (DCA/TP continue) | ✅ confirmed correct in original code | TO RESEARCH | TO RESEARCH |
| 45 | Future deposit pays down debt first | ✅ shared (credit_reserve) | TO RESEARCH | TO RESEARCH |

## Legend for status marks
- ✅ = verified directly from real code this session
- ⚠️ = verified the trigger/concept exists, but not the full implementation, OR a confirmed real bug
- — = confirmed this step genuinely does not exist/apply for that system
- TO RESEARCH = not yet checked - next research pass needed
