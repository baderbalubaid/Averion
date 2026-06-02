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
            SELECT u.id, u.email, u.is_admin, u.is_zero_fee,
                   u.is_suspended, t.chat_id,
                   t.verified, u.bot_slots_total,
                   COALESCE(s.trades_used_this_month, 0), u.next_billing_date
            FROM users u
            LEFT JOIN user_telegram t ON t.user_id = u.id
            LEFT JOIN user_subscriptions s ON s.user_id = u.id
            WHERE u.id = %s
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

# Column order reference for bot_loop.py:
# 0=id 1=user_id 2=exchange_id 3=name 4=method 5=direction
# 6=trading_on 7=dca_on 8=is_paper 9=base_coin 10=dca_percent
# 11=spacing_mult 12=size_mult 13=take_profit 14=trailing
# 15=base_order 16=trades_per_bot 17=trades_per_coin
# 18=gate_dca_on 19=gate_timer_on 20=gate_timer_hours
# 21=order_entry_type 22=order_dca_type
# 23=checkpoint_level 24=checkpoint_on
# 25=exchange 26=api_key_enc 27=secret_enc
# 28=passphrase_enc 29=paused_at
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
            AND (b.expires_at IS NULL OR b.expires_at > NOW())
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
                  is_paper, base_coin, profit_coin, sequence_number,
                  coin_trade_number, entry_method=None, profit_coin='USDT'):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO positions (
                bot_id, user_id, exchange_id, wallet_id,
                coin, direction, avg_cost, quantity,
                total_invested, last_buy_price, category,
                is_paper, base_coin, profit_coin, sequence_number,
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


def get_user_trade_usage(user_id):
   with get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           SELECT trades_used_this_month,
                  free_trade_bundle + paid_trade_bundle as total_bundle
           FROM user_subscriptions
           WHERE user_id = %s
       """, (user_id,))
       row = cur.fetchone()
       if not row:
           return {'used': 0, 'total': 100}
       return {
           'used': row[0] or 0,
           'total': row[1] or 100
       }

def increment_trade_usage(user_id):
   with get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           UPDATE user_subscriptions
           SET trades_used_this_month = trades_used_this_month + 1
           WHERE user_id = %s
       """, (user_id,))

if __name__ == '__main__':
    init_pool()
    print('✅ Database module ready')
    print('✅ All functions available')

# ═══════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════
def queue_notification(user_id, chat_id, message, message_type):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notification_queue
            (user_id, chat_id, message, message_type)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, chat_id, message, message_type))
        return cur.fetchone()[0]

def get_pending_notifications():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, chat_id, message, message_type
            FROM notification_queue
            WHERE sent = FALSE
            ORDER BY created_at ASC
            LIMIT 50
        """)
        return cur.fetchall()

def mark_notification_sent(notification_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE notification_queue
            SET sent = TRUE, sent_at = NOW()
            WHERE id = %s
        """, (notification_id,))

def increment_notification_retry(notification_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE notification_queue
            SET retry_count = retry_count + 1
            WHERE id = %s
        """, (notification_id,))

# ═══════════════════════════════
# VIRTUAL WALLETS
# ═══════════════════════════════
def get_user_wallets(user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT w.id, w.name, w.currency,
                   w.allocation_type, w.allocation_amount,
                   w.current_balance, w.standby_reserved,
                   e.exchange, e.custom_name
            FROM virtual_wallets w
            JOIN exchanges e ON e.id = w.exchange_id
            WHERE w.user_id = %s
            ORDER BY w.created_at ASC
        """, (user_id,))
        return cur.fetchall()

def get_wallet_by_id(wallet_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, user_id, exchange_id, name,
                   currency, allocation_type,
                   allocation_amount, current_balance,
                   standby_reserved
            FROM virtual_wallets WHERE id = %s
        """, (wallet_id,))
        return cur.fetchone()

def create_wallet(user_id, exchange_id, name,
                  currency, allocation_type, allocation_amount):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO virtual_wallets
            (user_id, exchange_id, name, currency,
             allocation_type, allocation_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, exchange_id, name, currency,
              allocation_type, allocation_amount))
        return cur.fetchone()[0]

def update_wallet_balance(wallet_id, amount, operation='add'):
    with get_db() as conn:
        cur = conn.cursor()
        if operation == 'add':
            cur.execute("""
                UPDATE virtual_wallets
                SET current_balance = current_balance + %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (amount, wallet_id))
        else:
            cur.execute("""
                UPDATE virtual_wallets
                SET current_balance = current_balance - %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (amount, wallet_id))

def record_wallet_transaction(wallet_id, position_id,
                               tx_type, amount, balance_after):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO wallet_transactions
            (wallet_id, position_id, type, amount, balance_after)
            VALUES (%s, %s, %s, %s, %s)
        """, (wallet_id, position_id, tx_type,
              amount, balance_after))

