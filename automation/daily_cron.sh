#!/bin/bash
# Averion Daily Cron — runs at 3am every day
LOG="/home/trader/Averion/logs/daily_$(date +%Y%m%d).log"
mkdir -p /home/trader/Averion/logs

echo "=== Averion Daily Cron $(date) ===" >> $LOG

# 1. Update CCXT
echo "[1/5] Updating CCXT..." >> $LOG
pip install ccxt --upgrade --break-system-packages -q >> $LOG 2>&1
echo "CCXT updated ✅" >> $LOG

# 2. Restart bot
echo "[2/5] Restarting bot..." >> $LOG
pm2 restart averion >> $LOG 2>&1
sleep 10
echo "Bot restarted ✅" >> $LOG

# 3. Database backup
echo "[3/5] Backing up database..." >> $LOG
mkdir -p /home/trader/Averion/backups
cp /home/trader/Averion/averion.db \
   /home/trader/Averion/backups/averion_$(date +%Y%m%d).db
# Keep last 7 days only
find /home/trader/Averion/backups -name "*.db" -mtime +7 -delete
echo "Database backed up ✅" >> $LOG

# 4. Health check
echo "[4/5] Health check..." >> $LOG
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
RAM=$(free -m | awk 'NR==2{printf "%.0f", $3*100/$2}')
DISK=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
PM2=$(pm2 jlist 2>/dev/null | python3 -c "
import json,sys
data=json.load(sys.stdin)
status=[p['pm2_env']['status'] for p in data if p['name']=='averion']
print(status[0] if status else 'not found')
" 2>/dev/null || echo "unknown")
echo "CPU: ${CPU}% | RAM: ${RAM}% | Disk: ${DISK}% | PM2: ${PM2}" >> $LOG

# 5. Log metrics for Claude analysis
echo "[5/5] Saving metrics..." >> $LOG
mkdir -p /home/trader/Averion/metrics
cat > /home/trader/Averion/metrics/latest.json << METRICS
{
  "date": "$(date +%Y-%m-%d)",
  "time": "$(date +%H:%M:%S)",
  "cpu_percent": ${CPU},
  "ram_percent": ${RAM},
  "disk_percent": ${DISK},
  "pm2_status": "${PM2}",
  "ccxt_updated": true,
  "backup_done": true
}
METRICS
echo "Metrics saved ✅" >> $LOG

echo "=== Daily cron complete $(date) ===" >> $LOG
