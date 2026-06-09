import os
import time
import ccxt
import redis
from datetime import datetime, timezone
from dotenv import load_dotenv
import database as db
import entry_signals as es
_ohlcv_cache = {}
import telegram as tg

load_dotenv()

PAPER_MODE = os.getenv('PAPER_MODE', 'true').lower() == 'true'
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# ═══════════════════════════════
# REDIS CLIENT
# ═══════════════════════════════
def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# ═══════════════════════════════
# TELEGRAM
# ═══════════════════════════════
# Telegram handled by telegram.py module

# ═══════════════════════════════
# EXCHANGE INITIALIZATION
# ═══════════════════════════════
def init_exchange(exchange_row):
    from exchanges import init_exchange as _init
    return _init(exchange_row)

# ═══════════════════════════════
# PRICE FETCHING
# ═══════════════════════════════
def fetch_and_cache_prices(exchange_obj, exchange_name, r):
    try:
        tickers = exchange_obj.fetch_tickers()
        for symbol, ticker in tickers.items():
            if ticker.get('last'):
                r.setex(
                    f'price:{exchange_name}:{symbol}',
                    120,
                    str(ticker['last'])
                )
        print(f'✅ Prices cached: {len(tickers)} pairs on {exchange_name}')
        return tickers
    except Exception as e:
        print(f'❌ Price fetch error {exchange_name}: {e}')
        db.record_bot_event(None, None, 'price_fetch_error',
                           exchange=exchange_name,
                           error_message=str(e))
        return {}

def get_price(coin, exchange_name, r, tickers):
    # Try Redis first
    cached = r.get(f'price:{exchange_name}:{coin}/USDT')
    if cached:
        return float(cached)
    # Try from tickers
    symbol = f'{coin}/USDT'
    if symbol in tickers and tickers[symbol].get('last'):
        return float(tickers[symbol]['last'])
    return None

# ═══════════════════════════════
# ST FLAG CHECK
# ═══════════════════════════════
def check_st_flag(coin, exchange_name, tickers, r):
    symbol = f'{coin}/USDT'
    # Check Redis cache first
    cached = r.get(f'st:{exchange_name}:{coin}')
    if cached:
        return cached == 'true'

    # Check from tickers
    if symbol in tickers:
        ticker = tickers[symbol]
        # Different exchanges use different fields
        if ticker.get('info', {}).get('status') in ['ST', 'SUSPENDED']:
            r.setex(f'st:{exchange_name}:{coin}', 3600, 'true')
            return True

    r.setex(f'st:{exchange_name}:{coin}', 3600, 'false')
    return False

# ═══════════════════════════════
# SMART QUEUE SCORING
# ═══════════════════════════════
def calculate_score(position, current_price, bot):
    # get_queue_candidates columns:
    # [0]id [1]coin [2]total_invested [3]last_buy_price
    # [4]avg_cost [5]dca_count [6]category [7]bot_id
    # [8]user_id [9]dca_percent [10]spacing_mult
    # [11]size_mult [12]base_order [13]dca_on
    avg_cost      = float(position[4] or 0)
    total_invested = float(position[2] or 0)
    dca_count     = int(position[5] or 0)
    last_buy_price = float(position[3] or avg_cost)
    dca_percent   = float(bot[10] or 7.0)
    spacing_mult  = float(bot[11] or 1.4)
    size_mult     = float(bot[12] or 1.5)
    base_order    = float(bot[15] or 100.0)

    if avg_cost == 0 or current_price == 0:
        return 0

    # Loss percentage from avg_cost
    loss_pct = ((avg_cost - current_price) / avg_cost) * 100
    if loss_pct <= 0:
        return 0  # Not in loss · not eligible

    # Next DCA trigger price
    effective_spacing = dca_percent * (spacing_mult ** dca_count)
    next_dca_price = last_buy_price * (1 - effective_spacing / 100)

    # Next DCA amount (dca_count+1 because this is the NEXT dca)
    next_dca_amount = base_order * (size_mult ** (dca_count + 1))

    if next_dca_amount == 0:
        return 0

    # Score = Loss% / USDT required
    score = loss_pct / next_dca_amount

    return score, next_dca_price, next_dca_amount

