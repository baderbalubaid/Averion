import psycopg2
import json
import os
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

def load_config():
    with open('setup/research_bots.json') as f:
        return json.load(f)

def get_admin_user(cur):
    cur.execute("SELECT id FROM users WHERE is_research_account = TRUE LIMIT 1")
    row = cur.fetchone()
    if not row:
        raise Exception("No admin user found. Create admin user first.")
    return row[0]

def get_exchange_id(cur, user_id):
    cur.execute("""
        SELECT id FROM exchanges 
        WHERE user_id = %s AND active = TRUE 
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    if not row:
        raise Exception("No active exchange found. Add exchange first.")
    return row[0]

def bot_exists(cur, bot_id):
    cur.execute("SELECT id FROM bots WHERE name LIKE %s", (f'%{bot_id}%',))
    return cur.fetchone() is not None

def create_benchmark_bot(cur, bench, user_id, exchange_id):
    if bot_exists(cur, bench['id']):
        print(f"⏭️  Skipping {bench['id']} — already exists")
        return

    cur.execute("""
        INSERT INTO bots (
            user_id, exchange_id, wallet_id, name, method,
            is_paper, status, max_trades, created_at
        ) VALUES (%s, %s, %s, %s, %s, TRUE, 'open', 10, %s)
    """, (
        user_id, exchange_id, None,
        bench['name'],
        bench['method'],
        datetime.utcnow()
    ))
    print(f"✅ Created benchmark: {bench['name']}")

def create_method_bot(cur, method_id, method_name, bot, user_id, exchange_id):
    bot_id = bot['id']
    bot_name = f"{method_id} — {method_name} — {bot_id}"

    if bot_exists(cur, bot_id):
        print(f"⏭️  Skipping {bot_id} — already exists")
        return

    params = json.dumps(bot)

    cur.execute("""
        INSERT INTO bots (
            user_id, exchange_id, wallet_id, name, method,
            is_paper, status, max_trades,
            dca_percent, spacing_multiplier,
            size_multiplier, take_profit_percent,
            created_at
        ) VALUES (%s, %s, %s, %s, %s, TRUE, 'open', 10,
                  7.0, 1.4, 1.5, 5.0, %s)
    """, (
        user_id, exchange_id, None,
        bot_name, method_id.lower(),
        datetime.utcnow()
    ))
    print(f"✅ Created: {bot_name}")

def main():
    print(f"🚀 Launching research bots — {datetime.utcnow()}")
    config = load_config()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    user_id = get_admin_user(cur)
    exchange_id = get_exchange_id(cur, user_id)

    print(f"👤 Admin user: {user_id}")
    print(f"📊 Exchange: {exchange_id}")
    print()

    # Create benchmark bots
    print("--- Creating 5 Benchmark Bots ---")
    for bench in config['benchmarks']:
        create_benchmark_bot(cur, bench, user_id, exchange_id)

    # Create method bots
    total = 0
    for method_id, method_data in config['methods'].items():
        print(f"\n--- Creating {method_id} bots ({method_data['name']}) ---")
        for bot in method_data['bots']:
            create_method_bot(
                cur, method_id,
                method_data['name'],
                bot, user_id, exchange_id
            )
            total += 1

    conn.commit()
    conn.close()

    print(f"\n🎉 Research bots launched!")
    print(f"✅ Benchmarks: 5")
    print(f"✅ Method bots: {total}")
    print(f"✅ Total: {total + 5}")
    print(f"\nNext: Monitor dashboard → scale trades gradually")
    print(f"Start: 10 trades/bot → 20 → 50 → 100 → 200")

if __name__ == '__main__':
    main()
