"""
bot_audit.py v3 - Independent verification tool for a bot's FULL
lifecycle, now type-aware: Long-DCA, Short-DCA, and Scalper bots each
have a genuinely different schema (Scalper lives in a separate table,
scalper_positions, with no wallet_id/dca_count at all). Bot type is
detected by checking which table actually has rows for this bot_id -
data-driven, not based on name/method patterns which can be
inconsistent (confirmed: bot 747 is method='S58' but direction='long').

Usage:
    python3 bot_audit.py <bot_id>
    python3 bot_audit.py <bot_id> --verify-price <position_id>
        (Long/Short only - checks one position's recorded fill price
        against MEXC's real historical OHLCV at that timestamp)

READ-ONLY. Never writes to the database.
"""
import sys
import os
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv('/home/averion/Averion/.env')
import database as db
import redis
from datetime import datetime, timezone

db.init_pool()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

PASS = '✅'
WARN = '⚠️ '
FAIL = '❌'

warnings = []
failures = []

def flag(level, msg):
    if level == 'WARN':
        warnings.append(msg)
        print(f'{WARN}{msg}')
    elif level == 'FAIL':
        failures.append(msg)
        print(f'{FAIL}{msg}')
    else:
        print(f'{PASS}{msg}')

def get_redis_price(coin):
    try:
        keys = r.keys(f'price:*:{coin}/USDT')
        if keys:
            val = r.get(keys[0])
            return float(val) if val else None
    except Exception:
        pass
    return None

def verify_historical_price(coin, target_dt, recorded_price):
    try:
        import ccxt
        exchange = ccxt.mexc({'enableRateLimit': True})
        symbol = f'{coin}/USDT'
        since_ms = int(target_dt.timestamp() * 1000) - 5 * 60 * 1000
        candles = exchange.fetch_ohlcv(symbol, timeframe='1m', since=since_ms, limit=10)
        if not candles:
            return None, "No historical candles returned by MEXC for this symbol/time"
        target_ms = int(target_dt.timestamp() * 1000)
        closest = min(candles, key=lambda c: abs(c[0] - target_ms))
        ts, o, h, l, c, v = closest
        candle_time = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        in_range = l <= recorded_price <= h
        return {
            'candle_time': candle_time, 'open': o, 'high': h,
            'low': l, 'close': c, 'in_range': in_range,
        }, None
    except Exception as e:
        return None, f"Historical price check failed: {e}"

