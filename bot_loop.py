import os
import time
import ccxt
import redis
from datetime import datetime, timezone
from dotenv import load_dotenv
import database as db
import entry_signals as es
from websocket_prices import MexcWebSocketPrices
import indicators
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
                    300,
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
            pass  # No price · skip silently
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
            tg.send_admin(f'🔴 Exchange paused: API key invalid\nExchange ID: {exchange_id}')
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
                 reason, r, tickers=None):
    symbol = f'{coin}/USDT'

    if PAPER_MODE:
        price = get_price(coin, '', r, tickers if tickers else {})
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
    # Use position-level dynamic params if available, else fall back to bot
    tp_percent = float(position[27] or bot[13] or 5.0)
    trailing_percent = float(position[29] or bot[14] or 2.0)

    if avg_cost == 0 or avg_cost < 1e-12:
        return False

    tp_price = avg_cost * (1 + tp_percent / 100)

    # Option B: if TP% - Trail% < 1% → skip trailing, sell directly at TP
    direct_tp = (tp_percent - trailing_percent) < 1.0

    # Arm TP when price reaches target
    if current_price >= tp_price and not tp_armed:
        db.arm_tp(position_id, current_price)
        print(f'🎯 TP armed: position {position_id} @ ${current_price:.6f}')
        peak_price = current_price
        tp_armed = True
        # Option B: direct sell when TP-Trail gap < 1%
        if direct_tp:
            print(f'🚀 Direct TP: position {position_id}')
            return True

    # Update peak price
    if tp_armed and current_price > peak_price:
        db.update_peak_price(position_id, current_price)
        peak_price = current_price

    # Fire trailing TP
    if tp_armed and peak_price > 0:
        trail_price = peak_price * (1 - trailing_percent / 100)
        if current_price <= trail_price:
            # Option A: minimum profit guard (0.5%)
            if current_price <= avg_cost * 1.005:
                return False
            print(f'🚀 TP firing: position {position_id}')
            return True

    return False

# ═══════════════════════════════
# REALTIME TP CHECKER (WebSocket callback)
# ═══════════════════════════════
# In-memory position cache for realtime TP
_rt_cache = {}
_rt_cache_time = 0
_rt_cache_lock = __import__('threading').Lock()

def _refresh_rt_cache(exc_id):
    global _rt_cache, _rt_cache_time
    import time as _t
    try:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.bot_id, p.user_id, p.exchange_id,
                       p.coin, p.direction, p.status,
                       p.avg_cost, p.quantity, p.total_invested,
                       p.dca_count, p.last_buy_price,
                       p.tp_armed, p.peak_price, p.queued,
                       p.standby_amount, p.standby_price,
                       p.category, p.is_paper, p.base_coin,
                       p.sequence_number, p.is_gate_reference,
                       p.coin_trade_number, p.gate_reference_since,
                       p.checkpoint_reached, p.pending_buyback,
                       p.opened_at,
                       p.pos_tp_pct, p.pos_dca_pct, p.pos_trail_pct
                FROM positions p
                WHERE p.status = 'open' AND p.exchange_id = %s
            """, (exc_id,))
            rows = cur.fetchall()
        cache = {}
        for row in rows:
            c = row[4]
            if c not in cache:
                cache[c] = []
            cache[c].append(row)
        with _rt_cache_lock:
            _rt_cache.clear()
            _rt_cache.update(cache)
            _rt_cache_time = _t.time()
    except Exception as e:
        print(f'Cache refresh error: {e}')

def make_realtime_tp_checker(exchange_obj, exc_id, exc_row):
    """Returns a callback function for WebSocket price updates."""
    def on_price_update(coin, price):
        try:
            import time as _t
            # Refresh cache every 30s
            if _t.time() - _rt_cache_time > 30:
                _refresh_rt_cache(exc_id)
            with _rt_cache_lock:
                positions = list(_rt_cache.get(coin, []))

            if not positions:
                return

            # Get bots for these positions
            active_bots = db.get_active_bots()
            r = get_redis()
            tickers = {f'{coin}/USDT': {'last': price}}
            # Remove closed positions from cache immediately
            with _rt_cache_lock:
                if coin in _rt_cache:
                    _rt_cache[coin] = [p for p in _rt_cache[coin] if p[6] == 'open']

            for pos in positions:
                bot = next((b for b in active_bots if b[0] == pos[1]), None)
                if not bot:
                    continue
                if check_tp(pos, price, bot):
                    result = execute_sell(
                        exchange_obj, coin, float(pos[8] or 0),
                        pos[0], pos[1], pos[2], exc_id, 'tp', r, tickers
                    )
                    if result:
                        db.close_position(pos[0], 'tp',
                            sell_price=result.get('price'),
                            usdt_received=result.get('usdt_received'))
                        invested = float(pos[9] or 0)
                        received = result.get('usdt_received', 0)
                        gross_profit = received - invested
                        if gross_profit > 0:
                            fee = gross_profit * 0.20
                            db.deduct_performance_fee(pos[2], pos[0], fee, gross_profit)
                        db.promote_gate_reference(pos[1], coin)
                        print(f'⚡ RT-TP closed: {coin} @ ${price:.6f} profit=${gross_profit:.2f}')
        except Exception as e:
            pass  # Never crash WebSocket thread
    return on_price_update

# ═══════════════════════════════
# OPEN NEW POSITION
# ═══════════════════════════════
def get_btc_regime_data(r):
    """Fetch BTC regime data once per cycle from DB + CoinGecko."""
    try:
        import requests
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT close FROM btc_daily
                ORDER BY timestamp DESC LIMIT 50
            """)
            rows = cur.fetchall()
        if len(rows) < 2:
            return None
        btc_price = float(rows[0][0])
        btc_prev = float(rows[1][0])
        sma50 = sum(float(r2[0]) for r2 in rows) / len(rows)
        change_24h = round((btc_price - btc_prev) / btc_prev * 100, 4)
        regime = 'bull' if btc_price > sma50 * 1.02 else 'bear' if btc_price < sma50 * 0.98 else 'sideways'

        # BTC dominance from Redis cache or CoinGecko
        dominance = None
        cached = r.get('btc:dominance')
        if cached:
            dominance = float(cached)
        else:
            try:
                resp = requests.get('https://api.coingecko.com/api/v3/global', timeout=5)
                if resp.status_code == 200:
                    dominance = round(resp.json()['data']['market_cap_percentage']['btc'], 2)
                    r.setex('btc:dominance', 3600, dominance)
            except:
                pass

        return {
            'btc_price': btc_price,
            'btc_sma50': round(sma50, 2),
            'btc_24h_change': change_24h,
            'btc_regime': regime,
            'btc_dominance': dominance
        }
    except Exception as e:
        print(f'⚠️ BTC regime error: {e}')
        return None


