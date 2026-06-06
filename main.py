import os
import time
import psycopg2
import redis
import ccxt
import exchanges as exchanges_module
import telegram as tg
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════
# CONFIGURATION
# ═══════════════════════════════
PAPER_MODE = os.getenv('PAPER_MODE', 'true').lower() == 'true'
MAX_COINS = os.getenv('MAX_COINS')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# ═══════════════════════════════
# STARTUP ASSERTIONS
# ═══════════════════════════════
def check_assertions():
    if MAX_COINS and not PAPER_MODE:
        raise Exception(
            "CRITICAL: Remove MAX_COINS before going live! "
            "MAX_COINS is for Replit only."
        )
    print(f"✅ Mode: {'PAPER' if PAPER_MODE else 'LIVE'}")
    print(f"✅ Assertions passed")

# ═══════════════════════════════
# WAIT FOR POSTGRESQL
# ═══════════════════════════════
def wait_for_postgresql():
    print("⏳ Waiting for PostgreSQL...")
    attempts = 0
    max_attempts = 12  # 60 seconds total
    while attempts < max_attempts:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("✅ PostgreSQL ready")
            db.init_pool()
            return True
        except Exception as e:
            attempts += 1
            print(f"PostgreSQL not ready ({attempts}/{max_attempts}): {e}")
            time.sleep(5)
    raise Exception("❌ PostgreSQL not available after 60 seconds · exiting")

# ═══════════════════════════════
# WAIT FOR REDIS
# ═══════════════════════════════
def wait_for_redis():
    print("⏳ Waiting for Redis...")
    attempts = 0
    max_attempts = 10  # 30 seconds total
    while attempts < max_attempts:
        try:
            r = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            r.ping()
            print("✅ Redis ready")
            return r
        except Exception as e:
            attempts += 1
            print(f"Redis not ready ({attempts}/{max_attempts}): {e}")
            time.sleep(3)
    raise Exception("❌ Redis not available after 30 seconds · exiting")

# ═══════════════════════════════
# UNCONFIRMED ORDER RECONCILIATION
# ═══════════════════════════════
def reconcile_orders():
    print("🔄 Running startup reconciliation...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Get all active exchanges
        cur.execute("""
            SELECT id, exchange, api_key_enc, secret_enc, passphrase_enc
            FROM exchanges
            WHERE active = TRUE AND paused_at IS NULL
        """)
        exchanges = cur.fetchall()

        for exc in exchanges:
            exc_id, exc_name, api_key, secret, passphrase = exc
            try:
                # Initialize CCXT exchange
                exchange_class = getattr(ccxt, exc_name)
                config = {
                    'apiKey': exchanges_module.decrypt(api_key),
                    'secret': exchanges_module.decrypt(secret)
                }
                if passphrase:
                    config['password'] = exchanges_module.decrypt(passphrase)

                exchange = exchange_class(config)

                # Fetch last 100 orders
                orders = exchange.fetch_orders(limit=100)

                for order in orders:
                    order_id = order.get('id')
                    if not order_id:
                        continue

                    # Check if order exists in DB
                    cur.execute("""
                        SELECT id FROM trades
                        WHERE exchange_order_id = %s
                    """, (order_id,))

                    if not cur.fetchone():
                        # Order on exchange but not in DB
                        # Look up position to get user_id and bot_id
                        symbol = order.get('symbol', '')
                        coin = symbol.split('/')[0] if '/' in symbol else symbol
                        order_time = datetime.utcfromtimestamp(
                            order.get('timestamp', 0) / 1000
                        ) if order.get('timestamp') else datetime.utcnow()

                        cur.execute("""
                            SELECT id, user_id, bot_id
                            FROM positions
                            WHERE exchange_id = %s
                            AND coin = %s
                            AND status = 'open'
                            ORDER BY ABS(EXTRACT(EPOCH FROM
                                (opened_at - %s::timestamp)))
                            LIMIT 1
                        """, (exc_id, coin, order_time))
                        pos = cur.fetchone()

                        if not pos:
                            print(f"⚠️ Skipping orphan order {order_id} · no matching position found")
                            continue

                        position_id = pos[0]
                        user_id = pos[1]
                        bot_id = pos[2]

                        print(f"⚠️ Missing order found: {order_id} on {exc_name}")
                        cur.execute("""
                            INSERT INTO trades (
                                position_id, bot_id, user_id,
                                exchange_id, coin, side, price,
                                quantity, usdt_amount, order_type,
                                exchange_order_id, is_paper,
                                timestamp
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, FALSE, %s
                            )
                        """, (
                            position_id, bot_id, user_id,
                            exc_id, coin,
                            order.get('side'),
                            order.get('average') or order.get('price') or 0,
                            order.get('filled') or 0,
                            order.get('cost') or 0,
                            order.get('type'),
                            order_id,
                            order_time
                        ))
                        print(f"✅ Reconciled: {order_id} → position #{position_id}")

                conn.commit()
                print(f"✅ Reconciliation complete for {exc_name}")

            except Exception as e:
                print(f"⚠️ Reconciliation skipped for {exc_name}: {e}")
                continue

        conn.close()
        print("✅ Startup reconciliation complete")

    except Exception as e:
        print(f"⚠️ Reconciliation error: {e} · continuing anyway")

# ═══════════════════════════════
# SEND TELEGRAM
# ═══════════════════════════════
def send_telegram(msg):
    try:
        import requests
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': ADMIN_CHAT, 'text': msg},
            timeout=10
        )
    except:
        pass