# ═══════════════════════════════
# EXECUTE TRADE
# ═══════════════════════════════
def execute_buy(exchange_obj, coin, amount_usdt,
                position_id, bot_id, user_id, exchange_id,
                dca_level, reason, r):
    symbol = f'{coin}/USDT'

    if PAPER_MODE:
        # Paper trade - search any exchange cache
        price = get_price(coin, '', r, {})
        if not price:
            keys = r.keys(f'price:*:{coin}/USDT')
            if keys:
                price = float(r.get(keys[0]))
        if not price:
            print(f'No price for {coin} · skipping paper trade')
            return None

        quantity = amount_usdt / price
        trade_id = db.record_trade(
            position_id, bot_id, user_id, exchange_id,
            coin, 'buy', price, quantity, amount_usdt,
            0, 'USDT', reason, 'market', f'paper_{int(time.time())}',
            True, dca_level
        )
        print(f'📄 Paper buy: {coin} ${amount_usdt:.2f} @ ${price:.6f}')
        return {'price': price, 'quantity': quantity,
                'trade_id': trade_id}
    else:
        # Live trade
        try:
            order = exchange_obj.create_market_buy_order(
                symbol, None,
                params={'quoteOrderQty': amount_usdt}
            )
            price = float(order.get('average') or
                         order.get('price') or 0)
            quantity = float(order.get('filled') or 0)
            fee = float(order.get('fee', {}).get('cost') or 0)
            fee_currency = order.get('fee', {}).get('currency', 'USDT')
            order_id = order.get('id', '')

            trade_id = db.record_trade(
                position_id, bot_id, user_id, exchange_id,
                coin, 'buy', price, quantity, amount_usdt,
                fee, fee_currency, reason, 'market',
                order_id, False, dca_level
            )
            print(f'✅ Live buy: {coin} ${amount_usdt:.2f} @ ${price:.6f}')
            return {'price': price, 'quantity': quantity,
                    'fee': fee, 'trade_id': trade_id}

        except ccxt.AuthenticationError as e:
            db.pause_exchange(exchange_id, 'API key invalid', 'auth_error')
            send_admin(f'🔴 Exchange paused: API key invalid\nExchange ID: {exchange_id}')
            db.record_bot_event(bot_id, user_id, 'api_auth_error',
                               coin=coin, error_message=str(e))
            return None

        except ccxt.InsufficientFunds:
            print(f'Insufficient funds for {coin}')
            return None

        except Exception as e:
            print(f'Buy error {coin}: {e}')
            db.record_bot_event(bot_id, user_id, 'buy_error',
                               coin=coin, error_message=str(e))
            return None

def execute_sell(exchange_obj, coin, quantity,
                 position_id, bot_id, user_id, exchange_id,
                 reason, r):
    symbol = f'{coin}/USDT'

    if PAPER_MODE:
        price = get_price(coin, '', r, {})
        if not price:
            keys = r.keys(f'price:*:{coin}/USDT')
            if keys:
                price = float(r.get(keys[0]))
        if not price:
            return None

        usdt_received = quantity * price
        trade_id = db.record_trade(
            position_id, bot_id, user_id, exchange_id,
            coin, 'sell', price, quantity, usdt_received,
            0, 'USDT', reason, 'market',
            f'paper_{int(time.time())}', True, 0
        )
        print(f'📄 Paper sell: {coin} {quantity:.4f} @ ${price:.6f}')
        return {'price': price, 'usdt_received': usdt_received,
                'trade_id': trade_id}
    else:
        try:
            order = exchange_obj.create_market_sell_order(
                symbol, quantity
            )
            price = float(order.get('average') or
                         order.get('price') or 0)
            usdt_received = float(order.get('cost') or
                                   price * quantity)
            fee = float(order.get('fee', {}).get('cost') or 0)
            fee_currency = order.get('fee', {}).get('currency', 'USDT')
            order_id = order.get('id', '')

            trade_id = db.record_trade(
                position_id, bot_id, user_id, exchange_id,
                coin, 'sell', price, quantity, usdt_received,
                fee, fee_currency, reason, 'market',
                order_id, False, 0
            )
            print(f'✅ Live sell: {coin} {quantity:.4f} @ ${price:.6f}')
            return {'price': price, 'usdt_received': usdt_received,
                    'fee': fee, 'trade_id': trade_id}

        except Exception as e:
            print(f'Sell error {coin}: {e}')
            db.record_bot_event(bot_id, user_id, 'sell_error',
                               coin=coin, error_message=str(e))
            return None

