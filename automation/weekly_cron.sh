#!/bin/bash
# Averion Weekly Cron — runs Sunday 4am
LOG="/home/trader/Averion/logs/weekly_$(date +%Y%m%d).log"
mkdir -p /home/trader/Averion/logs

echo "=== Averion Weekly Cron $(date) ===" >> $LOG

# 1. Clean old logs (keep 30 days)
echo "[1/4] Cleaning logs..." >> $LOG
find /home/trader/Averion/logs -name "*.log" -mtime +30 -delete
echo "Logs cleaned ✅" >> $LOG

# 2. Disk check
echo "[2/4] Disk check..." >> $LOG
DISK=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
echo "Disk usage: ${DISK}%" >> $LOG
if [ "$DISK" -gt 70 ]; then
    echo "⚠️ WARNING: Disk above 70%" >> $LOG
fi

# 3. DB optimization
echo "[3/4] Optimizing database..." >> $LOG
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/trader/Averion/averion.db')
conn.execute('VACUUM')
conn.execute('ANALYZE')
conn.close()
print('DB optimized')
" >> $LOG 2>&1
echo "Database optimized ✅" >> $LOG

# 4. Save weekly metrics
echo "[4/4] Weekly metrics..." >> $LOG
OPEN_TRADES=$(python3 -c "
import sqlite3
conn = sqlite3.connect('/home/trader/Averion/averion.db')
count = conn.execute(\"SELECT COUNT(*) FROM positions WHERE status='open'\").fetchone()[0]
conn.close()
print(count)
" 2>/dev/null || echo "0")
TOTAL_TRADES=$(python3 -c "
import sqlite3
conn = sqlite3.connect('/home/trader/Averion/averion.db')
count = conn.execute(\"SELECT COUNT(*) FROM trades\").fetchone()[0]
conn.close()
print(count)
" 2>/dev/null || echo "0")
echo "Open trades: ${OPEN_TRADES} | Total trades: ${TOTAL_TRADES}" >> $LOG

echo "=== Weekly cron complete $(date) ===" >> $LOG
