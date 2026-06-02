#!/bin/bash
# Averion Daily Cron
# Schedule:
# 03:00 Infrastructure
# 03:30 CoinGecko Fetch
# 04:00 CoinMarketCap Fetch
# 04:30 Classification
# 05:00 Reporting
# 05:30 Sunday Cleanup

set -e
AVERION_DIR=/home/averion/Averion
LOG_DIR=/var/log/averion
mkdir -p $LOG_DIR

echo "=== Averion Daily Cron $(date) ===" | tee -a $LOG_DIR/daily.log

# ═══════════════════════════════
# 03:00 — INFRASTRUCTURE
# ═══════════════════════════════
echo "--- 03:00 Infrastructure ---" | tee -a $LOG_DIR/daily.log

# Restart bot
pm2 restart averion >> $LOG_DIR/daily.log 2>&1
echo "✅ Bot restarted" | tee -a $LOG_DIR/daily.log

# PostgreSQL backup
BACKUP_FILE=/home/averion/backups/averion_$(date +%Y%m%d).sql
pg_dump -U averion -h localhost averion > $BACKUP_FILE
echo "✅ Backup saved: $BACKUP_FILE" | tee -a $LOG_DIR/daily.log

# Delete backups older than 7 days
find /home/averion/backups -name "*.sql" -mtime +7 -delete
echo "✅ Old backups cleaned" | tee -a $LOG_DIR/daily.log

# CCXT safe upgrade
cd $AVERION_DIR
CURRENT=$(python3 -c "import ccxt; print(ccxt.__version__)")
pip install ccxt --upgrade --break-system-packages --quiet
NEW=$(python3 -c "import ccxt; print(ccxt.__version__)")
if [ "$CURRENT" != "$NEW" ]; then
    echo "✅ CCXT upgraded: $CURRENT → $NEW" | tee -a $LOG_DIR/daily.log
else
    echo "✅ CCXT up to date: $CURRENT" | tee -a $LOG_DIR/daily.log
fi

echo "✅ Infrastructure complete $(date)" | tee -a $LOG_DIR/daily.log
sleep 1800  # Wait until 03:30

# ═══════════════════════════════
# 03:30 — COINGECKO FETCH
# ═══════════════════════════════
echo "--- 03:30 CoinGecko Fetch ---" | tee -a $LOG_DIR/coingecko.log
python3 $AVERION_DIR/automation/fetch_coingecko.py >> $LOG_DIR/coingecko.log 2>&1
echo "✅ CoinGecko fetch complete $(date)" | tee -a $LOG_DIR/coingecko.log
sleep 1800  # Wait until 04:00

# ═══════════════════════════════
# 04:00 — COINMARKETCAP FETCH
# ═══════════════════════════════
echo "--- 04:00 CoinMarketCap Fetch ---" | tee -a $LOG_DIR/cmc.log
python3 $AVERION_DIR/automation/fetch_cmc.py >> $LOG_DIR/cmc.log 2>&1
echo "✅ CMC fetch complete $(date)" | tee -a $LOG_DIR/cmc.log
sleep 1800  # Wait until 04:30

# ═══════════════════════════════
# 04:30 — CLASSIFICATION
# ═══════════════════════════════
echo "--- 04:30 Classification ---" | tee -a $LOG_DIR/classify.log
python3 $AVERION_DIR/automation/classify_coins.py >> $LOG_DIR/classify.log 2>&1
echo "✅ Classification complete $(date)" | tee -a $LOG_DIR/classify.log
sleep 1800  # Wait until 05:00

# ═══════════════════════════════
# 05:00 — REPORTING
# ═══════════════════════════════
echo "--- 05:00 Reporting ---" | tee -a $LOG_DIR/reporting.log
python3 $AVERION_DIR/automation/daily_aggregation.py >> $LOG_DIR/reporting.log 2>&1
python3 $AVERION_DIR/automation/generate_metrics.py >> $LOG_DIR/reporting.log 2>&1
python3 $AVERION_DIR/automation/generate_excel.py >> $LOG_DIR/reporting.log 2>&1
echo "✅ Reporting complete $(date)" | tee -a $LOG_DIR/reporting.log

# ═══════════════════════════════
# 05:30 — SUNDAY CLEANUP
# ═══════════════════════════════
if [ "$(date +%u)" = "7" ]; then
    sleep 1800  # Wait until 05:30
    echo "--- 05:30 Sunday Cleanup ---" | tee -a $LOG_DIR/cleanup.log
    python3 $AVERION_DIR/automation/weekly_cron.sh >> $LOG_DIR/cleanup.log 2>&1
    psql -U averion -h localhost averion -c "VACUUM ANALYZE;" >> $LOG_DIR/cleanup.log 2>&1
    find $LOG_DIR -name "*.log" -mtime +30 -delete
    find $AVERION_DIR/reports -name "*.xlsx" -mtime +30 -delete
    DISK=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [ "$DISK" -gt 70 ]; then
        echo "⚠️ Disk usage high: ${DISK}%" | tee -a $LOG_DIR/cleanup.log
    fi
    echo "✅ Sunday cleanup complete $(date)" | tee -a $LOG_DIR/cleanup.log
fi

echo "=== Daily Cron Complete $(date) ===" | tee -a $LOG_DIR/daily.log

# Check 90-day paper trade timer
python3 /home/averion/Averion/automation/check_paper_timer.py >> /var/log/averion/paper_timer.log 2>&1
