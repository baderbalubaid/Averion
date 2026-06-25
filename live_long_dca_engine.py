"""
live_long_dca_engine.py — Averion Live Long DCA Engine
=======================================================
Handles live user Long DCA bots only.
- Reads from: bots (is_research=FALSE, is_template=FALSE)
- Writes to:  positions (FIXED June 23 2026 - was the stale live_dca_positions table)
- Execution:  executor.py (PaperAdapter or LiveAdapter)
- TP:         WebSocket price callback (real-time)
- DCA queue:  60s cycle, per-user isolation

Research engine (research_engine.py) is NEVER touched here.
"""

import os
import time
import threading
import redis as _redis
from datetime import datetime, timezone
from dotenv import load_dotenv
import database as db
from executor import get_executor, PaperAdapter, LiveAdapter

load_dotenv()

REDIS_HOST     = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT     = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# ── Redis ──────────────────────────────────────────────────────────
_shared_redis_conn = None
def get_redis():
    # FIXED June 22 2026: was creating a BRAND NEW redis connection on
    # every single call - found during a real memory leak investigation
    # (gc object counts showed RLock/list objects exploding). This gets
    # called on every price tick now via the ASAP reactive handler, so
    # this was creating a massive number of connection objects per
    # minute. One shared, reusable module-level connection instead.
    global _shared_redis_conn
    if _shared_redis_conn is None:
        _shared_redis_conn = _redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT,
            password=REDIS_PASSWORD, decode_responses=True
        )
    return _shared_redis_conn

def get_redis_price(r, coin):
    """Get latest price from Redis. Returns float or None."""
    keys = r.keys(f'price:*:{coin}/USDT')
    for key in keys:
        val = r.get(key)
        if val:
            return float(val)
    return None

# ── Load active live long bots ─────────────────────────────────────
def is_st_coin(coin, exchange_name, r):
    # Check if coin is ST/suspended via Redis cache
    cached = r.get(f'st:{exchange_name}:{coin}')
    if cached:
        return cached == 'true'
    return False

def load_live_long_bots():
    """Load all active live long DCA bots with wallet info."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                b.id, b.user_id, b.exchange_id, b.wallet_id,
                b.name, b.method, b.entry_method,
                b.base_order, b.dca_percent, b.size_multiplier,
                b.take_profit_percent, b.trailing_percent,
                b.trades_per_bot, b.trades_per_coin,
                b.trading_on, b.dca_on, b.status,
                b.bot_params,
                vw.is_paper, vw.current_balance, vw.committed_usdt,
                vw.allocation_amount, vw.coin as wallet_coin,
                e.exchange as exchange_name,
                b.reserve_floor, b.resume_threshold, b.auto_resume, b.floor_paused,
                b.profit_coin
            FROM bots b
            JOIN virtual_wallets vw ON b.wallet_id = vw.id
            JOIN exchanges e ON b.exchange_id = e.id
            WHERE b.is_research = FALSE
            AND b.is_template = FALSE
            AND b.direction = 'long'
            AND b.status = 'open'
            AND b.status != 'deleted'
            AND (b.method LIKE 'DCA%' OR b.method LIKE 'E%')
            ORDER BY b.user_id, b.id
            -- FIXED June 25 2026: was "AND b.trading_on = TRUE" here,
            -- which excluded the bot from this entire function -
            -- silently freezing DCA and TP on every existing open
            -- position the moment a bot stopped, went into debt, or
            -- expired. Per locked discussion: trading_on=FALSE should
            -- only ever block NEW positions/entries, never existing
            -- ones - DCA and TP must keep managing what's already
            -- open regardless of why trading stopped. New-position
            -- opening is already separately, explicitly gated by
            -- trading_on at its own call sites (open_position() at
            -- line ~834 and the ASAP-bot filter at ~930), so removing
            -- the filter here does not reopen that door.
        """)
        rows = cur.fetchall()

    bots = []
    for r in rows:
        bots.append({
            'id':               r[0],
            'user_id':          r[1],
            'exchange_id':      r[2],
            'wallet_id':        r[3],
            'name':             r[4],
            'method':           r[5],
            'entry_method':     r[6],
            'base_order':       float(r[7] or 10),
            'dca_percent':      float(r[8] or 7),
            'size_multiplier':  float(r[9] or 1.5),
            'tp_percent':       float(r[10] or 5),
            'trailing_percent': float(r[11] or 2),
            'trades_per_bot':   int(r[12] or 5),
            'trades_per_coin':  int(r[13] or 1),
            'trading_on':       r[14],
            'dca_on':           r[15],
            'bot_params':       r[17] or {},
            'wallet': {
                'id':            r[3],
                'is_paper':      r[18],
                'current_balance': float(r[19] or 0),
                'committed_usdt':  float(r[20] or 0),
                'allocation_amount': float(r[21] or 0),
                'exchange_id':   r[2],
                'exchange_name': r[23],
            },
            'reserve_floor':    float(r[24]) if r[24] is not None else None,
            'resume_threshold': float(r[25]) if r[25] is not None else None,
            'auto_resume':      r[26] if r[26] is not None else True,
            'floor_paused':     r[27] or False,
            'profit_coin':      r[28] or 'USDT',
        })
    return bots

