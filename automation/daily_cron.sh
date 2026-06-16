#!/bin/bash
# Averion Daily Cron — runs at 03:00 daily
# Schedule: 03:00 Infrastructure · 03:30 Classify · 04:00 Params · 04:30 Reporting · 05:00 Sunday Cleanup

set -e
AVERION_DIR=/home/averion/Averion
LOG_DIR=/var/log/averion
mkdir -p $LOG_DIR $AVERION_DIR/backups

echo "=== Averion Daily Cron $(date) ===" | tee -a $LOG_DIR/daily.log

# ═══════════════════════════════
# 03:00 — INFRASTRUCTURE
# ═══════════════════════════════
echo "--- 03:00 Infrastructure ---" | tee -a $LOG_DIR/daily.log

# DB backup
BACKUP_FILE=$AVERION_DIR/backups/averion_$(date +%Y%m%d).sql
pg_dump -U averion -h localhost averion > $BACKUP_FILE
echo "✅ Backup: $BACKUP_FILE" | tee -a $LOG_DIR/daily.log

# Delete backups older than 7 days
find $AVERION_DIR/backups -name "*.sql" -mtime +7 -delete

# Record system health
python3 -c "
import sys; sys.path.insert(0, '$AVERION_DIR')
from dotenv import load_dotenv; load_dotenv()
import database as db, psutil, redis
db.init_pool()
r = redis.Redis(host='localhost', port=6379)
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage('/').percent
db.record_system_health(cpu, ram, disk, 0, 0, 0, 0, 0)
print(f'Health: CPU={cpu}% RAM={ram}% Disk={disk}%')
" >> $LOG_DIR/daily.log 2>&1

echo "✅ Infrastructure complete" | tee -a $LOG_DIR/daily.log
sleep 1800

# ═══════════════════════════════
# 03:30 — COIN CLASSIFICATION
# ═══════════════════════════════
echo "--- 03:30 Classification ---" | tee -a $LOG_DIR/classify.log
python3 $AVERION_DIR/classify_coins.py >> $LOG_DIR/classify.log 2>&1
echo "✅ Classification complete $(date)" | tee -a $LOG_DIR/classify.log
sleep 1800

# ═══════════════════════════════
# 04:00 — CALCULATE COIN PARAMS
# ═══════════════════════════════
echo "--- 04:00 Calculate Parameters ---" | tee -a $LOG_DIR/params.log
python3 $AVERION_DIR/calculate_coin_params.py >> $LOG_DIR/params.log 2>&1
echo "✅ Parameters calculated $(date)" | tee -a $LOG_DIR/params.log
sleep 1800

# ═══════════════════════════════
# 04:30 — RARS SCORING
# ═══════════════════════════════
echo "--- 04:30 RARS Scoring ---" | tee -a $LOG_DIR/rars.log
python3 $AVERION_DIR/rars_scoring.py >> $LOG_DIR/rars.log 2>&1
echo "✅ RARS scoring complete $(date)" | tee -a $LOG_DIR/rars.log
sleep 1800

# ═══════════════════════════════
# 05:00 — PAPER TIMER CHECK
# ═══════════════════════════════
echo "--- 05:00 Paper Timer ---" | tee -a $LOG_DIR/paper_timer.log
python3 $AVERION_DIR/automation/check_paper_timer.py >> $LOG_DIR/paper_timer.log 2>&1
echo "✅ Paper timer checked" | tee -a $LOG_DIR/paper_timer.log

# ═══════════════════════════════
# SUNDAY CLEANUP
# ═══════════════════════════════
if [ "$(date +%u)" = "7" ]; then
    echo "--- Sunday Cleanup ---" | tee -a $LOG_DIR/cleanup.log
    psql -U averion -h localhost averion -c "VACUUM ANALYZE;" >> $LOG_DIR/cleanup.log 2>&1
    find $LOG_DIR -name "*.log" -mtime +30 -delete
    DISK=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [ "$DISK" -gt 70 ]; then
        echo "⚠️ Disk usage high: ${DISK}%" | tee -a $LOG_DIR/cleanup.log
    fi
    echo "✅ Sunday cleanup complete" | tee -a $LOG_DIR/cleanup.log
fi

# ═══════════════════════════════
# RESEARCH REPORT GENERATION
# ═══════════════════════════════
echo "--- Research Reports ---" | tee -a $LOG_DIR/daily.log
bash $AVERION_DIR/generate_reports.sh >> $LOG_DIR/daily.log 2>&1
echo "✅ Research reports generated" | tee -a $LOG_DIR/daily.log

# ═══════════════════════════════
# DAILY TELEGRAM REPORT
# ═══════════════════════════════
echo "--- Telegram Daily Report ---" | tee -a $LOG_DIR/daily.log
python3 -c "
import sys; sys.path.insert(0, '$AVERION_DIR')
from dotenv import load_dotenv; load_dotenv()
import database as db, telegram as tg
db.init_pool()
from datetime import datetime, timedelta
with db.get_db() as conn:
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*),
               COALESCE(SUM(total_sold_usdt - total_invested), 0)
        FROM positions
        WHERE status='closed'
        AND closed_at > NOW() - INTERVAL '24 hours'
    """)
    closed_today, profit_today = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM positions WHERE status='open'")
    open_pos = cur.fetchone()[0]

tg.send_admin(f'''📊 <b>Averion Daily Report</b>
{datetime.utcnow().strftime('%B %d, %Y')}

Closed today: {closed_today}
Profit today: \${float(profit_today):.2f}
Open positions: {open_pos:,}

Research: {open_pos:,} open · data collecting
Generated at: {datetime.utcnow().strftime('%H:%M UTC')}''')
print('✅ Telegram daily report sent')
" >> $LOG_DIR/daily.log 2>&1

echo "=== Daily Cron Complete $(date) ===" | tee -a $LOG_DIR/daily.log

# Fetch BTC daily candle for SMA50
python3 /home/averion/Averion/fetch_btc_daily.py