# ═══════════════════════════════
# TP CHECK
# ═══════════════════════════════
def check_tp(position, current_price, bot):
    position_id = position[0]
    avg_cost = float(position[7] or 0)
    quantity = float(position[8] or 0)
    tp_armed = position[12]
    peak_price = float(position[13] or 0)
    tp_percent = float(bot[13] or 5.0)
    trailing_percent = float(bot[14] or 2.0)

    if avg_cost == 0:
        return False

    tp_price = avg_cost * (1 + tp_percent / 100)

    # Arm TP when price reaches target
    if current_price >= tp_price and not tp_armed:
        db.arm_tp(position_id, current_price)
        print(f'🎯 TP armed: position {position_id} @ ${current_price:.6f}')
        return False

    # Update peak price
    if tp_armed and current_price > peak_price:
        db.update_peak_price(position_id, current_price)
        return False

    # Fire TP when price drops from peak
    if tp_armed and peak_price > 0:
        trail_price = peak_price * (1 - trailing_percent / 100)
        if current_price <= trail_price:
            print(f'🚀 TP firing: position {position_id}')
            return True

    return False

# ═══════════════════════════════
# OPEN NEW POSITION
# ═══════════════════════════════
def try_open_position(bot, exchange_obj, tickers, r):
    bot_id = bot[0]
    user_id = bot[1]
    exchange_id = bot[2]
    coin_category = db.get_all_coin_categories()
    method = bot[4]
    direction = bot[5]
    base_coin = bot[9]

    size_mult = float(bot[12] or 1.0)
    take_profit = float(bot[13] or 3.0)
    base_order = float(bot[15] or 10.0)
    trailing = float(bot[14] or 1.0)
    base_order = float(bot[15] or 10.0)
    trades_per_bot = int(bot[16] or 1)
    trades_per_coin = int(bot[17] or 1)
    trades_per_bot = bot[16] or 1
    trades_per_coin = bot[17] or 1

    # Check max trades per bot
    open_positions = db.get_open_positions(bot_id=bot_id)
    if len(open_positions) >= trades_per_bot:
        return

    # Get eligible coins
    open_coins = {}
    for p in open_positions:
        coin = p[4]
        open_coins[coin] = open_coins.get(coin, 0) + 1

    # Find coin to trade - randomize order
    import random
    ticker_items = list(tickers.items())
    random.shuffle(ticker_items)
    for symbol, ticker in ticker_items:
        if not symbol.endswith(f'/{base_coin}'):
            continue

        coin = symbol.replace(f'/{base_coin}', '')

        # Check trades per coin limit
        if open_coins.get(coin, 0) >= trades_per_coin:
            continue

        # Check gate conditions
        if not check_gate_conditions(bot, coin, open_positions):
            continue

        # Check ST flag
        if check_st_flag(coin, '', tickers, r):
            continue

        category = coin_category.get(coin, 'micro')

        # Check entry signal for research bots
        if method and (method.startswith('E') or method.startswith('BM')):
            params = {}
            try:
                import json
                params = json.loads(bot[29]) if bot[29] else {}
            except:
                params = {}
            # Use cached OHLCV data (fetched once per coin per cycle)
            if coin not in _ohlcv_cache:
                _ohlcv_cache[coin] = ind.to_arrays(db.get_ohlcv(coin, 'mexc', limit=200))
            btc_data = _ohlcv_cache.get('BTC')
            signal = es.check_entry_signal(method, params, coin, 'mexc', btc_data)
            if not signal:
                continue
        current_price = float(ticker.get('last') or 0)
        if current_price == 0:
            continue

        # Get sequence number
        coin_positions = [p for p in open_positions if p[4] == coin]
        sequence_number = len(coin_positions) + 1
        coin_trade_number = len(coin_positions) + 1

        # Execute entry
        result = execute_buy(
            exchange_obj, coin, base_order,
            None, bot_id, user_id, exchange_id,
            0, 'entry', r
        )

        if result:
            price = result['price']
            quantity = result['quantity']

            # Open position in DB
            pos_id = db.open_position(
                bot_id, user_id, exchange_id, None,
                coin, direction, price, quantity,
                base_order, price, category,
                PAPER_MODE, base_coin, 'USDT',
                sequence_number, coin_trade_number,
                method
            )
            print(f'✅ Position opened: {coin} #{pos_id}')
            tg.notify_trade_open(user_id, coin, direction, result['price'], base_order, method, PAPER_MODE)
            break

