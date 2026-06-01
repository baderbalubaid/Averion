import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════
# CONNECTION POOL
# ═══════════════════════════════
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

_pool = None

def init_pool():
    global _pool
    _pool = psycopg2.pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=10,
        **DB_CONFIG
    )
    print('✅ Database connection pool initialized')

@contextmanager
def get_db():
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        _pool.putconn(conn)

# ═══════════════════════════════
# USERS
# ═══════════════════════════════
def get_user_by_email(email):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, email, password_hash, is_admin,
                   is_zero_fee, is_suspended, free_trial_credit
            FROM users WHERE email = %s
        """, (email,))
        return cur.fetchone()

def get_user_by_id(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, email, is_admin, is_zero_fee,
                   is_suspended, telegram_chat_id,
                   telegram_verified, bot_slots_total,
                   trades_used_this_month, next_billing_date
            FROM users WHERE id = %s
        """, (user_id,))
        return cur.fetchone()

def create_user(email, password_hash, referral_code=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (email, password_hash, referral_code)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (email, password_hash, referral_code))
        return cur.fetchone()[0]

# ═══════════════════════════════
# EXCHANGES
# ═══════════════════════════════
def get_user_exchanges(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, exchange, custom_name, active,
                   paused_at, pause_reason, last_connected_at,
                   ip_whitelist_confirmed, key_expires_at
            FROM exchanges
            WHERE user_id = %s AND active = TRUE
            ORDER BY created_at ASC
        """, (user_id,))
        return cur.fetchall()

def get_exchange_by_id(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, exchange, api_key_enc,
                   secret_enc, passphrase_enc, active,
                   paused_at, pause_reason
            FROM exchanges WHERE id = %s
        """, (exchange_id,))
        return cur.fetchone()

def add_exchange(user_id, exchange, custom_name,
                 api_key_enc, secret_enc, passphrase_enc=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO exchanges
            (user_id, exchange, custom_name, api_key_enc,
             secret_enc, passphrase_enc)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, exchange, custom_name,
              api_key_enc, secret_enc, passphrase_enc))
        return cur.fetchone()[0]

def pause_exchange(exchange_id, reason, pause_type='manual'):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE exchanges
            SET paused_at = NOW(), pause_reason = %s,
                pause_type = %s
            WHERE id = %s
        """, (reason, pause_type, exchange_id))

def resume_exchange(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE exchanges
            SET paused_at = NULL, pause_reason = NULL,
                pause_type = NULL, reconnect_attempts = 0,
                last_connected_at = NOW()
            WHERE id = %s
        """, (exchange_id,))

# ═══════════════════════════════
# BOTS
# ═══════════════════════════════
def get_user_bots(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.name, b.method, b.direction,
                   b.trading_on, b.dca_on, b.is_paper,
                   b.status, b.expires_at, b.auto_renew,
                   b.base_coin, b.trades_per_bot,
                   b.trades_per_coin, b.gate_dca_enabled,
                   b.gate_timer_enabled, b.gate_timer_hours,
                   b.order_entry_type, b.order_dca_type,
                   e.exchange, e.custom_name
            FROM bots b
            JOIN exchanges e ON e.id = b.exchange_id
            WHERE b.user_id = %s AND b.status != 'deleted'
            ORDER BY b.created_at ASC
        """, (user_id,))
        return cur.fetchall()

def get_active_bots():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.user_id, b.exchange_id,
                   b.name, b.method, b.direction,
                   b.trading_on, b.dca_on, b.is_paper,
                   b.base_coin, b.dca_percent,
                   b.spacing_multiplier, b.size_multiplier,
                   b.take_profit_percent, b.trailing_percent,
                   b.base_order, b.trades_per_bot,
                   b.trades_per_coin, b.gate_dca_enabled,
                   b.gate_timer_enabled, b.gate_timer_hours,
                   b.order_entry_type, b.order_dca_type,
                   b.dca_checkpoint_level, b.dca_checkpoint_on,
                   e.exchange, e.api_key_enc, e.secret_enc,
                   e.passphrase_enc, e.paused_at
            FROM bots b
            JOIN exchanges e ON e.id = b.exchange_id
            WHERE b.status = 'active'
            AND b.trading_on = TRUE
            AND e.paused_at IS NULL
            ORDER BY b.id ASC
        """)
        return cur.fetchall()