# ── Load open positions for a bot ──────────────────────────────────
def load_open_positions(bot_id):
    # FIXED June 23 2026: was reading from live_dca_positions, a
    # stale/abandoned table found during a real-money DCA bug
    # investigation - the codebase map (generate_codebase_map.py)
    # showed it touched by only 3 files vs 22 for the genuinely
    # maintained positions table. Real positions ("ALVA", "XT" on
    # bot 745) existed correctly in positions but were missing or
    # marked closed in live_dca_positions, so this DCA-trigger check
    # never even saw them. Targeted fix: redirect to positions,
    # the actively-maintained table everything else uses, instead
    # of reorganizing/merging tables (too high-risk for an unknown
    # number of other connected places).
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, coin, avg_cost, quantity, total_invested,
                   dca_count, tp_armed, peak_price,
                   pos_tp_pct, pos_trail_pct, pos_dca_pct,
                   status, opened_at, wallet_id, last_buy_price
            FROM positions
            WHERE bot_id=%s AND status='open' AND direction='long'
            ORDER BY opened_at ASC
        """, (bot_id,))
        rows = cur.fetchall()
    return [{
        'id':             r[0],
        'coin':           r[1],
        'avg_cost':       float(r[2] or 0),
        'quantity':       float(r[3] or 0),
        'total_invested': float(r[4] or 0),
        'dca_count':      int(r[5] or 0),
        'tp_armed':       r[6],
        'peak_price':     float(r[7] or 0),
        'pos_tp_pct':     float(r[8] or 0),
        'pos_trail_pct':  float(r[9] or 0),
        'pos_dca_pct':    float(r[10] or 0),
        'status':         r[11],
        'last_buy_price': float(r[14] or r[2] or 0),
        'wallet_id':      r[13],
    } for r in rows]

# ── Load wallet fresh ──────────────────────────────────────────────
def load_wallet(wallet_id):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, is_paper, current_balance, committed_usdt,
                   allocation_amount, exchange_id
            FROM virtual_wallets WHERE id=%s
        """, (wallet_id,))
        r = cur.fetchone()
    if not r:
        return None
    return {
        'id': r[0], 'is_paper': r[1],
        'current_balance': float(r[2] or 0),
        'committed_usdt':  float(r[3] or 0),
        'allocation_amount': float(r[4] or 0),
        'exchange_id': r[5],
    }

# ── Check if entry signal fires ────────────────────────────────────
def check_entry_signal(bot, coin, r):
    """
    Returns True if bot should open new position on coin.
    ASAP: always True
    Smart/Template: use entry_signals module
    """
    entry_method = bot.get('entry_method', 'dca_asap')

    if entry_method == 'dca_asap':
        return True

    if entry_method in ('dca_smart', 'dca_templates'):
        try:
            import entry_signals as es
            import indicators
            # For smart mode: dynamically use current champion's params.
            # Champion is loaded once per tick in _engine_loop() and
            # passed through via bot['_champion'] if available.
            # For templates: use the source research method from bot_params.
            bot_params = bot.get('bot_params', {})
            if isinstance(bot_params, str):
                import json as _j
                bot_params = _j.loads(bot_params)

            if entry_method == 'dca_smart' and bot.get('_champion'):
                # Use live champion's exact params + method family
                champ = bot['_champion']
                method = champ['method_family']
                params = champ['bot_params']
                print(f'🧠 Smart Mode: using champion {champ["bot_name"]} ({method}) for {coin}')
            else:
                method = bot_params.get('source_method') or bot['method']
                params = bot_params.get('research_params') or bot_params
            ohlcv = db.get_ohlcv(coin, 'mexc', limit=200)
            if not ohlcv:
                return False
            ohlcv_arrays = indicators.to_arrays(ohlcv)
            btc_ohlcv = db.get_ohlcv('BTC', 'mexc', limit=200)
            btc_data = indicators.to_arrays(btc_ohlcv) if btc_ohlcv else None
            signal = es.check_entry_signal(
                method, params, coin, 'mexc', btc_data, ohlcv_arrays
            )
            # signal returns True/False or a value — treat False/None as no signal
            return bool(signal)
        except Exception as e:
            print(f'⚠️ Entry signal error {coin}: {e}')
            return False

    return True  # Default: allow entry

