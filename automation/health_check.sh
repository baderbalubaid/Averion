#!/bin/bash
# Averion Health Check — runs every hour via cron
# Records system health to DB and generates diagnostics

AVERION_DIR=/home/averion/Averion
LOG_DIR=/var/log/averion

# Get system metrics
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
CPU=${CPU%.*}
RAM=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
DISK=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
REDIS_MB=$(redis-cli info memory 2>/dev/null | grep used_memory_human | cut -d: -f2 | tr -d 'K\r' | awk '{printf "%.2f", $1/1024}')
PG_CONN=$(psql -U averion -h localhost -d averion -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ')
CYCLE_TIME=$(redis-cli get bot:cycle_time 2>/dev/null || echo "0")
ACTIVE_BOTS=$(psql -U averion -h localhost -d averion -t -c "SELECT count(*) FROM bots WHERE status='active';" 2>/dev/null | tr -d ' ')
OPEN_POS=$(psql -U averion -h localhost -d averion -t -c "SELECT count(*) FROM positions WHERE status='open';" 2>/dev/null | tr -d ' ')

# Record to DB
psql -U averion -h localhost -d averion << SQL
INSERT INTO system_health
(cpu_percent, ram_percent, disk_percent, redis_mb,
 pg_connections, bot_cycle_time, active_bots,
 open_positions, recorded_at)
VALUES
($CPU, $RAM, $DISK, ${REDIS_MB:-0},
 ${PG_CONN:-0}, ${CYCLE_TIME:-0}, ${ACTIVE_BOTS:-0},
 ${OPEN_POS:-0}, NOW());

-- Delete records older than 30 days
DELETE FROM system_health
WHERE recorded_at < NOW() - INTERVAL '30 days';
SQL

# Send Telegram alerts if thresholds crossed
BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN $AVERION_DIR/.env | cut -d'=' -f2)
CHAT_ID=$(grep TELEGRAM_ADMIN_CHAT_ID $AVERION_DIR/.env | cut -d'=' -f2)

send_alert() {
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d chat_id="$CHAT_ID" \
        -d text="$1" > /dev/null
}

[ "$CPU" -gt 80 ] && send_alert "🔴 Averion: CPU high ${CPU}%"
[ "$RAM" -gt 80 ] && send_alert "🔴 Averion: RAM high ${RAM}%"
[ "$DISK" -gt 70 ] && send_alert "⚠️ Averion: Disk high ${DISK}%"

# Check PM2 bot status
PM2_STATUS=$(pm2 jlist 2>/dev/null | python3 -c "
import sys,json
try:
    procs=json.load(sys.stdin)
    running=[p for p in procs if p['name']=='averion' and p['pm2_env']['status']=='online']
    print('online' if running else 'offline')
except:
    print('unknown')
" 2>/dev/null)

if [ "$PM2_STATUS" != "online" ]; then
    send_alert "🔴 Averion CRITICAL: Bot offline · restarting..."
    pm2 restart averion
    # Log bot crash event
    psql -U averion -h localhost -d averion << SQL
INSERT INTO bot_events
(event_type, error_message, recorded_at)
VALUES ('crash', 'PM2 bot was offline · auto-restarted', NOW());
SQL
fi

# Generate diagnostics report
python3 $AVERION_DIR/automation/generate_diagnostics.py >> $LOG_DIR/diagnostics.log 2>&1

echo "Health check complete: CPU=${CPU}% RAM=${RAM}% Disk=${DISK}% Bot=${PM2_STATUS}"
