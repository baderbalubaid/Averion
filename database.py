import sqlite3

def get_db():
    conn = sqlite3.connect('averion.db')
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            avg_cost REAL,
            quantity REAL DEFAULT 0,
            total_invested REAL DEFAULT 0,
            dca_count INTEGER DEFAULT 0,
            last_buy_price REAL,
            opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            tp_armed INTEGER DEFAULT 0,
            queued INTEGER DEFAULT 0,
            peak_price REAL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_id INTEGER,
            coin TEXT,
            side TEXT,
            price REAL,
            quantity REAL,
            usdt_amount REAL,
            reason TEXT,
            paper INTEGER DEFAULT 1,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS balance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exchange TEXT DEFAULT 'mexc',
            value_usdt REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add new columns to existing positions table if not exist
    for col, definition in [
        ("tp_armed",   "INTEGER DEFAULT 0"),
        ("queued",     "INTEGER DEFAULT 0"),
        ("peak_price", "REAL"),
    ]:
        try:
            c.execute(f"ALTER TABLE positions ADD COLUMN {col} {definition}")
        except:
            pass

    # Add coin column to trades if not exist
    try:
        c.execute("ALTER TABLE trades ADD COLUMN coin TEXT")
    except:
        pass

    conn.commit()
    conn.close()
    print("Database ready!")

if __name__ == "__main__":
    init_db()