def audit_long_or_short_positions(cur, bot_id, wallet_id, trades_per_coin,
                                   direction_filter, verify_position_id):
    """Long and Short share the positions table and most columns,
    just with avg_cost/total_invested (Long) vs avg_sell_price/
    total_sold_usdt (Short) as the economically equivalent fields."""
    is_short = direction_filter == 'short'
    cost_col = 'avg_sell_price' if is_short else 'avg_cost'
    invested_col = 'total_sold_usdt' if is_short else 'total_invested'

    cur.execute(f"""
        SELECT id, coin, direction, status, {cost_col}, quantity,
               {invested_col}, dca_count, last_buy_price, last_dca_at,
               pos_dca_pct, pos_tp_pct, tp_armed, peak_price,
               wallet_id, opened_at, queued
        FROM positions
        WHERE bot_id=%s AND status='open' AND direction=%s
        ORDER BY opened_at ASC
    """, (bot_id, direction_filter))
    open_positions = cur.fetchall()
    print(f"  Total open positions: {len(open_positions)}\n")

    coin_counts = {}
    for p in open_positions:
        coin_counts[p[1]] = coin_counts.get(p[1], 0) + 1
    limit = int(trades_per_coin or 1)
    for coin_name, count in coin_counts.items():
        if count > limit:
            flag('FAIL', f"{coin_name}: {count} open positions exist, but trades_per_coin={limit} — "
                         f"this bot has more simultaneous positions on one coin than its own limit allows")

    for pos in open_positions:
        (pid, coin, pdir, pstatus, cost_val, quantity, invested_val,
         dca_count, last_buy_price, last_dca_at, pos_dca_pct,
         pos_tp_pct, tp_armed, peak_price, p_wallet_id, opened_at,
         queued) = pos

        print(f"  • [{pid}] {coin} ({pdir}) — dca_count={dca_count} opened={opened_at}")

        if p_wallet_id is None:
            flag('FAIL', f"  {coin} (id={pid}): wallet_id is NULL — DCA/TP cannot resolve a wallet for this position")
        elif p_wallet_id != wallet_id:
            flag('WARN', f"  {coin} (id={pid}): position wallet_id ({p_wallet_id}) differs from bot's current wallet_id ({wallet_id})")

        cost_f = float(cost_val or 0)
        quantity_f = float(quantity or 0)
        invested_f = float(invested_val or 0)
        if cost_f > 0 and quantity_f > 0:
            implied_invested = cost_f * quantity_f
            math_diff_pct = abs(implied_invested - invested_f) / invested_f * 100 if invested_f > 0 else 0
            if math_diff_pct > 5:
                flag('WARN', f"  {coin} (id={pid}): {cost_col} × quantity (${implied_invested:.4f}) doesn't closely "
                             f"match {invested_col} (${invested_f:.4f}) — {math_diff_pct:.1f}% off (fees/precision can explain a small gap)")

        current_price = get_redis_price(coin)
        if current_price is None:
            flag('WARN', f"  {coin} (id={pid}): no live price found in Redis right now — DCA/TP cannot evaluate this tick")
        else:
            last_buy = float(last_buy_price) if dca_count and dca_count > 0 and last_buy_price else cost_f
            if last_buy > 0:
                if is_short:
                    move_pct = (current_price - last_buy) / last_buy * 100
                else:
                    move_pct = (last_buy - current_price) / last_buy * 100
                required = float(pos_dca_pct) if pos_dca_pct else 7.0
                if move_pct >= required:
                    flag('WARN', f"  {coin} (id={pid}): PAST its DCA trigger right now — {move_pct:.2f}% move vs {required}% required. "
                                 f"If this persists across repeated audit runs, DCA may be stuck.")
                if is_short:
                    pnl_vs_cost = (cost_f - current_price) / cost_f * 100 if cost_f > 0 else 0
                else:
                    pnl_vs_cost = (current_price - cost_f) / cost_f * 100 if cost_f > 0 else 0
                print(f"      current_price={current_price}  P&L vs {cost_col}: {pnl_vs_cost:.2f}%  move since last buy: {move_pct:.2f}% (needs {required}%)")

        if queued:
            flag('WARN', f"  {coin} (id={pid}): queued=True — if this has been True for a long time, a buy attempt may have started and never cleared")

        if verify_position_id == pid:
            print(f"\n      ── Historical price verification for this position ──")
            target_dt = opened_at if opened_at.tzinfo else opened_at.replace(tzinfo=timezone.utc)
            result, err = verify_historical_price(coin, target_dt, cost_f)
            if err:
                flag('WARN', f"  {coin} (id={pid}) price verification: {err}")
            else:
                status_word = "WITHIN real range" if result['in_range'] else "OUTSIDE real range"
                print(f"      MEXC 1m candle near opened_at ({result['candle_time']}): "
                      f"open={result['open']} high={result['high']} low={result['low']} close={result['close']}")
                print(f"      Our recorded {cost_col} ${cost_f} is {status_word} of that real candle.")
                if not result['in_range']:
                    flag('WARN', f"  {coin} (id={pid}): recorded fill price ${cost_f} is OUTSIDE the real "
                                 f"historical low-high range (${result['low']}-${result['high']}) for that minute on MEXC")

    print(f"\n── 5. RECENT CLOSED POSITIONS (last 10) ──")
    cur.execute(f"""
        SELECT id, coin, {cost_col}, {invested_col}, total_sold_usdt,
               realized_pnl_usdt, realized_pnl_pct, close_reason,
               opened_at, closed_at
        FROM positions
        WHERE bot_id=%s AND status='closed' AND direction=%s
        ORDER BY closed_at DESC LIMIT 10
    """, (bot_id, direction_filter))
    closed = cur.fetchall()
    for c in closed:
        (cid, coin, cost_val, invested_val, sold, pnl_usdt, pnl_pct,
         reason, opened_at, closed_at) = c
        invested_f = float(invested_val or 0)
        sold_f = float(sold or 0)
        pnl_f = float(pnl_usdt or 0)
        implied_pnl = sold_f - invested_f if not is_short else invested_f - sold_f
        diff = abs(implied_pnl - pnl_f)
        print(f"  • [{cid}] {coin}: {invested_col}=${invested_f:.2f} sold=${sold_f:.2f} "
              f"realized_pnl=${pnl_f:.2f} ({pnl_pct}%) reason={reason} closed={closed_at}")
        if diff > 0.05:
            flag('WARN', f"  {coin} (id={cid}): implied P&L (${implied_pnl:.2f}) doesn't match "
                         f"stored realized_pnl_usdt (${pnl_f:.2f}) — off by ${diff:.2f}")

        if pnl_f > 0:
            cur.execute("SELECT amount_usdt, trade_profit FROM fee_debt WHERE position_id=%s", (cid,))
            fee_row = cur.fetchone()
            if not fee_row:
                flag('WARN', f"  {coin} (id={cid}): closed with profit ${pnl_f:.2f} but NO matching fee_debt row exists — performance fee may never have been charged")
            else:
                fee_amount, fee_trade_profit = fee_row
                expected_fee = float(fee_trade_profit or 0) * 0.20
                fee_diff = abs(float(fee_amount) - expected_fee)
                if fee_diff > 0.05:
                    flag('WARN', f"  {coin} (id={cid}): fee_debt.amount_usdt (${fee_amount}) doesn't match "
                                 f"20% of its own logged trade_profit (${expected_fee:.4f}) — off by ${fee_diff:.4f}")
    if not closed:
        print("  (none yet)")


