#!/bin/bash
# Averion Daily Cron — runs at 3am staggered
# 03:00 Infrastructure
# 03:30 Data and Classification
# 04:00 Reporting

echo "=== Averion Daily Cron $(date) ==="
cd /home/averion/Averion

# 03:00 — Infrastructure
echo "--- 03:00 Infrastructure ---"
pm2 restart averion
sleep 5
pg_dump -U averion averion > /home/averion/backups/averion_$(date +%Y%m%d).sql
find /home/averion/backups -name "*.sql" -mtime +7 -delete
echo "✅ Infrastructure done"

# 03:30 — Data and Classification
echo "--- 03:30 Data ---"
sleep 1800
python3 /home/averion/Averion/automation/fetch_ohlcv.py
echo "✅ OHLCV fetched"

# 04:00 — Reporting
echo "--- 04:00 Reporting ---"
sleep 1800
python3 /home/averion/Averion/automation/daily_aggregation.py
python3 /home/averion/Averion/automation/generate_metrics.py
python3 /home/averion/Averion/automation/generate_excel.py
echo "✅ Reports generated"

echo "=== Daily Cron Complete $(date) ==="
