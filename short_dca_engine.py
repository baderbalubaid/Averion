"""
short_dca_engine.py — Live Short DCA Engine
=============================================
Built June 20 2026, deliberately a SEPARATE file from
live_long_dca_engine.py - Short has fundamentally different mechanics
(sells not buys, limit-order buybacks, coin-quantity wallets instead
of USDT) and keeping it separate avoids any risk of breaking the
well-tested Long engine while building this.

Core mechanics (LOCKED spec, 13_LOCKED_DECISIONS.md):
- User must already hold the coin before opening a Short bot
- Bot sells portions as price RISES (mirrors Long DCA, direction flipped)
- avg_sell_price = weighted average of all sells so far
- TP target = avg_sell_price * (1 - TP%) - price must DROP to trigger buyback
- Sells are MARKET orders. Buyback is ALWAYS a LIMIT order (reserves
  USDT on the exchange, prevents Long DCA queue from grabbing it)
- PENDING_BUYBACK flag blocks Long DCA on the SAME virtual wallet
  while a sell has happened but the limit buyback isn't placed yet
- No trailing for Short (fixed limit buyback already locks the target)
- Entry methods: ASAP or Customized only (no signal-based entry timing
  the way Long has - user already holds the coin)
- Parameter mode: Smart (reuses the same per-coin coin_parameters
  classification system Long already uses) or Customized
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
import time
import threading
import redis as _redis
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv('/home/averion/Averion/.env')
import database as db
from executor import get_executor, PaperAdapter, LiveAdapter

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

def get_redis():
    return _redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_redis_price(r, coin, exchange_name='MEXC Paper'):
    try:
        val = r.get(f'price:{exchange_name}:{coin}/USDT')
        return float(val) if val else None
    except Exception:
        return None

# ── Load active Short bots ──────────────────────────────────────────
def load_short_bots():
    """Load all active Short DCA bots with wallet info (coin
    quantity, not USDT - this is the key structural difference from
    Long's load_live_long_bots())."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                b.id, b.user_id, b.exchange_id, b.wallet_id,
                b.name, b.entry_method, b.bot_params,
                b.dca_percent, b.spacing_multiplier, b.size_multiplier,
                b.take_profit_percent, b.profit_coin,
                b.trades_per_coin, b.trading_on, b.dca_on,
                vw.is_paper, vw.current_balance, vw.coin as wallet_coin,
                e.custom_name as exchange_name
            FROM bots b
            JOIN virtual_wallets vw ON b.wallet_id = vw.id
            JOIN exchanges e ON b.exchange_id = e.id
            WHERE b.is_research = FALSE
            AND b.is_template = FALSE
            AND b.direction = 'short'
            AND b.trading_on = TRUE
            AND b.status = 'open'
            AND b.status != 'deleted'
            ORDER BY b.user_id, b.id
        """)
        rows = cur.fetchall()

    bots = []
    for r in rows:
        import json as _j
        params = r[6]
        if isinstance(params, str):
            try:
                params = _j.loads(params)
            except Exception:
                params = {}
        params = params or {}
        bots.append({
            'id': r[0], 'user_id': r[1], 'exchange_id': r[2], 'wallet_id': r[3],
            'name': r[4], 'entry_method': r[5], 'bot_params': params,
            'dca_percent': float(r[7] or 7), 'spacing_multiplier': float(r[8] or 1.4),
            'size_multiplier': float(r[9] or 1.5), 'tp_percent': float(r[10] or 5),
            'profit_coin': r[11] or 'USDT', 'trades_per_coin': int(r[12] or 1),
            'trading_on': r[13], 'dca_on': r[14],
            'wallet': {
                'id': r[3], 'is_paper': r[15], 'current_balance': float(r[16] or 0),
                'coin': r[17], 'exchange_id': r[2], 'exchange_name': r[18],
            },
            'parameter_mode': params.get('parameter_mode', 'customized'),
        })
    return bots

# ── Load open Short positions for a bot ─────────────────────────────
def load_open_short_positions(bot_id):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, coin, avg_sell_price, last_sell_price, quantity,
                   total_sold_usdt, dca_count, pending_buyback,
                   short_buyback_order_id, sequence_number,
                   pos_tp_pct, pos_dca_pct, standby_amount
            FROM positions
            WHERE bot_id=%s AND status='open' AND direction='short'
        """, (bot_id,))
        rows = cur.fetchall()
    positions = []
    for r in rows:
        positions.append({
            'id': r[0], 'coin': r[1],
            'avg_sell_price': float(r[2] or 0), 'last_sell_price': float(r[3] or 0),
            'quantity': float(r[4] or 0), 'total_sold_usdt': float(r[5] or 0),
            'dca_count': int(r[6] or 0), 'pending_buyback': r[7] or False,
            'short_buyback_order_id': r[8], 'sequence_number': r[9],
            'pos_tp_pct': float(r[10]) if r[10] is not None else None,
            'standby_amount': float(r[12] or 0),
            'pos_dca_pct': float(r[11]) if r[11] is not None else None,
        })
    return positions