def check_gate_conditions(bot, coin, open_positions):
    gate_dca = bot[18]
    gate_timer = bot[19]
    gate_hours = bot[20] or 5

    if not gate_dca and not gate_timer:
        return True  # No gate · always tradeable

    # Find reference position for this coin
    coin_positions = [p for p in open_positions
                      if p[4] == coin and p[20]]  # is_gate_reference

    if not coin_positions:
        return True  # No reference · open first trade

    ref = coin_positions[0]
    ref_since = ref[23]  # gate_reference_since

    if gate_dca:
        dca_count = ref[10]
        if dca_count >= 1:  # Reference hit DCA
            return True

    if gate_timer and ref_since:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        if ref_since.tzinfo is None:
            ref_since = ref_since.replace(tzinfo=timezone.utc)
        elapsed = (now - ref_since).total_seconds() / 3600
        if elapsed >= gate_hours:
            return True

    return False

# ═══════════════════════════════
# MAIN BOT CYCLE
# ═══════════════════════════════
def run_cycle(r):
    cycle_start = time.time()
    print(f'\n--- Cycle {datetime.utcnow()} ---')

    # Pre-fetch BTC data and init OHLCV cache for this cycle
    global _ohlcv_cache
    _ohlcv_cache = {}
    import indicators as ind
    btc_rows = db.get_ohlcv('BTC', 'mexc', limit=200)
    _ohlcv_cache['BTC'] = ind.to_arrays(btc_rows) if btc_rows else None

    # Get all active bots grouped by exchange
    active_bots = db.get_active_bots()
    if not active_bots:
        print('No active bots')
        return

    # Group by exchange
    exchanges_needed = {}
    for bot in active_bots:
        exc_id = bot[2]
        if exc_id not in exchanges_needed:
            exchanges_needed[exc_id] = []
        exchanges_needed[exc_id].append(bot)

    # Process each exchange
    for exc_id, bots in exchanges_needed.items():
        exc_row = db.get_exchange_by_id(exc_id)
        if not exc_row:
            continue

        # Skip paused exchanges
        if exc_row[7]:  # paused_at
            print(f'Exchange {exc_id} paused · skipping')
            continue

        # Initialize exchange
        exchange_obj = init_exchange(exc_row)
        if not exchange_obj:
            continue

        # Fetch all prices at once
        tickers = fetch_and_cache_prices(
            exchange_obj, exc_row[2], r
        )

        if not tickers:
            continue

        # Get open positions for this exchange
        open_positions = db.get_open_positions(exchange_id=exc_id)

        # ─────────────────────────
        # STEP 1: Check ST flags + TP
        # ─────────────────────────
        positions_to_close = []
        for pos in open_positions:
            coin = pos[4]
            current_price = get_price(coin, exc_row[2], r, tickers)
            if not current_price:
                continue

            # ST flag check
            if check_st_flag(coin, exc_row[2], tickers, r):
                print(f'🚨 ST flag: {coin} · selling')
                result = execute_sell(
                    exchange_obj, coin, float(pos[8] or 0),
                    pos[0], pos[1], pos[2], exc_id, 'st_flag', r
                )
                if result:
                    positions_to_close.append((pos, result, 'st_flag'))
                    db.add_attention_log(
                        pos[2], 'red', 'st_flag',
                        f'{coin} ST flag detected · position closed',
                        bot_id=pos[1], position_id=pos[0]
                    )
                continue

            # TP check
            bot = next((b for b in bots if b[0] == pos[1]), None)
            if not bot:
                continue

            if check_tp(pos, current_price, bot):
                result = execute_sell(
                    exchange_obj, coin, float(pos[8] or 0),
                    pos[0], pos[1], pos[2], exc_id, 'tp', r
                )
                if result:
                    positions_to_close.append((pos, result, 'tp'))

        # Close positions and handle fees
        for pos, result, reason in positions_to_close:
            db.close_position(pos[0], reason)

            if reason == 'tp':
                # Calculate profit and fee
                invested = float(pos[9] or 0)
                received = result.get('usdt_received', 0)
                gross_profit = received - invested

                if gross_profit > 0:
                    fee_amount = gross_profit * 0.20
                    db.deduct_performance_fee(
                        pos[2], pos[0], fee_amount, gross_profit
                    )
                    print(f'💰 TP closed: {pos[4]} profit: ${gross_profit:.2f} fee: ${fee_amount:.2f}')
                    tg.notify_trade_closed(pos[2], pos[4], pos[5], float(pos[7] or 0), result.get('price', 0), gross_profit, fee_amount, pos[10], 'tp', PAPER_MODE)

                # Promote gate reference
                db.promote_gate_reference(pos[1], pos[4])

        # ─────────────────────────
        # STEP 2: Smart Queue DCA
        # ─────────────────────────
        queue_candidates = db.get_queue_candidates(exc_id)
        best_score = 0
        best_candidate = None
        best_next_price = None
        best_next_amount = None

        for pos in queue_candidates:
            coin = pos[1]  # pos[0]=id, pos[1]=coin
            current_price = get_price(coin, exc_row[2], r, tickers)
            if not current_price:
                continue

            bot = next((b for b in bots if b[0] == pos[7]), None)
            if not bot:
                continue

            result = calculate_score(pos, current_price, bot)
            if not result:
                continue

            score, next_dca_price, next_dca_amount = result

            # Check if price reached DCA trigger
            if current_price > next_dca_price:
                continue  # Not triggered yet

            if score > best_score:
                best_score = score
                best_candidate = pos
                best_next_price = next_dca_price
                best_next_amount = next_dca_amount

        # Execute best DCA
        if best_candidate:
            pos_id = best_candidate[0] if hasattr(
                best_candidate, '__getitem__') else best_candidate.id
            coin = best_candidate[1] if hasattr(
                best_candidate, '__getitem__') else best_candidate.coin

            print(f'📊 Queue: {coin} score={best_score:.4f}')

            db.set_position_queued(pos_id, True)
            result = execute_buy(
                exchange_obj, coin, best_next_amount,
                pos_id, best_candidate[7], best_candidate[8],
                exc_id, best_candidate[5] + 1, 'dca', r
            )

            if result:
                # Fetch current position data for accurate update
                with db.get_db() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT quantity, total_invested FROM positions WHERE id=%s",
                        (pos_id,)
                    )
                    pos_row = cur.fetchone()
                old_qty = float(pos_row[0] or 0)
                old_invested = float(pos_row[1] or 0)
                new_qty = old_qty + result['quantity']
                new_invested = old_invested + best_next_amount
                new_avg = new_invested / new_qty if new_qty > 0 else 0

                db.update_position_after_dca(
                    pos_id, new_avg, new_qty,
                    new_invested, result['price'],
                    best_candidate[5] + 1
                )
                db.set_position_queued(pos_id, False)
                print(f'✅ DCA executed: {coin} dca#{best_candidate[5]+1} avg=${new_avg:.6f} invested=${new_invested:.2f}')

        # ─────────────────────────
        # STEP 3: Open new positions
        # ─────────────────────────
        for bot in bots:
            try_open_position(bot, exchange_obj, tickers, r)

    # Record cycle time
    cycle_time = time.time() - cycle_start
    r.setex('bot:cycle_time', 120, str(round(cycle_time, 2)))
    r.setex('bot:last_cycle', 120, str(datetime.utcnow()))
    r.setex('bot:status', 120, 'running')
    print(f'✅ Cycle complete in {cycle_time:.2f}s')

# ═══════════════════════════════
# BOT LOOP ENTRY
# ═══════════════════════════════
def run_bot():
    print('🚀 Bot loop starting...')
    r = get_redis()
    consecutive_errors = 0

    while True:
        try:
            run_cycle(r)
            consecutive_errors = 0
            time.sleep(60)

        except KeyboardInterrupt:
            print('🛑 Bot stopped')
            break

        except Exception as e:
            consecutive_errors += 1
            print(f'❌ Cycle error ({consecutive_errors}): {e}')
            db.record_bot_event(None, None, 'cycle_error',
                               error_message=str(e))

            if consecutive_errors >= 3:
                send_admin(
                    f'🔴 Averion: {consecutive_errors} consecutive errors\n{str(e)[:200]}'
                )

            time.sleep(30)

if __name__ == '__main__':
    db.init_pool()
    run_bot()