def create_bot(user_id, exchange_id, wallet_id, name,
               method, direction, base_order, dca_percent,
               spacing_multiplier, size_multiplier,
               take_profit_percent, trailing_percent,
               base_coin, is_paper, trades_per_bot,
               trades_per_coin, gate_dca_enabled,
               gate_timer_enabled, gate_timer_hours,
               order_entry_type, order_dca_type):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bots (
                user_id, exchange_id, wallet_id, name,
                method, direction, base_order, dca_percent,
                spacing_multiplier, size_multiplier,
                take_profit_percent, trailing_percent,
                base_coin, is_paper, trades_per_bot,
                trades_per_coin, gate_dca_enabled,
                gate_timer_enabled, gate_timer_hours,
                order_entry_type, order_dca_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            ) RETURNING id
        """, (user_id, exchange_id, wallet_id, name,
              method, direction, base_order, dca_percent,
              spacing_multiplier, size_multiplier,
              take_profit_percent, trailing_percent,
              base_coin, is_paper, trades_per_bot,
              trades_per_coin, gate_dca_enabled,
              gate_timer_enabled, gate_timer_hours,
              order_entry_type, order_dca_type))
        return cur.fetchone()[0]

# ═══════════════════════════════
# POSITIONS
# ═══════════════════════════════
def get_open_positions(exchange_id=None, bot_id=None):
    with get_db() as conn:
        cur = conn.cursor()
        query = """
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
                   p.opened_at
            FROM positions p
            WHERE p.status = 'open'
        """
        params = []
        if exchange_id:
            query += " AND p.exchange_id = %s"
            params.append(exchange_id)
        if bot_id:
            query += " AND p.bot_id = %s"
            params.append(bot_id)
        query += " ORDER BY p.total_invested DESC"
        cur.execute(query, params)
        return cur.fetchall()

def open_position(bot_id, user_id, exchange_id, wallet_id,
                  coin, direction, avg_cost, quantity,
                  total_invested, last_buy_price, category,
                  is_paper, base_coin, sequence_number,
                  coin_trade_number, entry_method=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO positions (
                bot_id, user_id, exchange_id, wallet_id,
                coin, direction, avg_cost, quantity,
                total_invested, last_buy_price, category,
                is_paper, base_coin, sequence_number,
                coin_trade_number, entry_method,
                is_gate_reference, gate_reference_since
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s,
                TRUE, NOW()
            ) RETURNING id
        """, (bot_id, user_id, exchange_id, wallet_id,
              coin, direction, avg_cost, quantity,
              total_invested, last_buy_price, category,
              is_paper, base_coin, sequence_number,
              coin_trade_number, entry_method))
        return cur.fetchone()[0]

def update_position_after_dca(position_id, avg_cost,
                               quantity, total_invested,
                               last_buy_price, dca_count):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                avg_cost = %s,
                quantity = %s,
                total_invested = %s,
                last_buy_price = %s,
                dca_count = %s
            WHERE id = %s
        """, (avg_cost, quantity, total_invested,
              last_buy_price, dca_count, position_id))

def arm_tp(position_id, peak_price):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                tp_armed = TRUE, peak_price = %s
            WHERE id = %s
        """, (peak_price, position_id))

def update_peak_price(position_id, peak_price):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET peak_price = %s
            WHERE id = %s
        """, (peak_price, position_id))

def close_position(position_id, close_reason):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                status = 'closed',
                closed_at = NOW(),
                close_reason = %s,
                is_gate_reference = FALSE
            WHERE id = %s
        """, (close_reason, position_id))

def promote_gate_reference(bot_id, coin):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET
                is_gate_reference = TRUE,
                gate_reference_since = NOW()
            WHERE id = (
                SELECT id FROM positions
                WHERE bot_id = %s AND coin = %s
                AND status = 'open'
                ORDER BY sequence_number DESC
                LIMIT 1
            )
        """, (bot_id, coin))

# ═══════════════════════════════
# TRADES
# ═══════════════════════════════
def record_trade(position_id, bot_id, user_id,
                 exchange_id, coin, side, price,
                 quantity, usdt_amount, exchange_fee,
                 fee_currency, reason, order_type,
                 exchange_order_id, is_paper, dca_level):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO trades (
                position_id, bot_id, user_id, exchange_id,
                coin, side, price, quantity, usdt_amount,
                exchange_fee, fee_currency, reason,
                order_type, exchange_order_id, is_paper,
                dca_level
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (position_id, bot_id, user_id, exchange_id,
              coin, side, price, quantity, usdt_amount,
              exchange_fee, fee_currency, reason,
              order_type, exchange_order_id, is_paper,
              dca_level))
        return cur.fetchone()[0]

def get_position_trades(position_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, side, price, quantity, usdt_amount,
                   exchange_fee, reason, order_type,
                   dca_level, timestamp
            FROM trades
            WHERE position_id = %s
            ORDER BY timestamp ASC
        """, (position_id,))
        return cur.fetchall()

# ═══════════════════════════════
# SMART QUEUE
# ═══════════════════════════════
def get_queue_candidates(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.coin, p.total_invested,
                   p.last_buy_price, p.avg_cost,
                   p.dca_count, p.category,
                   p.bot_id, p.user_id,
                   b.dca_percent, b.spacing_multiplier,
                   b.size_multiplier, b.base_order,
                   b.dca_on, b.dca_checkpoint_level,
                   b.dca_checkpoint_on
            FROM positions p
            JOIN bots b ON b.id = p.bot_id
            WHERE p.exchange_id = %s
            AND p.status = 'open'
            AND p.queued = FALSE
            AND b.dca_on = TRUE
            AND b.trading_on = TRUE
            ORDER BY p.total_invested DESC
        """, (exchange_id,))
        return cur.fetchall()

def set_position_queued(position_id, queued=True):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE positions SET queued = %s
            WHERE id = %s
        """, (queued, position_id))

