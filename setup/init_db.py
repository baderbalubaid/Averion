import bcrypt
import psycopg2
import os
import hashlib
import secrets
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

def hash_password(password):
    salt = secrets.token_hex(16)
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def main():
    print("🚀 Initializing Averion Database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # ═══════════════════════════
    # Create Admin User
    # ═══════════════════════════
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@averionbot.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123')
    admin_hash = hash_password(admin_password)

    cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
    if cur.fetchone():
        print(f"⏭️  Admin user already exists: {admin_email}")
    else:
        cur.execute("""
            INSERT INTO users (
                email, password_hash, is_admin,
                is_zero_fee, created_at
            ) VALUES (%s, %s, TRUE, TRUE, %s)
        """, (admin_email, admin_hash, datetime.utcnow()))
        print(f"✅ Admin user created: {admin_email}")

    # ═══════════════════════════
    # Create Owner Balance Record
    # ═══════════════════════════
    cur.execute("SELECT id FROM owner_balance LIMIT 1")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO owner_balance
            (accumulated_fees_usdt, total_transferred)
            VALUES (0, 0)
        """)
        print("✅ Owner balance record created")
    else:
        print("⏭️  Owner balance already exists")

    # ═══════════════════════════
    # Verify All Tables Exist
    # ═══════════════════════════
    tables = [
        'users', 'exchanges', 'virtual_wallets', 'bots',
        'positions', 'trades', 'standby_orders',
        'reserve_wallets', 'reserve_deposits', 'fee_debt',
        'balance_history', 'coin_history', 'ohlcv_hourly',
        'owner_balance', 'referrals', 'wallet_bot_assignments',
        'wallet_transactions', 'user_telegram', 'attention_log',
        'system_settings',
        'research_virtual_balances',
        'smart_dca_champions',
        'rate_limits',
        'schema_migrations',
        'notification_queue', 'positions_archive',
        'strategy_versions', 'research_scores',
        'user_subscriptions', 'subscription_billing',
        'exchange_coin_limits', 'short_buyback_orders',
        'trade_bundles', 'pending_limit_orders',
        'security_audit_log', 'market_regimes',
        'performance_timing', 'system_health',
        'bot_events', 'bot_mirrors', 'exchange_mirrors'
    ]

    print("\n📋 Verifying tables:")
    all_good = True
    for table in tables:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """, (table,))
        exists = cur.fetchone()[0]
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
        if not exists:
            all_good = False

    conn.commit()
    conn.close()

    print()
    if all_good:
        print("🎉 Database initialized successfully!")
        print(f"   Admin: {admin_email}")
        print(f"   Password: {admin_password}")
        print("   ⚠️  Change password after first login!")
    else:
        print("❌ Some tables missing — run schema.sql first:")
        print("   psql -U averion -d averion -h localhost < setup/schema.sql")


def create_research_account():
    """Create the research account for automated bots"""
    import psycopg2
    research_email = 'research@averionbot.com'
    research_password = os.getenv('RESEARCH_ACCOUNT_PASSWORD', 'research_secure_pass_change_me')
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check if already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (research_email,))
        if cur.fetchone():
            print("✅ Research account already exists")
            conn.close()
            return
        
        # Create research account
        hashed = hash_password(research_password)
        cur.execute("""
            INSERT INTO users (username, email, password_hash, 
                             is_research_account, email_verified, created_at)
            VALUES (%s, %s, %s, TRUE, TRUE, NOW())
        """, ('research_bot', research_email, hashed))
        
        conn.commit()
        conn.close()
        print(f"✅ Research account created: {research_email}")
        
    except Exception as e:
        print(f"❌ Research account error: {e}")


if __name__ == '__main__':
    main()

# Create research account for automated research bots
def create_research_account():
    research_email = 'research@averionbot.com'
    research_password = os.getenv('RESEARCH_ACCOUNT_PASSWORD', 'change-me-on-day1')
    
    conn = psycopg2.connect(**DB_CONFIG)
conn.autocommit = False
try:
    if True:  # was: with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (research_email,))
        if cur.fetchone():
            print('✅ Research account already exists')
            return
        
        import bcrypt
        pw_hash = bcrypt.hashpw(research_password.encode(), bcrypt.gensalt()).decode()
        cur.execute("""
            INSERT INTO users (email, password_hash, is_admin, is_zero_fee, email_verified)
            VALUES (%s, %s, TRUE, TRUE, TRUE)
        """, (research_email, pw_hash))
        conn.commit()
        print('✅ Research account created: research@averionbot.com')

create_research_account()