# ── Coin classification params (Smart DCA v2 system) ──────────────
def load_coin_params_cache():
    """Load spacing/TP/trailing/tradeable per coin from coin_parameters.
    Same single source of truth used by research_engine.py — one
    calculation (calculate_coin_params.py), both systems read it."""
    cache = {}
    try:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT coin, dca_spacing, take_profit_pct, trailing_pct, tradeable, size_mult, calculation_version
                FROM coin_parameters
            """)
            for row in cur.fetchall():
                cache[row[0]] = {
                    'dca_spacing':   float(row[1]),
                    'take_profit':   float(row[2]),
                    'trailing':      float(row[3]),
                    'tradeable':     row[4] if row[4] is not None else True,
                    'size_mult':     float(row[5]) if row[5] is not None else None,
                    'calc_version':  row[6],
                }
    except Exception as e:
        print(f'⚠️ coin_params load error: {e}')
    return cache

# ── Get tradeable coins ────────────────────────────────────────────
def get_tradeable_coins(r, bot_params):
    """Returns list of coins this bot should consider."""
    coin_mode = bot_params.get('coin_mode', 'all') if isinstance(bot_params, dict) else 'all'

    if coin_mode == 'specific':
        coins = bot_params.get('specific_coins', [])
        if coins:
            return coins

    # All coins from Redis
    try:
        keys = r.keys('price:*:*/USDT')
        coins = [k.split(":")[-1].replace("/USDT", "") for k in keys]
        return [c for c in coins if c not in ('BTC', 'ETH', 'USDT')]
    except Exception:
        return []

# ── Check TP ──────────────────────────────────────────────────────
def check_tp(pos, current_price):
    """Returns True if TP should fire."""
    avg_cost = pos['avg_cost']
    if avg_cost <= 0:
        return False

    tp_pct   = pos['pos_tp_pct'] or 5.0
    trail_pct = pos['pos_trail_pct'] or 2.0
    tp_price = avg_cost * (1 + tp_pct / 100)
    direct_tp = (tp_pct - trail_pct) < 1.0

    # Arm TP
    if current_price >= tp_price and not pos['tp_armed']:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE positions
                SET tp_armed=TRUE, peak_price=%s
                WHERE id=%s
            """, (current_price, pos['id']))
        pos['tp_armed'] = True
        pos['peak_price'] = current_price
        print(f'🎯 TP armed: live pos {pos["id"]} {pos["coin"]} @ ${current_price}')
        if direct_tp:
            return True

    # Update peak
    if pos['tp_armed'] and current_price > pos['peak_price']:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE positions SET peak_price=%s WHERE id=%s",
                (current_price, pos['id']))
        pos['peak_price'] = current_price

    # Fire trailing
    if pos['tp_armed'] and pos['peak_price'] > 0:
        trail_price = pos['peak_price'] * (1 - trail_pct / 100)
        if current_price <= trail_price:
            if current_price <= avg_cost * 1.005:
                return False
            return True

    return False

# ── Execute TP sell ────────────────────────────────────────────────
def execute_tp_sell(pos, bot, current_price):
    """Execute TP sell via executor. ADDED June 20 2026: profit_coin
    support - if the position's snapshot says 'base_coin', sell only
    enough to recoup the original investment and leave the rest as
    real coin in the exchange wallet. Platform fee is still computed
    on the FULL theoretical profit (sold + kept), same 20% rule,
    deducted via the existing reserve_wallets mechanism either way -
    only the SELL QUANTITY changes, not how the fee itself works."""
    import system_gates
    if not system_gates.is_tp_trailing_allowed():
        return

    wallet = load_wallet(pos['wallet_id'])
    if not wallet:
        return

    executor = get_executor(wallet)
    full_quantity = pos['quantity']
    total_invested = pos['total_invested']

    # Theoretical full profit if everything sold at current_price -
    # this is always the fee basis, regardless of how much we actually sell
    full_value = full_quantity * current_price
    total_profit_theoretical = full_value - total_invested

    profit_coin = pos.get('profit_coin', 'USDT')
    keep_in_coin = (profit_coin == 'base_coin' and total_profit_theoretical > 0)

    if keep_in_coin:
        sell_quantity = min(full_quantity, total_invested / current_price)
    else:
        sell_quantity = full_quantity

    try:
        with db.get_db() as conn:
            result = executor.place_order(
                side='sell',
                coin=pos['coin'],
                usdt_amount=sell_quantity,
                wallet=wallet,
                conn=conn
            )

            if not result.success:
                print(f'⚠️ TP sell failed: {pos["coin"]} {result.error}')
                return

            # Calculate P&L on the portion actually sold
            gross_usdt = result.quantity * result.fill_price
            total_fees = result.fee_usdt
            net_usdt   = gross_usdt - total_fees
            pnl_usdt   = net_usdt - total_invested
            pnl_pct    = (pnl_usdt / total_invested * 100) if total_invested > 0 else 0

            kept_quantity = max(0, full_quantity - result.quantity)
            kept_value_usdt = kept_quantity * current_price

            # FIXED June 23 2026: was UPDATE live_dca_positions, the
            # stale table found during the DCA bug investigation -
            # the real position lives in positions, the same fix
            # applied to load_open_positions() above. fill_fee_usdt,
            # exchange_order_id, kept_coin_quantity, and
            # kept_coin_value_usdt were added to positions
            # specifically to preserve this fee/profit_coin tracking
            # rather than dropping it.
            cur = conn.cursor()
            cur.execute("""
                UPDATE positions
                SET status='closed',
                    closed_at=NOW(),
                    close_reason='tp',
                    total_sold_usdt=%s,
                    realized_pnl_usdt=%s,
                    realized_pnl_pct=%s,
                    fill_fee_usdt=fill_fee_usdt + %s,
                    exchange_order_id=%s,
                    kept_coin_quantity=%s,
                    kept_coin_value_usdt=%s
                WHERE id=%s
            """, (net_usdt, pnl_usdt, pnl_pct,
                  result.fee_usdt, result.order_id,
                  kept_quantity, kept_value_usdt, pos['id']))

            # Log wallet transaction
            cur.execute("""
                INSERT INTO wallet_transactions
                    (wallet_id, position_id, type, amount,
                     balance_before, balance_after, reference_type, note)
                VALUES (%s, %s, 'credit', %s, %s, %s, 'live_dca', %s)
            """, (wallet['id'], pos['id'], net_usdt,
                  wallet['current_balance'],
                  wallet['current_balance'] + net_usdt,
                  f'TP close {pos["coin"]} pnl={pnl_pct:.2f}%'))

            conn.commit()

            emoji = '💚' if pnl_usdt > 0 else '❤️'
            print(f'{emoji} TP CLOSE: {bot["name"]} {pos["coin"]} '
                  f'@ ${result.fill_price:.6f} '
                  f'pnl={pnl_pct:.2f}% (${pnl_usdt:.4f})')

            # Deduct performance fee on profit. FIXED June 19 2026:
            # now respects is_zero_fee and fee_override (per-user rate
            # customization, e.g. family discount) - columns existed
            # on users table but were never read anywhere before today.
            # Fee basis: full theoretical profit (sold + kept) when
            # keeping profit in coin, otherwise the realized pnl_usdt
            # (which equals the full profit anyway when nothing was kept)
            fee_basis = total_profit_theoretical if keep_in_coin else pnl_usdt
            if fee_basis > 0:
                try:
                    _fee_query = ("SELECT is_research_account, is_admin, "
                                  "is_zero_fee, fee_override FROM users WHERE id=%s")
                    with db.get_db() as _fc:
                        _cur = _fc.cursor()
                        _cur.execute(_fee_query, (bot['user_id'],))
                        _urow = _cur.fetchone()
                    _skip_fee = _urow and (_urow[0] or _urow[1] or _urow[2])
                    if not _skip_fee:
                        _fee_pct = float(_urow[3]) if _urow and _urow[3] is not None else 20.0
                        fee = fee_basis * (_fee_pct / 100)
                        db.deduct_performance_fee(bot['user_id'], pos['id'], fee, fee_basis)
                except Exception as e:
                    print(f'⚠️ Fee deduction error: {e}')

    except Exception as e:
        print(f'⚠️ TP sell error {pos["coin"]}: {e}')

