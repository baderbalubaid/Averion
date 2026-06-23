#!/bin/bash
# Averion Daily Cron — runs at 03:00 daily
# Schedule: 03:00 Backup/Health -> 03:45 Classification -> 04:30 Params -> 05:15 RARS -> tail steps
#
# HARDENED June 17 2026 (see system map KNOWN BUGS FIXED section for full history):
# - PGPASSWORD sourced from .env (fixes 7-day silent outage from missing DB auth)
# - set -e removed, every step wrapped in run_step() which logs and ALWAYS continues
# - Telegram alert fires if any step fails, same-day instead of discovered later
# - Every step now writes a real row to performance_timing so the admin
#   dashboard's cron status panel actually shows real data (was always
#   empty before today - nothing had ever written to that table)
# - Gaps between heavy steps widened 30min -> 45min for more buffer

AVERION_DIR=/home/averion/Averion
LOG_DIR=/var/log/averion
mkdir -p $LOG_DIR $AVERION_DIR/backups

export PGPASSWORD=$(grep '^DB_PASSWORD=' $AVERION_DIR/.env | cut -d '=' -f2-)

FAILED_STEPS=()

echo "=== Averion Daily Cron $(date) ===" | tee -a $LOG_DIR/daily.log

# run_step DISPLAY_NAME STEP_KEY LOGFILE COMMAND...
run_step() {
    local display_name="$1"
    local step_key="$2"
    local logfile="$3"
    shift 3
    local start_ts=$(date +%s)
    local step_output_file=$(mktemp)
    echo "--- $display_name ---" | tee -a "$logfile"
    local status="success"
    if "$@" > "$step_output_file" 2>&1; then
        echo "✅ $display_name complete $(date)" | tee -a "$logfile"
    else
        echo "❌ $display_name FAILED $(date) — see $logfile" | tee -a "$logfile"
        status="failed"
        FAILED_STEPS+=("$display_name")
    fi
    cat "$step_output_file" >> "$logfile"
    local records=$(grep -o 'RECORDS_PROCESSED:[0-9]*' "$step_output_file" | tail -1 | cut -d: -f2)
    records=${records:-0}
    rm -f "$step_output_file"
    local duration=$(( $(date +%s) - start_ts ))
    python3 -c "
import sys; sys.path.insert(0, '$AVERION_DIR')
from dotenv import load_dotenv; load_dotenv('/home/averion/Averion/.env')
import database as db
db.init_pool()
db.record_performance_timing('$step_key', $duration, $records, '$status')
" >> "$logfile" 2>&1
}

# ADDED June 23 2026 - checks a System Control cron toggle before
# running a step. Defaults to enabled (true) if the setting row
# doesn't exist yet, matching every other toggle's safe default.
setting_enabled() {
    local key="$1"
    local val=$(psql -U averion -h localhost averion -t -A -c "SELECT value FROM system_settings WHERE key='$key'" 2>/dev/null)
    if [ -z "$val" ]; then
        return 0
    fi
    if [ "$val" = "true" ]; then
        return 0
    else
        return 1
    fi
}

# ═══════════════════════════════
# 03:00 — INFRASTRUCTURE
# ═══════════════════════════════
BACKUP_FILE=$AVERION_DIR/backups/averion_$(date +%Y%m%d).sql
run_step "DB Backup" "db_backup" "$LOG_DIR/daily.log" pg_dump -U averion -h localhost averion --file="$BACKUP_FILE"
find $AVERION_DIR/backups -name "*.sql" -mtime +7 -delete

run_step "System Health" "system_health" "$LOG_DIR/daily.log" python3 -c "
import sys; sys.path.insert(0, '$AVERION_DIR')
from dotenv import load_dotenv; load_dotenv('/home/averion/Averion/.env')
import database as db, psutil, redis
db.init_pool()
r = redis.Redis(host='localhost', port=6379)
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage('/').percent
db.record_system_health(cpu, ram, disk, 0, 0, 0, 0, 0)
print(f'Health: CPU={cpu}% RAM={ram}% Disk={disk}%')
"
sleep 2700

# ═══════════════════════════════
# ~03:45 — COIN CLASSIFICATION
# ═══════════════════════════════
if setting_enabled "cron_classification_enabled"; then
    run_step "Classification" "classification" "$LOG_DIR/classify.log" python3 $AVERION_DIR/classify_coins.py
fi
if setting_enabled "cron_min_orders_enabled"; then
    run_step "Exchange Min Orders" "min_orders" "$LOG_DIR/min_orders.log" python3 $AVERION_DIR/refresh_min_orders.py
