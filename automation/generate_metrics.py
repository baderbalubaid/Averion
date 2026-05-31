import psycopg2
import json
import os
import subprocess
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

def generate_metrics():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    today = datetime.utcnow().date()
    
    # Total open positions
    cur.execute("SELECT COUNT(*) FROM positions WHERE status = 'open'")
    open_positions = cur.fetchone()[0]

    # Total closed today
    cur.execute("""
        SELECT COUNT(*) FROM positions 
        WHERE status = 'closed' 
        AND DATE(closed_at) = %s
    """, (today,))
    closed_today = cur.fetchone()[0]

    # Total profit today
    cur.execute("""
        SELECT COALESCE(SUM(t.usdt_amount - p.total_invested), 0)
        FROM positions p
        JOIN trades t ON t.position_id = p.id
        WHERE p.status = 'closed'
        AND DATE(p.closed_at) = %s
        AND t.side = 'sell'
    """, (today,))
    profit_today = float(cur.fetchone()[0])

    # Total users
    cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = FALSE")
    total_users = cur.fetchone()[0]

    # Total bots
    cur.execute("SELECT COUNT(*) FROM bots WHERE status = 'active'")
    total_bots = cur.fetchone()[0]

    # Paper vs live
    cur.execute("SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=TRUE")
    paper_open = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM positions WHERE status='open' AND is_paper=FALSE")
    live_open = cur.fetchone()[0]

    # Fees collected today
    cur.execute("""
        SELECT COALESCE(SUM(amount_usdt), 0) FROM fee_debt
        WHERE DATE(paid_at) = %s
    """, (today,))
    fees_today = float(cur.fetchone()[0])

    conn.close()

    metrics = {
        'generated_at': datetime.utcnow().isoformat(),
        'date': str(today),
        'positions': {
            'open_total': open_positions,
            'open_paper': paper_open,
            'open_live': live_open,
            'closed_today': closed_today
        },
        'profit': {
            'today_usdt': round(profit_today, 2),
            'fees_today_usdt': round(fees_today, 2)
        },
        'platform': {
            'total_users': total_users,
            'active_bots': total_bots
        }
    }

    # Save locally
    os.makedirs('metrics', exist_ok=True)
    with open('metrics/latest.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ metrics/latest.json generated")

    # Push to GitHub
    try:
        subprocess.run(['git', 'add', 'metrics/latest.json'], check=True)
        subprocess.run(['git', 'commit', '-m', f'metrics: daily update {today}'], check=True)
        token = os.getenv('GITHUB_TOKEN')
        subprocess.run([
            'git', 'push',
            f'https://baderbalubaid:{token}@github.com/baderbalubaid/Averion.git',
            'main'
        ], check=True)
        print(f"✅ metrics pushed to GitHub")
    except Exception as e:
        print(f"⚠️ GitHub push failed: {e}")

if __name__ == '__main__':
    generate_metrics()