from live_long_dca_engine import load_coin_params_cache

def get_short_params(bot, coin, coin_params_cache):
    """Returns (dca_pct, spacing_mult, tp_pct) for this bot+coin.
    Smart mode reuses the SAME coin_parameters classification system
    Long already uses - a coin's volatility number is the same
    whether price is rising or falling, so no separate 'short
    volatility' calculation is needed."""
    if bot.get('parameter_mode') == 'smart':
        cp = coin_params_cache.get(coin, {})
        dca_pct = cp.get('dca_spacing', bot['dca_percent'])
        tp_pct = cp.get('take_profit', bot['tp_percent'])
        spacing_mult = bot['spacing_multiplier']  # not in coin_parameters, use bot's own
        return dca_pct, spacing_mult, tp_pct
    return bot['dca_percent'], bot['spacing_multiplier'], bot['tp_percent']

def check_sell_trigger(pos, current_price, bot, coin_params_cache):
    """Mirrors Long's needs_dca() but inverted - price must RISE to
    trigger the next sell, not drop. Level 1 uses activation price
    (last_sell_price will be 0 before the first sell); Level 2+ uses
    the actual last_sell_price. Returns (should_sell, sell_quantity)
    or (False, 0)."""
    dca_pct, spacing_mult, tp_pct = get_short_params(bot, pos['coin'], coin_params_cache)
    dca_count = pos['dca_count']
    reference_price = pos['last_sell_price'] if pos['last_sell_price'] > 0 else pos['avg_sell_price']
    if reference_price <= 0:
        return False, 0  # no valid reference yet

    effective_spacing = dca_pct * (spacing_mult ** dca_count)
    trigger_price = reference_price * (1 + effective_spacing / 100)

    if current_price < trigger_price:
        return False, 0  # price hasn't risen enough yet

    return True, None  # caller computes actual quantity separately

# Min order size rarely changes - fast DB read, refreshed daily
# by refresh_min_orders.py via cron. Never a slow live API call.
def get_cached_min_order(bot, coin):
    result = db.get_min_order(bot['wallet']['exchange_id'], coin)
    if result is None:
        return {'min_amount': 0, 'min_cost': 1.0}
    return result

