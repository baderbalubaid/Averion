import sqlite3
from datetime import datetime

def get_db():
    conn = sqlite3.connect('dcabot.db')
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
            opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_id INTEGER,
            side TEXT,
            price REAL,
            quantity REAL,
            usdt_amount REAL,
            reason TEXT,
            paper INTEGER DEFAULT 1,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database ready!")

if __name__ == "__main__":
    init_db()
