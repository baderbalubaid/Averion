"""
bot_audit.py - Independent verification tool for a single bot's full
lifecycle and current health. Not a trade-only tool - covers config
sanity, every open position's internal math, wallet consistency, and
recent closed positions. Built specifically so fixes can be proven
with concrete evidence, not just claimed to work.

Usage: python3 bot_audit.py <bot_id>

This is a READ-ONLY diagnostic tool. It never writes to the database.
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bot_audit.py <bot_id>")
        sys.exit(1)
    bot_id = int(sys.argv[1])

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

        print("── 1. BOT CONFIGURATION ──")
        print(f"  Name: {name}  |  Method: {method}  |  Direction: {direction}")
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

        print("\n── 2. WALLET ──")
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

                cur.execute("""
                    SELECT COALESCE(SUM(total_invested), 0)
                    FROM positions
                    WHERE wallet_id=%s AND status='open'
                """, (wallet_id,))
                actual_invested = cur.fetchone()[0]
                diff = abs(float(actual_invested) - float(w_committed))
                if diff > 0.50:
                    flag('FAIL', f"Wallet committed_usdt (${w_committed}) doesn't match sum of open positions' "
                                 f"total_invested (${actual_invested}) for this wallet — off by ${diff:.2f}. "
                                 f"NOTE: if multiple bots share this wallet, this check covers ALL of them, not just this bot.")
                else:
                    flag('PASS', f"committed_usdt matches sum of open positions' invested capital (within $0.50)")

        print("\n── 3. OPEN POSITIONS ──")
        cur.execute("""
            SELECT id, coin, direction, status, avg_cost, quantity,
                   total_invested, dca_count, last_buy_price, last_dca_at,
                   pos_dca_pct, pos_tp_pct, tp_armed, peak_price,
                   wallet_id, opened_at, queued
            FROM positions
            WHERE bot_id=%s AND status='open'
            ORDER BY opened_at ASC
        """, (bot_id,))
        open_positions = cur.fetchall()
        print(f"  Total open positions: {len(open_positions)}\n")

        for pos in open_positions:
            (pid, coin, pdir, pstatus, avg_cost, quantity, total_invested,
             dca_count, last_buy_price, last_dca_at, pos_dca_pct,
             pos_tp_pct, tp_armed, peak_price, p_wallet_id, opened_at,
             queued) = pos

            print(f"  • [{pid}] {coin} ({pdir}) — dca_count={dca_count} opened={opened_at}")

            if p_wallet_id is None:
                flag('FAIL', f"  {coin} (id={pid}): wallet_id is NULL — DCA/TP cannot resolve a wallet for this position")
            elif p_wallet_id != wallet_id:
                flag('WARN', f"  {coin} (id={pid}): position wallet_id ({p_wallet_id}) differs from bot's current wallet_id ({wallet_id})")

            avg_cost_f = float(avg_cost or 0)
            quantity_f = float(quantity or 0)
            invested_f = float(total_invested or 0)
            if avg_cost_f > 0 and quantity_f > 0:
                implied_invested = avg_cost_f * quantity_f
                math_diff_pct = abs(implied_invested - invested_f) / invested_f * 100 if invested_f > 0 else 0
                if math_diff_pct > 5:
                    flag('WARN', f"  {coin} (id={pid}): avg_cost × quantity (${implied_invested:.4f}) doesn't closely "
                                 f"match total_invested (${invested_f:.4f}) — {math_diff_pct:.1f}% off (fees/precision can explain a small gap)")

            current_price = get_redis_price(coin)
            if current_price is None:
                flag('WARN', f"  {coin} (id={pid}): no live price found in Redis right now — DCA/TP cannot evaluate this tick")
            else:
                last_buy = float(last_buy_price) if dca_count and dca_count > 0 and last_buy_price else avg_cost_f
                if last_buy > 0:
                    drop_pct = (last_buy - current_price) / last_buy * 100
                    required = float(pos_dca_pct) if pos_dca_pct else 7.0
                    if drop_pct >= required:
                        flag('WARN', f"  {coin} (id={pid}): PAST its DCA trigger right now — {drop_pct:.2f}% drop vs {required}% required. "
                                     f"If this persists across repeated audit runs, DCA may be stuck.")
                    pnl_vs_avg = (current_price - avg_cost_f) / avg_cost_f * 100 if avg_cost_f > 0 else 0
                    print(f"      current_price={current_price}  P&L vs avg_cost: {pnl_vs_avg:.2f}%  drop since last buy: {drop_pct:.2f}% (needs {required}%)")

            if queued:
                flag('WARN', f"  {coin} (id={pid}): queued=True — if this has been True for a long time, a buy attempt may have started and never cleared")

        print("\n── 4. RECENT CLOSED POSITIONS (last 10) ──")
        cur.execute("""
            SELECT id, coin, avg_cost, total_invested, total_sold_usdt,
                   realized_pnl_usdt, realized_pnl_pct, close_reason,
                   opened_at, closed_at
            FROM positions
            WHERE bot_id=%s AND status='closed'
            ORDER BY closed_at DESC LIMIT 10
        """, (bot_id,))
        closed = cur.fetchall()
        for c in closed:
            (cid, coin, avg_cost, invested, sold, pnl_usdt, pnl_pct,
             reason, opened_at, closed_at) = c
            invested_f = float(invested or 0)
            sold_f = float(sold or 0)
            pnl_f = float(pnl_usdt or 0)
            implied_pnl = sold_f - invested_f
            diff = abs(implied_pnl - pnl_f)
            print(f"  • [{cid}] {coin}: invested=${invested_f:.2f} sold=${sold_f:.2f} "
                  f"realized_pnl=${pnl_f:.2f} ({pnl_pct}%) reason={reason} closed={closed_at}")
            if diff > 0.05:
                flag('WARN', f"  {coin} (id={cid}): total_sold_usdt - total_invested (${implied_pnl:.2f}) doesn't match "
                             f"stored realized_pnl_usdt (${pnl_f:.2f}) — off by ${diff:.2f}")

        if not closed:
            print("  (none yet)")

        print(f"\n{'='*70}")
        print(f"SUMMARY for bot {bot_id} ({name})")
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