# ═══════════════════════════════
# BALANCE HISTORY
# ═══════════════════════════════
def record_balance_history(user_id, exchange_id, value_usdt):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO balance_history
            (user_id, exchange_id, value_usdt)
            VALUES (%s, %s, %s)
        """, (user_id, exchange_id, value_usdt))

def get_balance_history(exchange_id, days=30):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT value_usdt, recorded_at
            FROM balance_history
            WHERE exchange_id = %s
            AND recorded_at > NOW() - INTERVAL '%s days'
            ORDER BY recorded_at ASC
        """, (exchange_id, days))
        return cur.fetchall()

# ═══════════════════════════════
# OHLCV
# ═══════════════════════════════
def store_ohlcv(coin, exchange, timestamp,
                open_p, high, low, close, volume):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ohlcv_hourly
            (coin, exchange, timestamp, open, high,
             low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (coin, exchange, timestamp)
            DO NOTHING
        """, (coin, exchange, timestamp,
              open_p, high, low, close, volume))

def get_ohlcv(coin, exchange, limit=100):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, open, high, low, close,
                   volume, atr_14
            FROM ohlcv_hourly
            WHERE coin = %s AND exchange = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """, (coin, exchange, limit))
        return cur.fetchall()

def update_atr(coin, exchange, atr_14):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE ohlcv_hourly SET atr_14 = %s
            WHERE coin = %s AND exchange = %s
            AND timestamp = (
                SELECT MAX(timestamp) FROM ohlcv_hourly
                WHERE coin = %s AND exchange = %s
            )
        """, (atr_14, coin, exchange, coin, exchange))

def cleanup_old_ohlcv(days=90):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM ohlcv_hourly
            WHERE timestamp < NOW() - INTERVAL '%s days'
        """, (days,))
        return cur.rowcount

# ═══════════════════════════════
# RESEARCH SCORES
# ═══════════════════════════════
def update_research_score(bot_id, method, config_id,
                           total_trades, winning_trades,
                           total_profit, max_drawdown,
                           avg_hold_hours):
    with get_db() as conn:
        cur = conn.cursor()
        losing = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100
                    ) if total_trades > 0 else 0

        cur.execute("""
            INSERT INTO research_scores (
                bot_id, method, bot_config_id,
                total_trades, winning_trades, losing_trades,
                win_rate, total_profit, max_drawdown,
                avg_hold_hours, last_calculated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (bot_id) DO UPDATE SET
                total_trades = EXCLUDED.total_trades,
                winning_trades = EXCLUDED.winning_trades,
                losing_trades = EXCLUDED.losing_trades,
                win_rate = EXCLUDED.win_rate,
                total_profit = EXCLUDED.total_profit,
                max_drawdown = EXCLUDED.max_drawdown,
                avg_hold_hours = EXCLUDED.avg_hold_hours,
                last_calculated = NOW()
        """, (bot_id, method, config_id, total_trades,
              winning_trades, losing, win_rate,
              total_profit, max_drawdown, avg_hold_hours))

def get_research_rankings():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.bot_id, r.method, r.bot_config_id,
                   r.total_trades, r.win_rate,
                   r.total_profit, r.max_drawdown,
                   r.avg_hold_hours, r.promotion_score,
                   r.rank, r.status,
                   b.name as bot_name
            FROM research_scores r
            JOIN bots b ON b.id = r.bot_id
            WHERE r.status = 'active'
            ORDER BY r.promotion_score DESC NULLS LAST
        """)
        return cur.fetchall()

# ═══════════════════════════════
# STANDBY ORDERS
# ═══════════════════════════════
def create_standby_order(position_id, bot_id,
                          wallet_id, standby_amount,
                          target_price, dca_level):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO standby_orders
            (position_id, bot_id, wallet_id,
             standby_amount, target_price, dca_level)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (position_id, bot_id, wallet_id,
              standby_amount, target_price, dca_level))
        return cur.fetchone()[0]

def get_active_standby_orders(exchange_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.position_id, s.standby_amount,
                   s.target_price, s.dca_level,
                   p.coin, p.bot_id, p.user_id
            FROM standby_orders s
            JOIN positions p ON p.id = s.position_id
            JOIN bots b ON b.id = p.bot_id
            WHERE s.status = 'active'
            AND b.exchange_id = %s
        """, (exchange_id,))
        return cur.fetchall()