# ── Execute DCA buy ────────────────────────────────────────────────
def execute_dca_buy(pos, bot, amount_usdt, r):
    """Execute DCA buy via executor."""
    import system_gates
    if not system_gates.is_dca_continuation_allowed():
        return False

    wallet = load_wallet(pos['wallet_id'])
    if not wallet:
        return False

    # Exchange minimum check (ADDED June 21 2026) - Long never does a
    # partial buy, so if this amount is below the real minimum, skip
    # entirely rather than create a dust order. Fast DB read, refreshed
    # daily by refresh_min_orders.py, never a slow live API call.
    min_req = db.get_min_order(wallet['exchange_id'], pos['coin'])
    if min_req and amount_usdt < min_req.get('min_cost', 0):
        print(f"DCA buy skipped: {pos['coin']} amount {amount_usdt} below exchange minimum {min_req.get('min_cost')}")
        return False

    executor = get_executor(wallet)

    try:
        with db.get_db() as conn:
            result = executor.place_order(
                side='buy',
                coin=pos['coin'],
                usdt_amount=amount_usdt,
                wallet=wallet,
                conn=conn
            )

            if not result.success:
                if result.error == 'insufficient_funds':
                    return False
                print(f'⚠️ DCA buy failed: {pos["coin"]} {result.error}')
                return False

            # Recalculate avg_cost
            old_value = pos['avg_cost'] * pos['quantity']
            new_value  = result.fill_price * result.quantity
            new_qty    = pos['quantity'] + result.quantity
            new_avg    = (old_value + new_value) / new_qty if new_qty > 0 else result.fill_price

            # FIXED June 23 2026: was UPDATE live_dca_positions, the
            # stale table found during the DCA bug investigation -
            # same fix as load_open_positions() and the TP-close
            # update above. total_fees_usdt, price_age_ms, and
            # last_dca_at added to positions to preserve this
            # tracking rather than dropping it.
            cur = conn.cursor()
            cur.execute("""
                UPDATE positions
                SET avg_cost=%s,
                    quantity=%s,
                    total_invested=total_invested + %s,
                    total_fees_usdt=total_fees_usdt + %s,
                    last_buy_price=%s,
                    dca_count=dca_count + 1,
                    last_dca_at=NOW(),
                    fill_fee_usdt=%s,
                    exchange_order_id=%s,
                    price_age_ms=%s,
                    tp_armed=FALSE,
                    peak_price=0
                WHERE id=%s
            """, (new_avg, new_qty, amount_usdt, result.fee_usdt,
                  result.fill_price, result.fee_usdt,
                  result.order_id, result.price_age_ms, pos['id']))

            # Log wallet transaction
            cur.execute("""
                INSERT INTO wallet_transactions
                    (wallet_id, position_id, type, amount,
                     balance_before, balance_after, reference_type, note)
                VALUES (%s, %s, 'debit', %s, %s, %s, 'live_dca', %s)
            """, (wallet['id'], pos['id'], amount_usdt,
                  wallet['current_balance'],
                  wallet['current_balance'] - amount_usdt,
                  f'DCA #{pos["dca_count"]+1} {pos["coin"]}'))

            conn.commit()
            print(f'📈 DCA BUY: {bot["name"]} {pos["coin"]} '
                  f'${amount_usdt:.2f} @ ${result.fill_price:.6f} '
                  f'avg=${new_avg:.6f} dca#{pos["dca_count"]+1}')
            return True

    except Exception as e:
        print(f'⚠️ DCA buy error {pos["coin"]}: {e}')
        return False

