import psycopg2
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'averion'),
    'user': os.getenv('DB_USER', 'averion'),
    'password': os.getenv('DB_PASSWORD')
}

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import telegram as tg

def send_telegram(msg):
    tg.send_admin(msg)

def aggregate_daily(conn):
    cur = conn.cursor()
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    # Positions closed yesterday
    cur.execute("""
        SELECT COUNT(*), 
               COALESCE(SUM(total_invested), 0)
        FROM positions
        WHERE status = 'closed'
        AND DATE(closed_at) = %s
    """, (yesterday,))
    closed_count, total_invested = cur.fetchone()

    # Open positions count
    cur.execute("SELECT COUNT(*) FROM positions WHERE status = 'open'")
    open_count = cur.fetchone()[0]

    # Paper vs live
    cur.execute("SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=TRUE")
    paper_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=FALSE")
    live_count = cur.fetchone()[0]

    # Active bots
    cur.execute("SELECT COUNT(*) FROM bots WHERE status='active'")
    bot_count = cur.fetchone()[0]

    # Fee debt outstanding
    cur.execute("SELECT COALESCE(SUM(amount_usdt),0) FROM fee_debt WHERE paid_at IS NULL")
    outstanding_debt = float(cur.fetchone()[0])

    # Owner balance
    cur.execute("SELECT accumulated_fees_usdt FROM owner_balance LIMIT 1")
    owner_balance = float(cur.fetchone()[0])

    conn.commit()

    return {
        'date': str(yesterday),
        'closed_yesterday': closed_count,
        'total_invested_closed': float(total_invested),
        'open_positions': open_count,
        'paper_open': paper_count,
        'live_open': live_count,
        'active_bots': bot_count,
        'outstanding_debt': outstanding_debt,
        'owner_balance': owner_balance
    }

def send_daily_report(data):
    msg = f"""📊 <b>Averion Daily Report — {data['date']}</b>

<b>Positions:</b>
• Open total: {data['open_positions']}
• Live: {data['live_open']} | Paper: {data['paper_open']}
• Closed yesterday: {data['closed_yesterday']}

<b>Platform:</b>
• Active bots: {data['active_bots']}
• Outstanding fees: ${data['outstanding_debt']:.2f}
• Owner balance: ${data['owner_balance']:.2f}

✅ Daily aggregation complete"""

    send_telegram(msg)
    print(msg)

def cleanup_old_data(conn):
    cur = conn.cursor()

    # Archive positions closed > 1 year ago
    cutoff = datetime.utcnow() - timedelta(days=365)
    cur.execute("""
        UPDATE positions SET status = 'archived'
        WHERE status = 'closed'
        AND closed_at < %s
    """, (cutoff,))
    archived = cur.rowcount

    # Clean old logs
    log_cutoff = datetime.utcnow() - timedelta(days=30)
    print(f"🗄️ Archived {archived} old positions")

    conn.commit()

def main():
    print(f"🔄 Daily aggregation started: {datetime.utcnow()}")
    conn = psycopg2.connect(**DB_CONFIG)

    data = aggregate_daily(conn)
    send_daily_report(data)
    cleanup_old_data(conn)

    conn.close()
    print(f"✅ Daily aggregation complete: {datetime.utcnow()}")

if __name__ == '__main__':
    main()
