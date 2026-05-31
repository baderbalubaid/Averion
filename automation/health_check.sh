#!/bin/bash
# Averion Health Check — runs every hour via cron

BOT_TOKEN=$(grep TELEGRAM_BOT_TOKEN /home/averion/Averion/.env | cut -d'=' -f2)
CHAT_ID=$(grep TELEGRAM_ADMIN_CHAT_ID /home/averion/Averion/.env | cut -d'=' -f2)

send_alert() {
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d chat_id="$CHAT_ID" \
        -d text="$1" > /dev/null
}

# CPU Check
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
CPU=${CPU%.*}
if [ "$CPU" -gt 80 ]; then
    send_alert "⚠️ Averion Alert: CPU high ${CPU}%"
fi

# RAM Check
RAM=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$RAM" -gt 80 ]; then
    send_alert "⚠️ Averion Alert: RAM high ${RAM}%"
fi

# Disk Check
DISK=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
if [ "$DISK" -gt 70 ]; then
    send_alert "⚠️ Averion Alert: Disk high ${DISK}%"
fi

# PM2 Check
PM2_STATUS=$(pm2 jlist 2>/dev/null | python3 -c "import sys,json; procs=json.load(sys.stdin); running=[p for p in procs if p['name']=='averion' and p['pm2_env']['status']=='online']; print('online' if running else 'offline')" 2>/dev/null)
if [ "$PM2_STATUS" != "online" ]; then
    send_alert "🔴 Averion CRITICAL: Bot is offline! Attempting restart..."
    pm2 restart averion
fi

echo "Health check complete: CPU=${CPU}% RAM=${RAM}% Disk=${DISK}% Bot=${PM2_STATUS}"