# ── Open new position ──────────────────────────────────────────────
def open_position(bot, coin, r, coin_params_cache=None):
    """Open a new long DCA position."""
    import system_gates
    if not system_gates.is_new_trade_allowed(
        'long', entry_method=bot.get('entry_method'),
        exchange_name=bot.get('exchange_name'),
        is_research=bot.get('is_research', False),
        user_id=bot.get('user_id'),
        is_paper=bot.get('is_paper', False)
    ):
        return False

    cp_for_coin = (coin_params_cache or {}).get(coin, {})
    wallet = load_wallet(bot['wallet_id'])
    if not wallet:
        return False

    base_order = bot['base_order']
    if wallet['current_balance'] < base_order:
        return False

    min_req = db.get_min_order(wallet['exchange_id'], coin)
    if min_req and base_order < min_req.get('min_cost', 0):
        print(f"Open position skipped: {coin} base_order {base_order} below exchange minimum {min_req.get('min_cost')}")
        return False

    executor = get_executor(wallet)

    try:
        with db.get_db() as conn:
            result = executor.place_order(
                side='buy',
                coin=coin,
                usdt_amount=base_order,
                wallet=wallet,
                conn=conn
            )

            if not result.success:
                if result.error == 'insufficient_funds':
                    return False
                print(f'⚠️ Open failed: {coin} {result.error}')
                return False

            # Get BTC context
            btc_price = None
            btc_regime = None
            btc_24h = None
            btc_dominance = None
            btc_sma50 = None
            market_age = db.get_market_age_days(coin)
            try:
                import json as _j
                btc_cached = r.get('btc:regime_data')
                if btc_cached:
                    btc_data = _j.loads(btc_cached)
                    btc_price     = btc_data.get('btc_price')
                    btc_regime    = btc_data.get('btc_regime', 'unknown')
                    btc_24h       = btc_data.get('btc_24h_change')
                    btc_dominance = btc_data.get('btc_dominance')
                    btc_sma50     = btc_data.get('btc_sma50')
                else:
                    btc_price = get_redis_price(r, 'BTC')
            except Exception:
                pass

            # Coin trade number
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM positions
                WHERE bot_id=%s AND coin=%s
            """, (bot['id'], coin))
            coin_trade_num = cur.fetchone()[0] + 1

            # Insert position
            cur.execute("""
                INSERT INTO positions (
                    bot_id, user_id, exchange_id, wallet_id,
                    coin, direction, status,
                    avg_cost, quantity, total_invested,
                    last_buy_price, dca_count,
                    total_fees_usdt, fill_fee_usdt,
                    execution_type, fill_price, exchange_order_id,
                    price_age_ms,
                    entry_method, entry_method_at_open,
                    btc_price_at_entry, btc_regime,
                    btc_24h_change_pct, btc_dominance, btc_sma50_at_entry,
                    market_age_days,
                    pos_tp_pct, pos_trail_pct, pos_dca_pct,
                    size_mult_at_open, calculation_version,
                    coin_trade_number, opened_at, profit_coin
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, 'long', 'open',
                    %s, %s, %s,
                    %s, 0,
                    %s, %s,
                    %s, %s, %s,
                    %s,
                    %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, NOW(), %s
                ) RETURNING id
            """, (
                bot['id'], bot['user_id'], bot['exchange_id'], bot['wallet_id'],
                coin,
                result.fill_price, result.quantity, base_order,
                result.fill_price,
                result.fee_usdt, result.fee_usdt,
                'paper' if wallet['is_paper'] else 'live',
                result.fill_price, result.order_id,
                result.price_age_ms,
                bot['entry_method'], bot['entry_method'],
                btc_price, btc_regime,
                btc_24h, btc_dominance, btc_sma50,
                market_age,
                cp_for_coin.get('take_profit', bot['tp_percent']),
                cp_for_coin.get('trailing', bot['trailing_percent']),
                cp_for_coin.get('dca_spacing', bot['dca_percent']),
                cp_for_coin.get('size_mult'),
                cp_for_coin.get('calc_version'),
                coin_trade_num, bot.get('profit_coin', 'USDT')
            ))
            pos_id = cur.fetchone()[0]

            # Log wallet transaction
            cur.execute("""
                INSERT INTO wallet_transactions
                    (wallet_id, position_id, type, amount,
                     balance_before, balance_after, reference_type, note)
                VALUES (%s, %s, 'debit', %s, %s, %s, 'live_dca', %s)
            """, (wallet['id'], pos_id, base_order,
                  wallet['current_balance'],
                  wallet['current_balance'] - base_order,
                  f'Open {coin} position'))

            conn.commit()
            print(f'🟢 OPEN: {bot["name"]} {coin} '
                  f'${base_order:.2f} @ ${result.fill_price:.6f}')
            return True

    except Exception as e:
        print(f'⚠️ Open position error {coin}: {e}')
        return False

# ── DCA queue logic ────────────────────────────────────────────────
def needs_dca(pos, current_price, base_order=10.0, size_mult=1.5):
    """Returns (True, dca_amount) if position needs DCA."""
    if pos['avg_cost'] <= 0 or pos['last_buy_price'] <= 0:
        return False, 0

    dca_pct = pos['pos_dca_pct'] or 7.0
    last_buy = pos['last_buy_price'] if pos['dca_count'] > 0 else pos['avg_cost']
    drop_pct = (last_buy - current_price) / last_buy * 100

    if drop_pct >= dca_pct:
        # DCA amount = base_order × size_multiplier^(dca_count+1)
        next_dca_num = pos['dca_count'] + 1
        dca_amount = base_order * (size_mult ** next_dca_num)
        dca_amount = max(dca_amount, 5.0)
        return True, round(dca_amount, 2)

    return False, 0

def score_position(pos, current_price, dca_amount=10.0):
    """Score: loss% / required_usdt — higher loss per dollar = higher priority."""
    if pos['avg_cost'] <= 0 or dca_amount <= 0:
        return 0
    loss_pct = (pos['avg_cost'] - current_price) / pos['avg_cost'] * 100
    return loss_pct / dca_amount

# ── Per-user DCA cycle ─────────────────────────────────────────────
def run_user_cycle(user_id, user_bots, r):
    """Run DCA queue for one user."""
    for bot in user_bots:
        try:
            run_bot_cycle(bot, r)
        except Exception as e:
            print(f'⚠️ Bot cycle error {bot["name"]}: {e}')

def run_bot_cycle(bot, r):
    """Run one bot's DCA cycle."""
    open_positions = load_open_positions(bot['id'])
    open_coins = {}
    for pos in open_positions:
        open_coins[pos['coin']] = open_coins.get(pos['coin'], 0) + 1

    coin_params_cache = load_coin_params_cache()

    # ── Check DCA queue ──
    if bot['dca_on'] and open_positions:
        # Score all positions needing DCA
        candidates = []
        for pos in open_positions:
            current_price = get_redis_price(r, pos['coin'])
            if not current_price:
                continue
            needs, amount = needs_dca(pos, current_price, bot['base_order'], bot['size_multiplier'])
            if needs:
                score = score_position(pos, current_price, amount)
                candidates.append((score, pos, amount, current_price))

        # Sort by priority (highest loss first)
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Try candidates in priority order, skip unaffordable ones,
        # execute the first one that's actually fundable. Per LOCKED
        # spec (13_LOCKED_DECISIONS.md "Smart Queue Insufficient Funds
        # Behavior"): never idle when something can be funded.
        # FIXED June 18 2026 - previously only tried candidates[0] and
        # gave up entirely if unaffordable, even when a cheaper #2/#3
        # candidate sat right there fully fundable. Real capital could
        # sit idle for this reason.
        # FIXED June 23 2026: was stopping after the FIRST successful
        # buy (break), even when the wallet had plenty left to fund
        # several more. With many open positions and small DCA
        # amounts, the single highest-priority candidate was always
        # affordable, so it always won and lower-priority candidates
        # could be starved indefinitely. Now processes every
        # affordable candidate in the same cycle, not just one.
        #
        # ALSO FIXED June 23 2026, the real root cause of a live,
        # confirmed-stuck position (bot 745, coin XT, dca_count never
        # advancing past 8 despite needs_dca()=True every cycle for
        # an extended period): load_wallet(pos['wallet_id']) silently
        # returned None because positions.wallet_id was NULL on this
        # row (and 264,116 others platform-wide, a historical data
        # issue, not an active bug in current INSERT statements which
        # already set wallet_id correctly). Backfilled every affected
        # row from its own bot's wallet_id. Found via direct,
        # methodical debug logging rather than guessing - confirmed
        # the exact silent failure point before touching any data.
        funded_count = 0
        for score, pos, amount, price in candidates:
            wallet = load_wallet(pos['wallet_id'])
            if wallet and wallet['current_balance'] >= amount:
                execute_dca_buy(pos, bot, amount, r)
                funded_count += 1
            else:
                try:
                    key = f'insuf:{bot["id"]}:{pos["id"]}'
                    count = int(r.get(key) or 0) + 1
                    r.setex(key, 3600, count)
                except Exception:
                    pass

        if funded_count == 0 and candidates:
            print(f'⚠️ {bot["name"]}: no affordable DCA candidate this '
                  f'cycle out of {len(candidates)} needing DCA')

    # Reserve floor state machine (ADDED June 20 2026, shared logic
    # in database.py - used identically by Scalper engine too)
    floor_paused = db.check_and_update_floor_state(
        bot['id'], bot['name'], bot['wallet']['current_balance'],
        bot.get('reserve_floor'), bot.get('resume_threshold'),
        bot.get('auto_resume', True), bot.get('floor_paused', False)
    )

    # Account-level reserve debt check (ADDED June 20 2026) - separate
    # mechanism from the bot-level floor above. Each user independent.
    account_in_debt = db.is_reserve_in_debt(bot['user_id'])

    # Cross-system fund isolation (ADDED June 21 2026) - if a Short
    # bot on this SAME wallet has a sell pending its buyback limit
    # placement, Long must hold off opening new positions here. Short
    # buyback funding has priority per locked spec.
    wallet_pending_buyback = db.is_wallet_pending_buyback(bot['wallet_id'])

    # ── Open new positions ──
    # ASAP-entry bots are now handled reactively in the tick callback
    # (ADDED June 20 2026, zero-delay) - skip here to avoid a
    # double-open race between this periodic pass and the tick
    # handler. Template/smart entry still needs this periodic pass,
    # since their entry SIGNAL evaluation is intentionally periodic.
    if bot['trading_on'] and not floor_paused and not account_in_debt \
            and not wallet_pending_buyback \
            and bot.get('entry_method') != 'dca_asap' \
            and len(open_positions) < bot['trades_per_bot']:
        coins = get_tradeable_coins(r, bot.get('bot_params', {}))
        for coin in coins:
            # Check per-coin limit
            if open_coins.get(coin, 0) >= bot['trades_per_coin']:
                continue
            # Check ST flag - skip suspended coins
            if is_st_coin(coin, bot.get('exchange_name', 'mexc'), r):
                continue
            # Check coin classification eligibility (stablecoins,
            # new coins under 30 days, frozen-anomaly coins)
            cp_check = coin_params_cache.get(coin, {})
            if cp_check and cp_check.get('tradeable') is False:
                continue
            # Check entry signal
            if not check_entry_signal(bot, coin, r):
                continue
            # Open position
            if open_position(bot, coin, r, coin_params_cache):
                open_positions = load_open_positions(bot['id'])
                open_coins[coin] = open_coins.get(coin, 0) + 1
                if len(open_positions) >= bot['trades_per_bot']:
                    break