def try_open_position(bot, exchange_obj, tickers, r, coin_params_cache=None, btc_regime_data=None):
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
        return  # Already at max · skip coin scanning entirely

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
                _ohlcv_cache[coin] = indicators.to_arrays(db.get_ohlcv(coin, 'mexc', limit=200))
            btc_data = _ohlcv_cache.get('BTC')
            signal = es.check_entry_signal(method, params, coin, 'mexc', btc_data, _ohlcv_cache.get(coin))
            if not signal:
                continue
        current_price = float(ticker.get('last') or 0)
        if current_price == 0:
            continue
        # Guard: skip if price is suspiciously low (precision issue)
        if current_price < 1e-12:
            continue

        # Get sequence number
        coin_positions = [p for p in open_positions if p[4] == coin]
        sequence_number = len(coin_positions) + 1
        coin_trade_number = len(coin_positions) + 1

        # Execute entry
        # Get dynamic params for this coin
        cp = (coin_params_cache or {}).get(coin, {})
        dynamic_tp    = cp.get('take_profit', float(bot[13] or 5))
        dynamic_dca   = cp.get('dca_spacing', float(bot[11] or 7))
        dynamic_trail = cp.get('trailing',    float(bot[14] or 2))

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
                method,
                take_profit_pct=dynamic_tp,
                dca_spacing=dynamic_dca,
                trailing_pct=dynamic_trail,
                btc_price_at_entry=btc_regime_data.get('btc_price') if btc_regime_data else None,
                btc_sma50_at_entry=btc_regime_data.get('btc_sma50') if btc_regime_data else None,
                btc_24h_change_pct=btc_regime_data.get('btc_24h_change') if btc_regime_data else None,
                btc_regime=btc_regime_data.get('btc_regime') if btc_regime_data else None,
                btc_dominance=btc_regime_data.get('btc_dominance') if btc_regime_data else None
            )
            print(f'✅ Position opened: {coin} #{pos_id}')
            is_research = bot[4].startswith('E') or bot[4].startswith('BM') if bot else False
            if not is_research:
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
_last_health_time = 0