# ═══════════════════════════════
# ATTENTION LOG
# ═══════════════════════════════
def add_attention_log(user_id, severity, item_type,
                      message, bot_id=None, position_id=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO attention_log
            (user_id, bot_id, position_id, severity,
             item_type, message)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, bot_id, position_id, severity,
              item_type, message))
        return cur.fetchone()[0]

def resolve_attention_log(log_id, action_taken):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE attention_log SET
                resolved = TRUE,
                resolved_at = NOW(),
                action_taken = %s
            WHERE id = %s
        """, (action_taken, log_id))

def get_user_attention_logs(user_id, resolved=False):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, severity, item_type, message,
                   bot_id, position_id, created_at
            FROM attention_log
            WHERE user_id = %s AND resolved = %s
            ORDER BY
                CASE severity
                    WHEN 'red' THEN 1
                    WHEN 'yellow' THEN 2
                    WHEN 'green' THEN 3
                END,
                created_at DESC
        """, (user_id, resolved))
        return cur.fetchall()

# ═══════════════════════════════
# RESERVE WALLET
# ═══════════════════════════════
def get_reserve_wallet(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, balance_usdt, total_deposited,
                   total_deducted
            FROM reserve_wallets
            WHERE user_id = %s
        """, (user_id,))
        return cur.fetchone()

def deduct_performance_fee(user_id, position_id,
                            fee_amount, trade_profit):
    with get_db() as conn:
        cur = conn.cursor()
        # Check balance
        cur.execute("""
            SELECT balance_usdt FROM reserve_wallets
            WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
        balance = float(row[0]) if row else 0

        if balance >= fee_amount:
            # Deduct from reserve
            cur.execute("""
                UPDATE reserve_wallets SET
                    balance_usdt = balance_usdt - %s,
                    total_deducted = total_deducted + %s,
                    last_updated = NOW()
                WHERE user_id = %s
            """, (fee_amount, fee_amount, user_id))
            paid = True
        else:
            # Record as debt
            paid = False

        # Record in fee_debt
        cur.execute("""
            INSERT INTO fee_debt
            (user_id, position_id, amount_usdt, trade_profit)
            VALUES (%s, %s, %s, %s)
        """, (user_id, position_id, fee_amount, trade_profit))

        return paid

# ═══════════════════════════════
# COIN CLASSIFICATION
# ═══════════════════════════════
def get_coin_category(coin):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT category, recorded_cap
            FROM coin_history
            WHERE coin = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (coin,))
        row = cur.fetchone()
        return row[0] if row else 'micro'

def get_all_coin_categories():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (coin) coin, category,
                   recorded_cap, recorded_at
            FROM coin_history
            ORDER BY coin, recorded_at DESC
        """)
        return {row[0]: row[1] for row in cur.fetchall()}

# ═══════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════
def record_system_health(cpu, ram, disk, redis_mb,
                          pg_conn, cycle_time,
                          active_bots, open_positions):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO system_health (
                cpu_percent, ram_percent, disk_percent,
                redis_mb, pg_connections, bot_cycle_time,
                active_bots, open_positions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (cpu, ram, disk, redis_mb, pg_conn,
              cycle_time, active_bots, open_positions))
        # Delete older than 30 days
        cur.execute("""
            DELETE FROM system_health
            WHERE recorded_at < NOW() - INTERVAL '30 days'
        """)

def record_performance_timing(step, duration,
                               records, status, error=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO performance_timing (
                step, duration_seconds, records_processed,
                status, error_message, started_at
            ) VALUES (%s, %s, %s, %s, %s,
                      NOW() - INTERVAL '%s seconds')
        """, (step, duration, records, status, error, duration))
        # Delete older than 30 days
        cur.execute("""
            DELETE FROM performance_timing
            WHERE completed_at < NOW() - INTERVAL '30 days'
        """)

def record_bot_event(bot_id, user_id, event_type,
                     coin=None, exchange=None,
                     error_message=None, stack_trace=None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bot_events (
                bot_id, user_id, event_type, coin,
                exchange, error_message, stack_trace
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (bot_id, user_id, event_type, coin,
              exchange, error_message, stack_trace))
        # Delete older than 30 days
        cur.execute("""
            DELETE FROM bot_events
            WHERE recorded_at < NOW() - INTERVAL '30 days'
        """)

if __name__ == '__main__':
    init_pool()
    print('✅ Database module ready')
    print('✅ All functions available')