# ── WebSocket TP callback ──────────────────────────────────────────
# In-memory cache for open live positions (refreshed every 30s)
_tp_cache = {}
_tp_cache_time = 0
_tp_cache_lock = threading.Lock()

def refresh_tp_cache():
    global _tp_cache, _tp_cache_time
    with db.get_db() as conn:
        cur = conn.cursor()
        # FIXED June 23 2026: was FROM live_dca_positions, the stale
        # table found during the DCA bug investigation - same fix as
        # everywhere else in this file. Added direction filter since
        # positions holds both long and short, unlike the old table.
        cur.execute("""
            SELECT p.id, p.bot_id, p.coin, p.avg_cost, p.quantity,
                   p.total_invested, p.dca_count, p.tp_armed,
                   p.peak_price, p.pos_tp_pct, p.pos_trail_pct,
                   p.wallet_id, b.user_id, b.name, p.profit_coin
            FROM positions p
            JOIN bots b ON p.bot_id = b.id
            WHERE p.status='open' AND p.direction='long'
        """)
        rows = cur.fetchall()

    new_cache = {}
    for r in rows:
        coin = r[2]
        pos = {
            'id': r[0], 'bot_id': r[1], 'coin': coin,
            'avg_cost': float(r[3] or 0),
            'quantity': float(r[4] or 0),
            'total_invested': float(r[5] or 0),
            'dca_count': r[6],
            'tp_armed': r[7],
            'peak_price': float(r[8] or 0),
            'pos_tp_pct': float(r[9] or 5),
            'pos_trail_pct': float(r[10] or 2),
            'wallet_id': r[11],
            'user_id': r[12],
            'bot_name': r[13],
            'last_buy_price': float(r[3] or 0),  # use avg_cost as fallback
            'profit_coin': r[14] or 'USDT',
        }
        if coin not in new_cache:
            new_cache[coin] = []
        new_cache[coin].append(pos)

    with _tp_cache_lock:
        _tp_cache = new_cache
        _tp_cache_time = time.time()

