#!/usr/bin/env python3
"""90-day paper trade auto-close if no live trades"""
import sys
sys.path.insert(0, '/home/averion/Averion')
import database as db
import telegram as tg
from datetime import datetime, timezone

def check_paper_timer():
    with db.get_db() as conn:
        cur = conn.cursor()
        # Find users with paper trades but no live trade in 90 days
        cur.execute("""
            SELECT DISTINCT u.id, u.email,
                MAX(p.opened_at) as last_paper_open,
                (SELECT MAX(p2.opened_at) FROM positions p2
                 WHERE p2.user_id = u.id AND p2.is_paper = FALSE) as last_live_open
            FROM users u
            JOIN positions p ON p.user_id = u.id
            WHERE p.is_paper = TRUE AND p.status = 'open'
            AND u.is_admin = FALSE
            GROUP BY u.id, u.email
        """)
        users = cur.fetchall()

        for user in users:
            user_id, email, last_paper, last_live = user
            now = datetime.now(timezone.utc)

            # Check if no live trade in 90 days
            days_since_live = 999
            if last_live:
                days_since_live = (now - last_live.replace(tzinfo=timezone.utc)).days

            if days_since_live >= 90:
                print(f'Auto-closing paper trades for user {user_id} ({days_since_live} days no live trade)')
                cur.execute("""
                    UPDATE positions SET status = 'closed', closed_at = NOW()
                    WHERE user_id = %s AND is_paper = TRUE AND status = 'open'
                """, (user_id,))
                conn.commit()
                tg.send_admin(f'📄 Paper trades auto-closed: user {user_id} · {days_since_live} days no live trade')
            elif days_since_live >= 83:
                tg.send_user(user_id, f'⚠️ Warning: No live trades for {days_since_live} days · Paper trades auto-close at Day 90')

if __name__ == '__main__':
    check_paper_timer()