def run_cycle(r):
    cycle_start = time.time()
    print(f'\n--- Cycle {datetime.utcnow()} ---')
    # Mark bot as running at START of cycle
    try:
        get_redis().setex('bot:status', 600, 'running')
        get_redis().setex('bot:last_cycle', 600, str(datetime.utcnow()))
    except: pass

    # Record system health every 5 minutes
    global _last_health_time
    if time.time() - _last_health_time >= 300:
        try:
            import psutil
            cpu  = psutil.cpu_percent(interval=0.5)
            ram  = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            db.record_system_health(cpu, ram, disk, 0, 0, 0, 0, 0)
            _last_health_time = time.time()
            print(f'📊 Health recorded: CPU={cpu}% RAM={ram}% Disk={disk}%')
        except Exception as _e:
            print(f'⚠️ Health record error: {_e}')

    # Load coin parameters for dynamic DCA/TP/trail
    coin_params_cache = {}
    try:
        with db.get_db() as _conn:
            _cur = _conn.cursor()
            _cur.execute("SELECT coin, dca_spacing, take_profit_pct, trailing_pct FROM coin_parameters")
            for row in _cur.fetchall():
                coin_params_cache[row[0]] = {
                    'dca_spacing': float(row[1]),
                    'take_profit': float(row[2]),
                    'trailing':    float(row[3]),
                }
    except Exception as e:
        print(f'⚠️ coin_params load error: {e}')

    # Sync trades_per_bot = open_count + 1 for all research bots
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE bots b SET trades_per_bot =
                LEAST(250, GREATEST(1, (SELECT COUNT(*) FROM positions p
                    WHERE p.bot_id=b.id AND p.status='open') + 1))
            WHERE b.is_research=TRUE AND b.trading_on=TRUE
        """)

    # Run coin classification once per day
    _classify_key = 'classify:last_run'
    if not r.get(_classify_key):
        try:
            import classify_coins
            classify_coins.run()
            r.setex(_classify_key, 86400, '1')  # 24h
            print('✅ Coin classification updated')
        except Exception as e:
            print(f'⚠️ Classification error: {e}')

    # Pre-fetch BTC data and init OHLCV cache for this cycle
    global _ohlcv_cache
    _ohlcv_cache = {}
    btc_rows = db.get_ohlcv('BTC', 'mexc', limit=200)
    _ohlcv_cache['BTC'] = indicators.to_arrays(btc_rows) if btc_rows else None

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

        # Hook realtime TP checker for this exchange
        try:
            ws_prices.tp_callback = make_realtime_tp_checker(exchange_obj, exc_id, exc_row)
        except Exception:
            pass

        # Use WebSocket prices (already in Redis)
        # Fall back to REST if WebSocket not providing prices
        ws_status = r.get('ws:mexc:status')
        if ws_status == 'connected':
            # Build tickers from Redis for compatibility
            tickers = {}
            keys = r.keys(f'price:{exc_row[2]}:*/USDT')
            for key in keys:
                symbol = key.replace(f'price:{exc_row[2]}:', '')
                price = r.get(key)
                if price:
                    tickers[symbol] = {'last': float(price)}
            if tickers:
                print(f'✅ WS prices: {len(tickers)} pairs on {exc_row[2]}')
            else:
                tickers = fetch_and_cache_prices(exchange_obj, exc_row[2], r)
        else:
            tickers = fetch_and_cache_prices(exchange_obj, exc_row[2], r)

        if not tickers:
            continue

        # Get open positions for this exchange
        open_positions = db.get_open_positions(exchange_id=exc_id)
        # Pre-filter: only check TP for armed positions or positions near TP
        tp_candidates = [p for p in open_positions if p[12] or True]  # all for now

        # Batch arm all positions above TP price
        price_map = {sym.replace("/USDT",""):float(tick["last"]) for sym,tick in tickers.items() if tick.get("last") and sym.endswith("/USDT")}
        to_arm = []
        for pos in open_positions:
            if pos[12]: continue
            coin = pos[4]
            avg = float(pos[7] or 0)
            if avg == 0: continue
            price = price_map.get(coin)
            if not price: continue
            bot_obj = next((b for b in bots if b[0] == pos[1]), None)
            if not bot_obj: continue
            tp_price = avg * (1 + float(bot_obj[13] or 5)/100)
            if price >= tp_price:
                to_arm.append((price, pos[0]))
        if to_arm:
            with db.get_db() as _conn:
                _cur = _conn.cursor()
                _cur.executemany("UPDATE positions SET tp_armed=TRUE, peak_price=%s WHERE id=%s AND tp_armed=FALSE", to_arm)
            print(f"🎯 Batch armed {len(to_arm)} positions")

            open_positions = db.get_open_positions(exchange_id=exc_id)
        # ── BTC REGIME (once per cycle) ──
        btc_regime_data = get_btc_regime_data(r)
        if btc_regime_data:
            print(f'📈 BTC: ${btc_regime_data["btc_price"]:,.0f} · SMA50=${btc_regime_data["btc_sma50"]:,.0f} · {btc_regime_data["btc_regime"].upper()} · 24h={btc_regime_data["btc_24h_change"]:+.2f}%')

        # ─────────────────────────
        # STEP 1: Check ST flags (every 12h per exchange · per unique coin)
        # ─────────────────────────
        positions_to_close = []
        st_cache_key = f'st:checked:{exc_row[2]}'
        should_check_st = not r.get(st_cache_key)

        if should_check_st:
            print(f'🔍 ST flag check for {exc_row[2]}')
            flagged_coins = set()
            unique_coins = set(pos[4] for pos in open_positions)
            for coin in unique_coins:
                if check_st_flag(coin, exc_row[2], tickers, r):
                    flagged_coins.add(coin)
            # Mark as checked for 12 hours
            r.setex(st_cache_key, 43200, '1')

            # Close all positions for flagged coins
            for pos in open_positions:
                coin = pos[4]
                if coin in flagged_coins:
                    result = execute_sell(
                        exchange_obj, coin, float(pos[8] or 0),
                        pos[0], pos[1], pos[2], exc_id, 'st_flag', r, tickers
                    )
                    if result:
                        positions_to_close.append((pos, result, 'st_flag'))
                        db.add_attention_log(
                            pos[2], 'red', 'st_flag',
                            f'{coin} ST flag detected · position closed',
                            bot_id=pos[1], position_id=pos[0]
                        )


        # TP check - separate loop for ALL open positions every cycle
        for pos in open_positions:
            coin = pos[4]
            current_price = price_map.get(coin) or get_price(coin, exc_row[2], r, tickers)
            if not current_price:
                continue
            bot_obj = next((b for b in bots if b[0] == pos[1]), None)
            if not bot_obj:
                continue
            if check_tp(pos, current_price, bot_obj):
                result = execute_sell(
                    exchange_obj, coin, float(pos[8] or 0),
                    pos[0], pos[1], pos[2], exc_id, 'tp', r, tickers
                )
                if result:
                    positions_to_close.append((pos, result, 'tp'))

        # Close positions and handle fees
        for pos, result, reason in positions_to_close:
            db.close_position(pos[0], reason,
                sell_price=result.get('price'),
                usdt_received=result.get('usdt_received'))


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
                    _pos_bot = next((b for b in bots if b[0] == pos[1]), None)
                    pos_is_research = bool(_pos_bot and _pos_bot[31]) if _pos_bot and len(_pos_bot) > 31 else bool(_pos_bot and (_pos_bot[4].startswith('E') or _pos_bot[4].startswith('BM')))
                    if not pos_is_research:
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
                print(f'✅ DCA executed: {coin} dca#{best_candidate[5]+1} avg=${new_avg:.6f} invested=${new_invested:.2f} time={datetime.utcnow().strftime("%H:%M:%S")}')
                try:
                    _best_bot = next((b for b in bots if b[0] == best_candidate[7]), None)
                    best_is_research = bool(_best_bot and _best_bot[31]) if _best_bot and len(_best_bot) > 31 else bool(_best_bot and (_best_bot[4].startswith('E') or _best_bot[4].startswith('BM')))
                    if not best_is_research:
                        tg.notify_dca(best_candidate[8], coin, best_candidate[5]+1, result['price'], best_next_amount, new_avg, PAPER_MODE)
                except Exception:
                    pass

        # ─────────────────────────
        # STEP 3: Open new positions
        # ─────────────────────────
        # Pre-filter: only bots that haven't reached max trades
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT bot_id, COUNT(*) as cnt
                FROM positions WHERE status='open'
                GROUP BY bot_id
            """)
            open_counts = {r2[0]: r2[1] for r2 in cur.fetchall()}

        bots_needing_trades = [
            b for b in bots
            if open_counts.get(b[0], 0) < int(b[16] or 1)
        ]
        print(f'Bots needing trades: {len(bots_needing_trades)}/{len(bots)}')
        for bot in bots_needing_trades:
            try_open_position(bot, exchange_obj, tickers, r, coin_params_cache, btc_regime_data)

    # Record cycle time
    cycle_time = time.time() - cycle_start
    r.setex('bot:cycle_time', 600, str(round(cycle_time, 2)))
    r.setex('bot:last_cycle', 600, str(datetime.utcnow()))
    r.setex('bot:status', 600, 'running')
    print(f'✅ Cycle complete in {cycle_time:.2f}s · {datetime.utcnow().strftime("%H:%M:%S")}')

# ═══════════════════════════════
# BOT LOOP ENTRY
# ═══════════════════════════════
def run_bot():
    print('🚀 Bot loop starting...')
    r = get_redis()
    consecutive_errors = 0

    # Start WebSocket price stream in background
    ws_prices = MexcWebSocketPrices()
    ws_prices.start_background()
    import time as _t
    print('⏳ Waiting 5s for WebSocket to connect...')
    _t.sleep(5)
    # Hook realtime TP checker after exchanges are known
    # Will be set per exchange in run_cycle

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
                tg.send_admin(
                    f'🔴 Averion: {consecutive_errors} consecutive errors\n{str(e)[:200]}'
                )

            time.sleep(30)

if __name__ == '__main__':
    db.init_pool()
    run_bot()