# In-memory cache of ASAP-entry bots (ADDED June 20 2026, per
# explicit instruction: zero-delay entry opening, not just TP). Only
# the BOT LIST and the coin_parameters table snapshot are cached
# (config/classification don't change tick-by-tick) - every actual
# eligibility DECISION (ST flag, per-coin count) still runs LIVE on
# every tick, since those are cheap (a Redis read, a quick count) and
# not safe to cache without risking a stale decision.
_asap_bots_cache = []
_asap_bots_cache_time = 0
_asap_bots_lock = threading.Lock()
_coin_params_cache_local = {}
_coin_params_cache_local_time = 0

def refresh_asap_bots_cache():
    global _asap_bots_cache, _asap_bots_cache_time
    global _coin_params_cache_local, _coin_params_cache_local_time
    bots = load_live_long_bots()
    asap_bots = [b for b in bots if b.get('entry_method') == 'dca_asap' and b['trading_on']]
    with _asap_bots_lock:
        _asap_bots_cache = asap_bots
        _asap_bots_cache_time = time.time()
    # load_coin_params_cache() queries the FULL coin_parameters table
    # every call - cached locally here, NOT called fresh on every
    # tick, or it would hammer the DB dozens of times per second
    _coin_params_cache_local = load_coin_params_cache()
    _coin_params_cache_local_time = time.time()

def _coin_in_bot_scope(coin, bot_params):
    """Cheap, instant scope check - no DB/Redis call, mirrors
    get_tradeable_coins()'s filter logic exactly."""
    if not isinstance(bot_params, dict):
        return coin not in ('BTC', 'ETH', 'USDT')
    if bot_params.get('coin_mode') == 'specific':
        return coin in bot_params.get('specific_coins', [])
    return coin not in ('BTC', 'ETH', 'USDT')

def make_live_tp_callback():
    """Returns WebSocket price callback for live long DCA TP checking,
    ALSO now handles zero-delay ASAP entry opening on the same tick."""
    def on_price_update(coin, price):
        try:
            # Refresh cache every 30s
            if time.time() - _tp_cache_time > 30:
                refresh_tp_cache()
            if time.time() - _asap_bots_cache_time > 60:
                refresh_asap_bots_cache()

            # ASAP entry: bot list + classification snapshot are
            # cached above; everything else here is checked LIVE
            with _asap_bots_lock:
                asap_bots = list(_asap_bots_cache)
            for bot in asap_bots:
                try:
                    if not _coin_in_bot_scope(coin, bot.get('bot_params', {})):
                        continue
                    open_positions = load_open_positions(bot['id'])
                    open_coins_count = sum(1 for p in open_positions if p['coin'] == coin)
                    if open_coins_count >= bot['trades_per_coin']:
                        continue
                    if len(open_positions) >= bot['trades_per_bot']:
                        continue
                    if db.is_wallet_pending_buyback(bot['wallet_id']):
                        continue
                    if is_st_coin(coin, bot.get('exchange_name', 'mexc'), get_redis()):
                        continue
                    cp_check = _coin_params_cache_local.get(coin, {})
                    if cp_check and cp_check.get('tradeable') is False:
                        continue
                    open_position(bot, coin, get_redis())
                except Exception:
                    pass

            with _tp_cache_lock:
                positions = list(_tp_cache.get(coin, []))

            if not positions:
                return

            # Remove closed from cache
            with _tp_cache_lock:
                if coin in _tp_cache:
                    _tp_cache[coin] = [
                        p for p in _tp_cache[coin] if p['avg_cost'] > 0
                    ]

            for pos in positions:
                if check_tp(pos, price):
                    # Load bot info
                    bot = {'user_id': pos['user_id'], 'name': pos['bot_name']}
                    execute_tp_sell(pos, bot, price)
                    # Remove from cache
                    with _tp_cache_lock:
                        if coin in _tp_cache:
                            _tp_cache[coin] = [
                                p for p in _tp_cache[coin]
                                if p['id'] != pos['id']
                            ]

        except Exception as e:
            pass  # Never crash WebSocket thread

    return on_price_update