# Computes how much coin to sell for this DCA level. Returns
# (sell_qty, new_standby_amount). sell_qty=0 means skip entirely
# this tick. Partial fills (>=75% of required, meeting exchange
# minimum) sell what's available and carry the remainder forward
# as standby_amount, added on top of the NEXT level's requirement.
def compute_sell_amount(bot, wallet_current_balance, dca_count, current_price, coin, standby_amount=0):
    params = bot.get('bot_params', {})
    mode = params.get('short_amount_mode', 'wallet_pct')
    value = float(params.get('short_amount_value', 10))

    if mode == 'wallet_pct':
        base_qty = wallet_current_balance * (value / 100)
    elif mode == 'coin_quantity':
        base_qty = value
    elif mode == 'usdt_equivalent':
        base_qty = value / current_price if current_price > 0 else 0
    else:
        base_qty = wallet_current_balance * 0.10

    size_mult = bot['size_multiplier']
    scaled_qty = base_qty * (size_mult ** dca_count)
    required_total = scaled_qty + standby_amount

    available_cap = db.get_available_for_short(bot['user_id'], coin, bot['wallet'])
    effective_available = wallet_current_balance if available_cap is None else min(wallet_current_balance, available_cap)

    min_req = get_cached_min_order(bot, coin)
    min_qty_floor = max(
        min_req.get('min_amount', 0) or 0,
        (min_req.get('min_cost', 0) or 0) / current_price if current_price > 0 else 0
    )

    if effective_available >= required_total:
        return required_total, 0

    threshold = max(required_total * 0.75, min_qty_floor)
    if effective_available >= threshold and effective_available >= min_qty_floor:
        new_standby = required_total - effective_available
        return effective_available, new_standby

    return 0, standby_amount

def execute_short_sell(pos, bot, sell_quantity):
    """Executes a market sell for a Short position, recalculates
    avg_sell_price/TP target, cancels old buyback limit + places a
    fresh one. PENDING_BUYBACK is set immediately on sell (before the
    buyback is even placed) so Long DCA on this wallet holds right
    away - cleared only once the new limit order is confirmed placed.
    If limit placement fails (insufficient USDT), the flag stays SET
    so Long DCA stays blocked and we retry next cycle - Short buyback
    funding always wins the race for funds on that wallet."""
    wallet = bot['wallet']
    executor = get_executor(wallet)
    coin = pos['coin']

    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE positions SET pending_buyback=TRUE, pending_buyback_since=NOW() WHERE id=%s", (pos['id'],))
        conn.commit()

    with db.get_db() as conn:
        result = executor.place_short_sell(coin, sell_quantity, wallet, conn)
        conn.commit()

    if not result.success:
        print(f'Short sell failed: {coin} {result.error}')
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE positions SET pending_buyback=FALSE WHERE id=%s", (pos['id'],))
            conn.commit()
        return False

    new_sold_usdt_this_fill = result.quantity * result.fill_price
    new_total_sold_usdt = pos['total_sold_usdt'] + new_sold_usdt_this_fill
    new_quantity = pos['quantity'] + result.quantity
    new_avg_sell_price = new_total_sold_usdt / new_quantity if new_quantity > 0 else result.fill_price
    new_dca_count = pos['dca_count'] + 1

    dca_pct, spacing_mult, tp_pct = get_short_params(bot, coin, {})
    tp_target = new_avg_sell_price * (1 - tp_pct / 100)

    with db.get_db() as conn:
        cur = conn.cursor()
        if pos['short_buyback_order_id']:
            executor.cancel_limit_order(pos['short_buyback_order_id'], coin, wallet, conn)

        cur.execute("""
            UPDATE positions
            SET avg_sell_price=%s, last_sell_price=%s, quantity=%s,
                total_sold_usdt=%s, dca_count=%s
            WHERE id=%s
        """, (new_avg_sell_price, result.fill_price, new_quantity,
              new_total_sold_usdt, new_dca_count, pos['id']))
        conn.commit()

    print(f'SHORT SELL: {bot["name"]} {coin} @ ${result.fill_price:.6f} '
          f'qty={result.quantity:.4f} avg_sell=${new_avg_sell_price:.6f} '
          f'tp_target=${tp_target:.6f}')

    # Buyback target quantity depends on profit_coin (ADDED June 20
    # 2026): 'USDT' mode buys back exactly the quantity sold (the
    # buyback price is lower than the sell price, so this naturally
    # leaves a leftover USDT difference sitting in the exchange
    # account - that leftover IS the profit, banked as cash with zero
    # extra work needed). 'base_coin' mode spends ALL the proceeds
    # raised to buy back coin at the now-lower price, getting MORE
    # coin than was sold - profit shows up as extra coin quantity.
    if bot.get('profit_coin') == 'base_coin':
        buyback_quantity = new_total_sold_usdt / tp_target if tp_target > 0 else new_quantity
    else:
        buyback_quantity = new_quantity

    with db.get_db() as conn:
        limit_result = executor.place_limit_buyback(
            pos['id'], coin, tp_target, buyback_quantity, wallet, conn
        )
        cur = conn.cursor()
        if limit_result.success:
            cur.execute("""
                UPDATE positions
                SET short_buyback_order_id=%s, pending_buyback=FALSE,
                    short_buyback_reserved_usdt=%s, pending_buyback_since=NULL
                WHERE id=%s
            """, (limit_result.order_id, limit_result.usdt_reserved, pos['id']))
            conn.commit()
            print(f'Buyback limit placed: {coin} target=${tp_target:.6f} qty={new_quantity:.4f}')
        else:
            conn.commit()
            print(f'Buyback limit FAILED (will retry, Long DCA held on wallet): {limit_result.error}')

    return True