# ═══════════════════════════════
# MAIN BOT LOOP
# ═══════════════════════════════
def bot_loop(redis_client):
    print("🚀 Bot loop starting...")
    tg.admin_bot_started(PAPER_MODE)

    cycle = 0
    while True:
        try:
            cycle += 1
            start = time.time()

            from bot_loop import run_cycle
            run_cycle(redis_client)

            elapsed = time.time() - start
            print(f"Cycle {cycle} complete in {elapsed:.2f}s")

            # Store loop health in Redis
            redis_client.setex('bot:last_cycle', 120, str(datetime.utcnow()))
            redis_client.setex('bot:cycle_time', 120, str(round(elapsed, 2)))
            redis_client.setex('bot:status', 120, 'running')

            # Sleep remainder of 60 seconds
            sleep_time = max(0, 60 - elapsed)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("🛑 Bot stopped manually")
            tg.admin_bot_stopped("manual")
            break
        except Exception as e:
            print(f"❌ Loop error: {e}")
            redis_client.setex('bot:status', 120, f'error: {e}')
            time.sleep(10)

# ═══════════════════════════════
# STARTUP SEQUENCE
# ═══════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("AVERION — Adaptive DCA Trading Bot")
    print(f"Starting: {datetime.utcnow()}")
    print("=" * 50)

    try:
        # Step 1: Assertions
        check_assertions()

        # Step 2: Wait for PostgreSQL
        wait_for_postgresql()

        # Step 3: Wait for Redis
        redis_client = wait_for_redis()

        # Step 4: Reconcile orders
        reconcile_orders()

        # Step 5: Start bot loop
        bot_loop(redis_client)

    except Exception as e:
        print(f"❌ FATAL: {e}")
        tg.admin_error(str(e))
        exit(1)

def clear_stale_pending_buyback():
    """Clear PENDING_BUYBACK flags older than 60 seconds"""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions
            SET pending_buyback = FALSE,
                pending_buyback_since = NULL
            WHERE pending_buyback = TRUE
            AND pending_buyback_since < NOW() - INTERVAL '60 seconds'
        """)
        count = cur.rowcount
        conn.commit()
        if count > 0:
            print(f'⚠️ Cleared {count} stale PENDING_BUYBACK flags')
            tg.send_admin(f'⚠️ Cleared {count} stale PENDING_BUYBACK flags on startup')