def audit_scalper_positions(cur, bot_id):
    """scalper_positions has NO wallet_id, NO user_id, NO dca_count -
    a structurally different shape from Long/Short. Entries are meant
    to be short-lived (hold_seconds), so a long-open position is
    itself a red flag here, unlike Long/Short where staying open for
    days is completely normal."""
    cur.execute("""
        SELECT id, coin, entry_price, exit_price, entry_time, exit_time,
               hold_seconds, trigger_jump_pct, stop_loss_pct, pnl_pct,
               pnl_usdt, base_order, exit_reason, status
        FROM scalper_positions
        WHERE bot_id=%s AND status='open'
        ORDER BY entry_time ASC
    """, (bot_id,))
    open_positions = cur.fetchall()
    print(f"  Total open positions: {len(open_positions)}\n")

    now = datetime.now(timezone.utc)
    for pos in open_positions:
        (pid, coin, entry_price, exit_price, entry_time, exit_time,
         hold_seconds, trigger_jump_pct, stop_loss_pct, pnl_pct,
         pnl_usdt, base_order, exit_reason, status) = pos
        et = entry_time if entry_time.tzinfo else entry_time.replace(tzinfo=timezone.utc)
        age_seconds = (now - et).total_seconds()
        print(f"  • [{pid}] {coin} — entry={entry_price} opened={entry_time} age={age_seconds:.0f}s")

        if age_seconds > 600:
            flag('WARN', f"  {coin} (id={pid}): open for {age_seconds:.0f}s — Scalper trades are meant to be "
                         f"short-lived (timer-based exit), this may be a stuck position that never closed")

        current_price = get_redis_price(coin)
        if current_price is None:
            flag('WARN', f"  {coin} (id={pid}): no live price found in Redis right now")
        else:
            entry_f = float(entry_price or 0)
            if entry_f > 0:
                live_pnl_pct = (current_price - entry_f) / entry_f * 100
                print(f"      current_price={current_price}  live unrealized P&L: {live_pnl_pct:.2f}%")

    print(f"\n── RECENT CLOSED SCALPER POSITIONS (last 10) ──")
    cur.execute("""
        SELECT id, coin, entry_price, exit_price, hold_seconds,
               pnl_pct, pnl_usdt, base_order, exit_reason, exit_time
        FROM scalper_positions
        WHERE bot_id=%s AND status='closed'
        ORDER BY exit_time DESC LIMIT 10
    """, (bot_id,))
    closed = cur.fetchall()
    for c in closed:
        (cid, coin, entry_price, exit_price, hold_seconds, pnl_pct,
         pnl_usdt, base_order, exit_reason, exit_time) = c
        entry_f = float(entry_price or 0)
        exit_f = float(exit_price or 0)
        base_f = float(base_order or 2)
        pnl_pct_f = float(pnl_pct or 0)
        pnl_usdt_f = float(pnl_usdt or 0)
        print(f"  • [{cid}] {coin}: entry={entry_f} exit={exit_f} hold={hold_seconds}s "
              f"pnl=${pnl_usdt_f:.4f} ({pnl_pct_f:.2f}%) reason={exit_reason} closed={exit_time}")

        if entry_f > 0:
            implied_pnl_pct = (exit_f - entry_f) / entry_f * 100
            diff_pct = abs(implied_pnl_pct - pnl_pct_f)
            if diff_pct > 0.5:
                flag('WARN', f"  {coin} (id={cid}): (exit-entry)/entry ({implied_pnl_pct:.2f}%) doesn't closely "
                             f"match stored pnl_pct ({pnl_pct_f:.2f}%) — {diff_pct:.2f} points off")

        implied_pnl_usdt = base_f * pnl_pct_f / 100
        diff_usdt = abs(implied_pnl_usdt - pnl_usdt_f)
        if diff_usdt > 0.01:
            flag('WARN', f"  {coin} (id={cid}): base_order × pnl_pct (${implied_pnl_usdt:.4f}) doesn't closely "
                         f"match stored pnl_usdt (${pnl_usdt_f:.4f}) — off by ${diff_usdt:.4f}")

    if not closed:
        print("  (none yet)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bot_audit.py <bot_id> [--verify-price <position_id>]")
        sys.exit(1)
    bot_id = int(sys.argv[1])
    verify_position_id = None
    if '--verify-price' in sys.argv:
        idx = sys.argv.index('--verify-price')
        if idx + 1 < len(sys.argv):
            verify_position_id = int(sys.argv[idx + 1])

    print(f"\n{'='*70}")
    print(f"BOT AUDIT — bot_id={bot_id}")
    print(f"Generated {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*70}\n")

    with db.get_db() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, method, direction, trading_on, dca_on,
                   status, is_research, is_paper, wallet_id, user_id,
                   exchange_id, base_order, dca_percent, size_multiplier,
                   take_profit_percent, trailing_percent, trades_per_bot,
                   trades_per_coin, bot_params, created_at, expires_at
            FROM bots WHERE id=%s
        """, (bot_id,))
        bot = cur.fetchone()
        if not bot:
            print(f"{FAIL}No bot found with id={bot_id}")
            sys.exit(1)

        (bid, name, method, direction, trading_on, dca_on, status,
         is_research, is_paper, wallet_id, user_id, exchange_id,
         base_order, dca_percent, size_multiplier, tp_pct, trail_pct,
         trades_per_bot, trades_per_coin, bot_params, created_at,
         expires_at) = bot

        cur.execute("SELECT COUNT(*) FROM scalper_positions WHERE bot_id=%s", (bot_id,))
        has_scalper_rows = cur.fetchone()[0] > 0
        bot_type = 'scalper' if has_scalper_rows else direction

        print("── 1. BOT CONFIGURATION ──")
        print(f"  Name: {name}  |  Method: {method}  |  Direction: {direction}  |  Detected type: {bot_type}")
        print(f"  Status: {status}  |  trading_on: {trading_on}  |  dca_on: {dca_on}")
        print(f"  is_research: {is_research}  |  is_paper: {is_paper}")
        print(f"  wallet_id: {wallet_id}  |  user_id: {user_id}  |  exchange_id: {exchange_id}")
        print(f"  base_order: {base_order}  dca_percent: {dca_percent}  size_mult: {size_multiplier}")
        print(f"  tp_pct: {tp_pct}  trail_pct: {trail_pct}")
        print(f"  trades_per_bot: {trades_per_bot}  trades_per_coin: {trades_per_coin}")
        print(f"  created_at: {created_at}  expires_at: {expires_at}")
        print()

        if wallet_id is None:
            flag('FAIL', f"bot.wallet_id is NULL — this bot cannot reference a real wallet")
        else:
            flag('PASS', f"wallet_id is set ({wallet_id})")

        if is_research and (not bot_params or bot_params == {}):
            flag('WARN', "is_research=True but bot_params is empty/None — entry signal would use no parameters")
        elif is_research:
            flag('PASS', f"bot_params present: {bot_params}")

        if expires_at and expires_at < datetime.now(timezone.utc).replace(tzinfo=expires_at.tzinfo):
            if trading_on:
                flag('FAIL', f"expires_at ({expires_at}) is in the past but trading_on is still True")
            else:
                flag('PASS', f"Expired correctly: trading_on is False past expires_at")

        print("\n── 2. RESERVE WALLET (user-level, covers ALL bots for this user) ──")
        cur.execute("""
            SELECT balance_usdt, total_deposited, total_deducted, last_alert_level
            FROM reserve_wallets WHERE user_id=%s
        """, (user_id,))
        rw = cur.fetchone()
        if not rw:
            flag('WARN', f"No reserve_wallets row for user_id={user_id} — fee deduction would fail silently if a position closes profitably")
        else:
            rw_balance, rw_deposited, rw_deducted, rw_alert = rw
            print(f"  balance_usdt: ${rw_balance}  total_deposited: ${rw_deposited}  total_deducted: ${rw_deducted}  alert_level: {rw_alert}")
            if float(rw_balance) < 0:
                flag('WARN', f"Reserve balance is negative (${rw_balance}) — user is in fee debt. "
                             f"New positions should be blocked for ALL this user's bots until a deposit covers it "
                             f"(existing DCA/TP on already-open positions should still continue per locked rule).")

            cur.execute("SELECT COALESCE(SUM(amount_usdt), 0) FROM fee_debt WHERE user_id=%s", (user_id,))
            total_fee_debt_logged = cur.fetchone()[0]
            diff = abs(float(total_fee_debt_logged) - float(rw_deducted))
            if diff > 0.50:
                flag('WARN', f"Sum of fee_debt.amount_usdt (${total_fee_debt_logged}) doesn't match "
                             f"reserve_wallets.total_deducted (${rw_deducted}) — off by ${diff:.2f}")
            else:
                flag('PASS', f"fee_debt log matches total_deducted (within $0.50)")

        print("\n── 3. VIRTUAL WALLET ──")
        if wallet_id:
            cur.execute("""
                SELECT id, is_paper, current_balance, committed_usdt,
                       allocation_amount
                FROM virtual_wallets WHERE id=%s
            """, (wallet_id,))
            wallet = cur.fetchone()
            if not wallet:
                flag('FAIL', f"wallet_id={wallet_id} does not exist in virtual_wallets")
            else:
                w_id, w_paper, w_bal, w_committed, w_alloc = wallet
                print(f"  Wallet {w_id}: balance=${w_bal}  committed=${w_committed}  allocation=${w_alloc}")

                if bot_type != 'scalper':
                    cur.execute("""
                        SELECT COALESCE(SUM(total_invested), 0)
                        FROM positions
                        WHERE wallet_id=%s AND status='open' AND direction='long'
                    """, (wallet_id,))
                    actual_invested = cur.fetchone()[0]
                    diff = abs(float(actual_invested) - float(w_committed))
                    if diff > 0.50:
                        flag('FAIL', f"Wallet committed_usdt (${w_committed}) doesn't match sum of open LONG positions' "
                                     f"total_invested (${actual_invested}) for this wallet — off by ${diff:.2f}. "
                                     f"NOTE: covers all Long bots sharing this wallet, and excludes Short/Scalper which may use it too.")
                    else:
                        flag('PASS', f"committed_usdt matches sum of open Long positions' invested capital (within $0.50)")
                else:
                    print(f"  (Scalper bots have no per-position wallet_id - committed_usdt cross-check skipped for this bot type)")

                cur.execute("""
                    SELECT type, amount, balance_before, balance_after, created_at
                    FROM wallet_transactions
                    WHERE wallet_id=%s
                    ORDER BY created_at ASC
                """, (wallet_id,))
                txns = cur.fetchall()
                if txns:
                    print(f"  {len(txns)} transactions on record for this wallet")
                    last_balance_after = float(txns[-1][3] or 0)
                    diff2 = abs(last_balance_after - float(w_bal))
                    if diff2 > 0.50:
                        flag('WARN', f"Last wallet_transactions row's balance_after (${last_balance_after:.2f}) "
                                     f"doesn't match current_balance (${w_bal}) — off by ${diff2:.2f}. "
                                     f"May mean a balance change happened outside the transaction log.")
                    else:
                        flag('PASS', f"Transaction log's final balance_after matches current wallet balance")
                else:
                    flag('WARN', f"No wallet_transactions rows found for wallet {wallet_id} — no audit trail exists for this wallet's history")

        if bot_type == 'scalper':
            print("\n── 4. OPEN SCALPER POSITIONS ──")
            audit_scalper_positions(cur, bot_id)
        else:
            print(f"\n── 4. OPEN {bot_type.upper()} POSITIONS ──")
            audit_long_or_short_positions(cur, bot_id, wallet_id, trades_per_coin,
                                           bot_type, verify_position_id)

        print(f"\n{'='*70}")
        print(f"SUMMARY for bot {bot_id} ({name}) — type: {bot_type}")
        print(f"  {len(failures)} FAILURE(S), {len(warnings)} WARNING(S)")
        if failures:
            print(f"\n  Failures:")
            for f in failures:
                print(f"    {FAIL}{f}")
        if warnings:
            print(f"\n  Warnings:")
            for w in warnings:
                print(f"    {WARN}{w}")
        if not failures and not warnings:
            print(f"  {PASS} No issues found.")
        print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