def retry_pending_buybacks(bots_by_id):
    """Each cycle, retry placing the buyback limit order for any
    position stuck in pending_buyback=TRUE with no order_id yet (sell
    happened, limit placement failed last time - e.g. insufficient
    USDT because something else used it first). Per the locked
    priority rule, Short buyback funding wins the race for funds on
    that wallet until it succeeds, so we keep retrying every cycle."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, coin, avg_sell_price, quantity, bot_id, pos_tp_pct
            FROM positions
            WHERE direction='short' AND status='open'
            AND pending_buyback=TRUE AND short_buyback_order_id IS NULL
        """)
        stuck = cur.fetchall()

    for pos_id, coin, avg_sell_price, quantity, bot_id, pos_tp_pct in stuck:
        bot = bots_by_id.get(bot_id)
        if not bot:
            continue
        wallet = bot['wallet']
        executor = get_executor(wallet)
        dca_pct, spacing_mult, tp_pct = get_short_params(bot, coin, {})
        if pos_tp_pct is not None:
            tp_pct = float(pos_tp_pct)
        tp_target = float(avg_sell_price) * (1 - tp_pct / 100)

        with db.get_db() as conn:
            limit_result = executor.place_limit_buyback(
                pos_id, coin, tp_target, float(quantity), wallet, conn
            )
            if limit_result.success:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE positions
                    SET short_buyback_order_id=%s, pending_buyback=FALSE,
                        short_buyback_reserved_usdt=%s, pending_buyback_since=NULL
                    WHERE id=%s
                """, (limit_result.order_id, limit_result.usdt_reserved, pos_id))
                conn.commit()
                print(f'Retry succeeded: buyback limit placed for {coin} pos={pos_id}')
            else:
                conn.commit()
                print(f'Retry still failing for {coin} pos={pos_id}: {limit_result.error}')

def handle_buyback_fill(pos_id, coin, total_sold_usdt, fill_result, bot, wallet, executor):
    """Position's buyback limit has filled - credit wallet with
    bought-back coin (paper only - live syncs externally), calculate
    realized profit, deduct platform fee (same mechanism/wallet as
    Long and Scalper - always from reserve_wallets, fee basis always
    in USDT terms regardless of profit_coin), close the position."""
    buyback_cost = fill_result.fill_quantity * fill_result.fill_price
    realized_pnl_usdt = total_sold_usdt - buyback_cost
    realized_pnl_pct = (realized_pnl_usdt / total_sold_usdt * 100) if total_sold_usdt > 0 else 0

    with db.get_db() as conn:
        cur = conn.cursor()
        if wallet.get('is_paper') and isinstance(executor, PaperAdapter):
            executor.credit_buyback_to_wallet(wallet['id'], fill_result.fill_quantity, conn)

        cur.execute("""
            UPDATE positions
            SET status='closed', closed_at=NOW(), close_reason='tp',
                realized_pnl_usdt=%s, realized_pnl_pct=%s
            WHERE id=%s
        """, (realized_pnl_usdt, realized_pnl_pct, pos_id))
        conn.commit()

    emoji = '\U0001F49A' if realized_pnl_usdt > 0 else '\u2764\uFE0F'
    print(f'{emoji} SHORT BUYBACK FILLED: {bot["name"]} {coin} '
          f'buyback_qty={fill_result.fill_quantity:.4f} @ ${fill_result.fill_price:.6f} '
          f'pnl=${realized_pnl_usdt:.4f} ({realized_pnl_pct:.2f}%)')

    if realized_pnl_usdt > 0:
        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT is_research_account, is_admin, is_zero_fee, fee_override
                    FROM users WHERE id=%s
                """, (bot['user_id'],))
                urow = cur.fetchone()
            skip_fee = urow and (urow[0] or urow[1] or urow[2])
            if not skip_fee:
                fee_pct = float(urow[3]) if urow and urow[3] is not None else 20.0
                fee = realized_pnl_usdt * (fee_pct / 100)
                db.deduct_performance_fee(bot['user_id'], pos_id, fee, realized_pnl_usdt)
        except Exception as e:
            print(f'Short fee deduction error: {e}')