# ── Main engine loop ───────────────────────────────────────────────
_running = False
_cycle_thread = None

def is_engine_alive():
    """Watchdog check: is the live DCA thread actually running right now?"""
    global _cycle_thread
    return _running and _cycle_thread is not None and _cycle_thread.is_alive()

def start_engine():
    """Start the live long DCA engine.
    NOT a daemon thread: daemon threads die silently with zero warning
    if the main process restarts/reloads internally — this caused a
    16.5 hour silent outage on June 16 2026. Non-daemon means a crash
    is visible, and the watchdog in research_engine.py can detect and
    restart it automatically within ~60s instead."""
    global _running, _cycle_thread
    if is_engine_alive():
        return
    _running = True
    _cycle_thread = threading.Thread(target=_engine_loop, daemon=False)
    _cycle_thread.start()
    print('✅ LiveLongDCA engine started')

def load_dca_champion():
    """Fetch current DCA bear/bull/sideways champions from champion_history.
    Returns {regime: {bot_name, bot_params, method_family}} or {}.
    Called ONCE per engine tick, cached in memory for that cycle only —
    never mid-cycle, to avoid fracturing batch-arming/TP state."""
    try:
        import redis as _redis_mod
        r_cache = _redis_mod.Redis(host='localhost', port=6379, decode_responses=True)
        btc_data = r_cache.get('btc:regime_data')
        current_regime = 'bear'  # safe default
        if btc_data:
            import json as _j
            current_regime = _j.loads(btc_data).get('btc_regime', 'bear')

        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT ch.regime, ch.method_id, b.bot_params, b.method
                FROM champion_history ch
                LEFT JOIN bots b ON b.name = ch.method_id
                WHERE ch.is_active_champion=TRUE AND ch.system_type='DCA'
            """)
            champions = {}
            for regime, bot_name, bot_params, method in cur.fetchall():
                champions[regime] = {
                    'bot_name': bot_name,
                    'bot_params': bot_params or {},
                    'method_family': method or bot_name,
                }
        return champions, current_regime
    except Exception as e:
        print(f'⚠️ Champion lookup failed: {e}')
        return {}, 'bear'

def _engine_loop():
    """Main 60s DCA cycle loop."""
    r = get_redis()
    while _running:
        try:
            cycle_start = time.time()
            # Heartbeat (ADDED June 21 2026) - written from WITHIN this
            # process so the api.py process (a SEPARATE process) can
            # read real engine-alive status via Redis instead of trying
            # to import this module directly, which would only ever see
            # its OWN never-started copy of these globals.
            try:
                r.setex('engine:long_dca:heartbeat', 150, str(time.time()))
            except Exception:
                pass
            print(f'\n--- LiveLongDCA Cycle {datetime.now(timezone.utc)} ---')

            # Load champion ONCE per tick before any bot processing
            # (never mid-cycle — all bots in this tick use same champion)
            _champions, _current_regime = load_dca_champion()
            if _champions:
                champ = _champions.get(_current_regime)
                if champ:
                    print(f'👑 DCA Champion ({_current_regime}): {champ["bot_name"]}')

            # Load all active bots
            bots = load_live_long_bots()
            if not bots:
                print('No active live long bots')
            else:
                # Inject current champion into smart-mode bots
                # Done here (once per tick, before grouping) so all
                # bots in this cycle use the same champion consistently
                for bot in bots:
                    if bot.get('entry_method') == 'dca_smart':
                        champ = _champions.get(_current_regime)
                        bot['_champion'] = champ  # None if no champion yet
                        bot['_regime'] = _current_regime

                # Group by user
                users = {}
                for bot in bots:
                    uid = bot['user_id']
                    if uid not in users:
                        users[uid] = []
                    users[uid].append(bot)

                # Run per-user cycle
                for user_id, user_bots in users.items():
                    run_user_cycle(user_id, user_bots, r)

            elapsed = time.time() - cycle_start
            sleep_time = max(0, 60 - elapsed)
            time.sleep(sleep_time)

        except Exception as e:
            print(f'⚠️ Engine loop error: {e}')
            time.sleep(10)

def stop_engine():
    global _running
    _running = False
    print('🛑 LiveLongDCA engine stopped')

# ── Called from websocket_prices.py ───────────────────────────────
_live_tp_callback = None

def get_live_tp_callback():
    global _live_tp_callback
    if _live_tp_callback is None:
        _live_tp_callback = make_live_tp_callback()
        refresh_tp_cache()
    return _live_tp_callback