def trigger_standby_order(standby_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE standby_orders
            SET status = 'triggered', triggered_at = NOW()
            WHERE id = %s
        """, (standby_id,))

def cancel_standby_order(standby_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE standby_orders
            SET status = 'cancelled', expired_at = NOW()
            WHERE id = %s
        """, (standby_id,))

# ═══════════════════════════════
# ADMIN
# ═══════════════════════════════
def get_platform_stats():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM users WHERE is_admin=FALSE) as total_users,
                (SELECT COUNT(*) FROM bots WHERE status='active') as active_bots,
                (SELECT COUNT(*) FROM positions WHERE status='open') as open_positions,
                (SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=FALSE) as live_positions,
                (SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=TRUE) as paper_positions,
                (SELECT COALESCE(SUM(balance_usdt),0) FROM reserve_wallets) as total_reserve,
                (SELECT accumulated_fees_usdt FROM owner_balance LIMIT 1) as owner_balance,
                (SELECT COUNT(*) FROM trades WHERE DATE(timestamp)=CURRENT_DATE) as trades_today
        """)
        return cur.fetchone()

def get_all_users_admin():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.email, u.created_at,
                   u.is_suspended, u.telegram_verified,
                   COUNT(DISTINCT b.id) as bot_count,
                   COUNT(DISTINCT p.id) as open_positions,
                   COALESCE(r.balance_usdt, 0) as reserve_balance,
                   COALESCE(SUM(fd.amount_usdt) FILTER
                       (WHERE fd.paid_at IS NULL), 0) as fee_debt
            FROM users u
            LEFT JOIN bots b ON b.user_id = u.id
                AND b.status = 'active'
            LEFT JOIN positions p ON p.user_id = u.id
                AND p.status = 'open'
            LEFT JOIN reserve_wallets r ON r.user_id = u.id
            LEFT JOIN fee_debt fd ON fd.user_id = u.id
            WHERE u.is_admin = FALSE
            GROUP BY u.id, u.email, u.created_at,
                     u.is_suspended, u.telegram_verified,
                     r.balance_usdt
            ORDER BY open_positions DESC
        """)
        return cur.fetchall()

# ═══════════════════════════════
# SECURITY AUDIT LOG
# ═══════════════════════════════
def log_security_event(user_id, event_type, ip_address=None,
                        user_agent=None, details=None):
    import json
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO security_audit_log
            (user_id, event_type, ip_address, user_agent, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, event_type, ip_address, user_agent,
              json.dumps(details) if details else None))

def get_security_logs(user_id=None, limit=100):
    with get_db() as conn:
        cur = conn.cursor()
        if user_id:
            cur.execute("""
                SELECT id, user_id, event_type, ip_address,
                       details, created_at
                FROM security_audit_log
                WHERE user_id = %s
                ORDER BY created_at DESC LIMIT %s
            """, (user_id, limit))
        else:
            cur.execute("""
                SELECT id, user_id, event_type, ip_address,
                       details, created_at
                FROM security_audit_log
                ORDER BY created_at DESC LIMIT %s
            """, (limit,))
        return cur.fetchall()

# ═══════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════
def create_verification_code(user_id):
    import random
    code = str(random.randint(100000, 999999))
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET
                verification_code = %s,
                verification_expires_at = NOW() + INTERVAL '15 minutes'
            WHERE id = %s
        """, (code, user_id))
    return code

def verify_code(user_id, code):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT verification_code, verification_expires_at
            FROM users WHERE id = %s
        """, (user_id,))
        row = cur.fetchone()
        if not row:
            return False
        stored_code, expires_at = row
        if stored_code != code:
            return False
        from datetime import datetime, timezone
        if expires_at < datetime.now(timezone.utc):
            return False
        # Mark as verified
        cur.execute("""
            UPDATE users SET
                last_verified_at = NOW(),
                verification_code = NULL,
                verification_expires_at = NULL,
                email_verified = TRUE
            WHERE id = %s
        """, (user_id,))
        return True