def check_buyback_fills(bots_by_id):
    """Each cycle, checks every open Short position with an active
    buyback limit order for fills."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, coin, avg_sell_price, quantity, total_sold_usdt,
                   bot_id, short_buyback_order_id
            FROM positions
            WHERE direction='short' AND status='open'
            AND short_buyback_order_id IS NOT NULL
        """)
        active = cur.fetchall()

    for pos_id, coin, avg_sell_price, quantity, total_sold_usdt, bot_id, order_id in active:
        bot = bots_by_id.get(bot_id)
        if not bot:
            continue
        wallet = bot['wallet']
        executor = get_executor(wallet)

        with db.get_db() as conn:
            fill_result = executor.check_limit_fill(order_id, coin, wallet, conn)

        if fill_result.filled:
            handle_buyback_fill(pos_id, coin, float(total_sold_usdt), fill_result, bot, wallet, executor)

print("Chunk 4 loaded: buyback fill detection + handling ready")

def open_short_position_record(bot, coin):
    """Creates the initial position record for a new Short bot+coin
    pairing. No trade happens here - the user already holds the coin.
    This just establishes the reference price (current market price)
    the first sell-trigger will be measured against. The very first
    sell happens later through the SAME execute_short_sell() used for
    every subsequent sell, once price rises enough."""
    r = get_redis()
    current_price = get_redis_price(r, coin, bot['wallet']['exchange_name'])
    if not current_price:
        print(f'No price available yet for {coin}, skipping open')
        return None
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO positions (bot_id, user_id, exchange_id, wallet_id, coin,
                                    direction, status, avg_sell_price, last_sell_price,
                                    quantity, total_sold_usdt, dca_count, opened_at,
                                    profit_coin, entry_method, entry_method_at_open,
                                    is_paper)
            VALUES (%s, %s, %s, %s, %s, 'short', 'open', %s, 0, 0, 0, 0, NOW(), %s, %s, %s, %s)
            RETURNING id
        """, (bot['id'], bot['user_id'], bot['exchange_id'], bot['wallet_id'], coin,
              current_price, bot['profit_coin'], bot['entry_method'], bot['entry_method'],
              bot['wallet']['is_paper']))
        pos_id = cur.fetchone()[0]
        conn.commit()
    print(f'SHORT POSITION OPENED (tracking only, no trade yet): {bot["name"]} {coin} @ ${current_price:.6f}')
    return pos_id

def run_cycle():
    """One full engine cycle: open new position slots where eligible,
    check sell triggers on existing positions, execute sells, check
    buyback fills, retry any stuck buyback placements. Also refreshes
    the tick-based cache used by on_price_update() for real-time
    checking - this periodic loop remains as a safety-net backup."""
    refresh_short_cache()
    r = get_redis()
    bots = load_short_bots()
    bots_by_id = {b['id']: b for b in bots}

    smart_mode_active = any(b.get('parameter_mode') == 'smart' for b in bots)
    coin_params_cache = load_coin_params_cache() if smart_mode_active else {}

    # NOTE: new-slot opening and sell-trigger checks have moved to
    # on_price_update() for true zero-delay reactive behavior (ADDED
    # June 20 2026). This periodic loop is now ONLY a safety-net
    # backup (in case a tick was somehow missed) plus the genuinely
    # periodic bookkeeping: buyback-fill safety check and stuck
    # buyback retries.
    for bot in bots:
        if not bot['trading_on'] or not bot['dca_on']:
            continue
        coin = bot['wallet']['coin']
        open_positions = load_open_short_positions(bot['id'])
        existing_for_coin = [p for p in open_positions if p['coin'] == coin]

        current_price = get_redis_price(r, coin, bot['wallet']['exchange_name'])
        if not current_price:
            continue

        for pos in existing_for_coin:
            should_sell, _ = check_sell_trigger(pos, current_price, bot, coin_params_cache)
            if should_sell:
                sell_qty, new_standby = compute_sell_amount(
                    bot, bot['wallet']['current_balance'], pos['dca_count'], current_price,
                    pos['coin'], pos.get('standby_amount', 0)
                )
                if new_standby != pos.get('standby_amount', 0):
                    db.update_standby_amount(pos['id'], new_standby)
                if sell_qty > 0:
                    execute_short_sell(pos, bot, sell_qty)

    check_buyback_fills(bots_by_id)
    retry_pending_buybacks(bots_by_id)

_running = False
_cycle_thread = None

def _engine_loop():
    global _running
    print('Short DCA engine starting (60s cycle)...')
    while _running:
        try:
            r = get_redis()
            r.setex('engine:short_dca:heartbeat', 150, str(time.time()))
        except Exception:
            pass
        try:
            run_cycle()
        except Exception as e:
            print(f'Short engine cycle error: {e}')
        time.sleep(60)

def is_engine_alive():
    """Watchdog check: is the Short DCA thread actually running right now?"""
    global _cycle_thread
    return _running and _cycle_thread is not None and _cycle_thread.is_alive()

def start_engine():
    """Start the Short DCA engine. NOT a daemon thread - same reasoning
    as live_long_dca_engine.py's start_engine(): daemon threads die
    silently with zero warning if the host process restarts/reloads
    internally. Non-daemon means a crash is visible and a watchdog can
    detect + restart it, rather than the engine just vanishing forever."""
    global _running, _cycle_thread
    if is_engine_alive():
        return
    _running = True
    _cycle_thread = threading.Thread(target=_engine_loop, daemon=False)
    _cycle_thread.start()
    print('\u2705 Short DCA engine started')

if __name__ == '__main__':
    db.init_pool()
    _running = True
    _engine_loop()

# ── Real-time tick-based checking (ADDED June 20 2026) ──────────────
# Previously the only check was the 60s polling loop, which could
# miss a price spike that rises and falls back within that window -
# Long DCA's TP and Scalper's entry checks already work tick-by-tick
# via the websocket feed; this brings Short DCA in line with that.
_short_cache_lock = __import__('threading').Lock()
_short_bots_by_coin = {}  # coin -> bot dict, refreshed periodically
_short_positions_by_coin = {}  # coin -> list of open position dicts

def refresh_short_cache():
    """Refreshes the in-memory coin->bot/position lookup used by
    on_price_update() for fast per-tick checks (no DB hit per tick)."""
    global _short_bots_by_coin, _short_positions_by_coin
    bots = load_short_bots()
    bots_by_coin = {}
    positions_by_coin = {}
    for bot in bots:
        if not bot['trading_on']:
            continue
        coin = bot['wallet']['coin']
        bots_by_coin[coin] = bot
        positions_by_coin[coin] = load_open_short_positions(bot['id'])
    with _short_cache_lock:
        _short_bots_by_coin = bots_by_coin
        _short_positions_by_coin = positions_by_coin

def on_price_update(coin, price):
    """Called on every websocket price tick (registered in
    websocket_prices.py, same pattern as Long DCA's TP callback and
    Scalper's entry check). Fast no-op for the 1700+ coins with no
    active Short bot - only does real work for matched coins."""
    with _short_cache_lock:
        bot = _short_bots_by_coin.get(coin)
        positions = list(_short_positions_by_coin.get(coin, []))
    if not bot:
        return

    is_paper = bot['wallet']['is_paper']

    # Open a new trade slot reactively, the instant it's eligible
    # (ADDED June 20 2026 per explicit instruction - this previously
    # only happened in the 60s run_cycle loop, meaning a bot under
    # its trades_per_coin capacity could wait up to a minute before
    # opening its next slot. ASAP entry has no signal dependency at
    # all, so there's no reason for any delay here - zero-delay
    # applies to opening new slots just as much as to sells/buybacks.)
    if bot['trading_on'] and bot['entry_method'] == 'asap' \
            and len(positions) < bot['trades_per_coin'] \
            and bot['wallet']['current_balance'] > 0:
        try:
            new_pos_id = open_short_position_record(bot, coin)
            if new_pos_id:
                first_pos = {
                    'id': new_pos_id, 'coin': coin, 'avg_sell_price': price,
                    'last_sell_price': 0, 'quantity': 0, 'total_sold_usdt': 0,
                    'dca_count': 0, 'short_buyback_order_id': None
                }
                first_qty, new_standby = compute_sell_amount(
                    bot, bot['wallet']['current_balance'], 0, price, coin, 0
                )
                if first_qty > 0:
                    execute_short_sell(first_pos, bot, first_qty)
                if new_standby > 0:
                    db.update_standby_amount(new_pos_id, new_standby)
                refresh_short_cache()
        except Exception as e:
            print(f'\u26a0\ufe0f Short on_price_update new-slot error for {coin}: {e}')

    for pos in positions:
        try:
            should_sell, _ = check_sell_trigger(pos, price, bot, {})
            if should_sell:
                sell_qty, new_standby = compute_sell_amount(
                    bot, bot['wallet']['current_balance'], pos['dca_count'], price,
                    coin, pos.get('standby_amount', 0)
                )
                if new_standby != pos.get('standby_amount', 0):
                    db.update_standby_amount(pos['id'], new_standby)
                if sell_qty > 0:
                    execute_short_sell(pos, bot, sell_qty)
                    refresh_short_cache()
                    continue
        except Exception as e:
            print(f'\u26a0\ufe0f Short on_price_update sell-check error for {coin}: {e}')

        # Buyback fill check: tick-speed for BOTH paper and live
        # (UPDATED June 20 2026 per explicit instruction - live now
        # checks the exchange on every tick too, not throttled. Real
        # rate-limit risk if many positions are simultaneously active
        # is knowingly accepted in exchange for true zero-delay
        # behavior; the try/except below still protects against an
        # exchange error crashing the engine, it just doesn't
        # preemptively limit call frequency.)
        if pos.get('short_buyback_order_id'):
            try:
                executor = get_executor(bot['wallet'])
                with db.get_db() as conn:
                    fill_result = executor.check_limit_fill(
                        pos['short_buyback_order_id'], coin, bot['wallet'], conn
                    )
                if fill_result.filled:
                    handle_buyback_fill(
                        pos['id'], coin, pos['total_sold_usdt'], fill_result, bot,
                        bot['wallet'], executor
                    )
                    refresh_short_cache()
            except Exception as e:
                print(f'\u26a0\ufe0f Short on_price_update fill-check error for {coin}: {e}')
