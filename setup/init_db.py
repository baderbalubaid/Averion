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
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"

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
        'wallet_transactions'
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

if __name__ == '__main__':
    main()