def write_market_regime(date, regime, btc_24h, btc_7d, volatility):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO market_regimes
                (date, regime, btc_24h_change, btc_7d_change, market_volatility)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE SET
                regime = EXCLUDED.regime,
                btc_24h_change = EXCLUDED.btc_24h_change,
                btc_7d_change = EXCLUDED.btc_7d_change,
                market_volatility = EXCLUDED.market_volatility
        """, (date, regime, btc_24h, btc_7d, volatility))
        conn.commit()

def get_market_regime(date=None):
    with get_db() as conn:
        cur = conn.cursor()
        if date:
            cur.execute("""
                SELECT date, regime, btc_7d_change, market_volatility
                FROM market_regimes WHERE date = %s
            """, (date,))
        else:
            cur.execute("""
                SELECT date, regime, btc_7d_change, market_volatility
                FROM market_regimes ORDER BY date DESC LIMIT 1
            """)
        return cur.fetchone()

def get_regime_history(days=180):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT date, regime FROM market_regimes
            ORDER BY date DESC LIMIT %s
        """, (days,))
        return cur.fetchall()

def regenerate_verification_code(user_id):
   """Generate new 6-digit code · invalidate old one · track resend count"""
   import random
   code = str(random.randint(100000, 999999))
   with get_db() as conn:
       cur = conn.cursor()
       # Check resend count in last hour
       cur.execute("""
           SELECT resend_count, resend_reset_at
           FROM users WHERE id = %s
       """, (user_id,))
       row = cur.fetchone()
       if row:
           count = row[0] or 0
           reset_at = row[1]
           from datetime import datetime, timezone
           now = datetime.now(timezone.utc)
           # Reset count if more than 1 hour passed
           if reset_at and (now - reset_at.replace(tzinfo=timezone.utc)).seconds > 3600:
               count = 0
           if count >= 5:
               return None, 'too_many_attempts'
       # Update code and increment resend count
       cur.execute("""
           UPDATE users SET
               verification_code = %s,
               verification_expires_at = NOW() + INTERVAL '30 minutes',
               resend_count = COALESCE(resend_count, 0) + 1,
               resend_reset_at = CASE
                   WHEN resend_reset_at IS NULL
                   OR NOW() - resend_reset_at > INTERVAL '1 hour'
                   THEN NOW() ELSE resend_reset_at END,
               last_resend_at = NOW()
           WHERE id = %s
           RETURNING verification_code
       """, (code, user_id))
       conn.commit()
       return code, 'ok'

def get_last_resend_time(user_id):
   """Get when last resend was sent"""
   with get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           SELECT last_resend_at, resend_count
           FROM users WHERE id = %s
       """, (user_id,))
       return cur.fetchone()

def get_btc_7d_change():
    """Get BTC 7-day price change percentage"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                ((SELECT close FROM ohlcv_hourly
                  WHERE coin = 'BTC' ORDER BY timestamp DESC LIMIT 1) -
                 (SELECT close FROM ohlcv_hourly
                  WHERE coin = 'BTC'
                  AND timestamp <= NOW() - INTERVAL '7 days'
                  ORDER BY timestamp DESC LIMIT 1)) /
                NULLIF((SELECT close FROM ohlcv_hourly
                  WHERE coin = 'BTC'
                  AND timestamp <= NOW() - INTERVAL '7 days'
                  ORDER BY timestamp DESC LIMIT 1), 0) * 100
        """)
        row = cur.fetchone()
        return float(row[0] or 0) if row else 0.0

def get_btc_24h_change():
    """Get BTC 24-hour price change percentage"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                ((SELECT close FROM ohlcv_hourly
                  WHERE coin = 'BTC' ORDER BY timestamp DESC LIMIT 1) -
                 (SELECT close FROM ohlcv_hourly
                  WHERE coin = 'BTC'
                  AND timestamp <= NOW() - INTERVAL '24 hours'
                  ORDER BY timestamp DESC LIMIT 1)) /
                NULLIF((SELECT close FROM ohlcv_hourly
                  WHERE coin = 'BTC'
                  AND timestamp <= NOW() - INTERVAL '24 hours'
                  ORDER BY timestamp DESC LIMIT 1), 0) * 100
        """)
        row = cur.fetchone()
        return float(row[0] or 0) if row else 0.0

def get_market_volatility():
    """Get market volatility from BTC ATR as percentage"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT atr_14 / NULLIF(close, 0) * 100
            FROM ohlcv_hourly
            WHERE coin = 'BTC'
            ORDER BY timestamp DESC LIMIT 1
        """)
        row = cur.fetchone()
        return float(row[0] or 0) if row else 0.0