fi
sleep 2700

# ═══════════════════════════════
# ~04:30 — CALCULATE COIN PARAMS
# ═══════════════════════════════
if setting_enabled "cron_params_enabled"; then
    run_step "Calculate Parameters" "params" "$LOG_DIR/params.log" python3 $AVERION_DIR/calculate_coin_params.py
fi
sleep 2700

# ═══════════════════════════════
# ~05:15 — RARS SCORING
# ═══════════════════════════════
if setting_enabled "cron_rars_enabled"; then
    run_step "RARS Scoring" "rars" "$LOG_DIR/rars.log" python3 $AVERION_DIR/rars_champion_scoring.py
fi
if setting_enabled "cron_champion_enabled"; then
    run_step "Champion Promotion" "champion" "$LOG_DIR/rars.log" python3 $AVERION_DIR/rars_champion_promotion.py
fi

# ═══════════════════════════════
# TAIL STEPS — fast, run right after each other
# ═══════════════════════════════
run_step "Paper Timer" "paper_timer" "$LOG_DIR/paper_timer.log" python3 $AVERION_DIR/automation/check_paper_timer.py
run_step "BTC Daily Fetch" "btc_daily" "$LOG_DIR/daily.log" python3 $AVERION_DIR/fetch_btc_daily.py

if [ "$(date +%u)" = "7" ]; then
    if setting_enabled "cron_retention_enabled"; then
        run_step "Data Retention" "retention" "$LOG_DIR/retention.log" python3 $AVERION_DIR/data_retention_cleanup.py --execute
    fi
    run_step "Sunday VACUUM" "cleanup" "$LOG_DIR/cleanup.log" psql -U averion -h localhost averion -c "VACUUM ANALYZE;"
    find $LOG_DIR -name "*.log" -mtime +30 -delete
    DISK=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [ "$DISK" -gt 70 ]; then
        echo "⚠️ Disk usage high: ${DISK}%" | tee -a $LOG_DIR/cleanup.log
    fi
fi

if setting_enabled "cron_reports_enabled"; then
    run_step "Research Reports" "reports" "$LOG_DIR/daily.log" bash $AVERION_DIR/generate_reports.sh
fi

if setting_enabled "notify_daily_report"; then
run_step "Telegram Daily Report" "telegram" "$LOG_DIR/daily.log" python3 -c "
import sys; sys.path.insert(0, '$AVERION_DIR')
from dotenv import load_dotenv; load_dotenv('/home/averion/Averion/.env')
import database as db, telegram as tg
db.init_pool()
from datetime import datetime, timedelta
with db.get_db() as conn:
    cur = conn.cursor()
    cur.execute(\"\"\"
        SELECT COUNT(*),
               COALESCE(SUM(total_sold_usdt - total_invested), 0)
        FROM positions
        WHERE status='closed'
        AND closed_at > NOW() - INTERVAL '24 hours'
    \"\"\")
    closed_today, profit_today = cur.fetchone()
    cur.execute(\"SELECT COUNT(*) FROM positions WHERE status='open'\")
    open_pos = cur.fetchone()[0]

tg.send_admin(f'''📊 <b>Averion Daily Report</b>
{datetime.utcnow().strftime('%B %d, %Y')}

Closed today: {closed_today}
Profit today: \${float(profit_today):.2f}
Open positions: {open_pos:,}

Research: {open_pos:,} open · data collecting
Generated at: {datetime.utcnow().strftime('%H:%M UTC')}''')
print('✅ Telegram daily report sent')
"
fi

echo "=== Daily Cron Complete $(date) ===" | tee -a $LOG_DIR/daily.log

if [ ${#FAILED_STEPS[@]} -gt 0 ]; then
    FAILED_LIST=$(printf '%s, ' "${FAILED_STEPS[@]}")
    echo "⚠️ FAILED STEPS TODAY: $FAILED_LIST" | tee -a $LOG_DIR/daily.log
    if setting_enabled "notify_health_alerts"; then
        python3 -c "
import sys; sys.path.insert(0, '$AVERION_DIR')
from dotenv import load_dotenv; load_dotenv('/home/averion/Averion/.env')
import telegram as tg
tg.send_admin('⚠️ <b>Averion Daily Cron — Step Failures</b>\n\nFailed: ${FAILED_LIST}\n\nCheck /var/log/averion/ logs for details.')
" >> $LOG_DIR/daily.log 2>&1
    fi
fi
