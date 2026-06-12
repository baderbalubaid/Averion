"""
save_scalper_snapshot.py
Saves daily P&L snapshot for top 20 scalper bots at 8pm Saudi (5pm UTC).
Run via cron: 0 17 * * * python3 /home/averion/Averion/save_scalper_snapshot.py
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from datetime import datetime, timezone, timedelta
db.init_pool()

def get_top20_scalper_score():
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, b.name,
                COALESCE(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed'), 0) as total_pnl,
                COUNT(*) FILTER (WHERE s.status='closed') as trades,
                COALESCE(SUM(CASE WHEN s.pnl_usdt > 0 THEN s.pnl_usdt ELSE 0 END) FILTER (WHERE s.status='closed'), 0) as gross_win,
                COALESCE(SUM(ABS(s.pnl_usdt)) FILTER (WHERE s.status='closed' AND s.pnl_usdt <= 0), 0) as gross_loss,
                array_agg(s.pnl_usdt ORDER BY s.pnl_usdt DESC) FILTER (WHERE s.status='closed') as all_pnls
            FROM bots b
            LEFT JOIN scalper_positions s ON s.bot_id=b.id
            WHERE b.method='E58'
            GROUP BY b.id, b.name
            HAVING COUNT(*) FILTER (WHERE s.status='closed') > 0
        """)
        rows = cur.fetchall()

    scored = []
    for r in rows:
        bot_id, name, total_pnl, trades, gross_win, gross_loss, all_pnls = r
        total_pnl = float(total_pnl or 0)
        gross_win = float(gross_win or 0)
        gross_loss = float(gross_loss or 0)
        pnls = [float(x) for x in (all_pnls or [])]
        excl5 = sum(pnls[5:]) if len(pnls) > 5 else total_pnl
        pf = gross_win/gross_loss if gross_loss > 0 else gross_win
        score = total_pnl*0.4 + excl5*0.3 + pf*0.2 + (trades or 0)*0.1
        scored.append({'id': bot_id, 'name': name, 'score': score, 'total_pnl': total_pnl})

    scored.sort(key=lambda x: -x['score'])
    return scored[:20]

def save_snapshot():
    # Saudi time = UTC+3, snapshot at 8pm Saudi = 5pm UTC
    saudi_now = datetime.now(timezone.utc) + timedelta(hours=3)
    today = saudi_now.date()

    top20 = get_top20_scalper_score()

    with db.get_db() as conn:
        cur = conn.cursor()
        saved = 0
        for bot in top20:
            cur.execute("""
                INSERT INTO scalper_daily_snapshots 
                    (snapshot_date, bot_id, bot_name, cumulative_pnl)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (snapshot_date, bot_id) 
                DO UPDATE SET cumulative_pnl = EXCLUDED.cumulative_pnl,
                              created_at = NOW()
            """, (today, bot['id'], bot['name'], round(bot['total_pnl'], 2)))
            saved += 1
        conn.commit()

    print(f'✅ Snapshot saved · {today} · {saved} bots')
    for b in top20[:5]:
        print(f'   {b["name"]}: ${b["total_pnl"]:.2f}')

if __name__ == '__main__':
    save_snapshot()
