import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import database as db

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

# ═══════════════════════════════
# CORE SEND FUNCTION
# ═══════════════════════════════
def send_message(chat_id, message, parse_mode='HTML'):
    if not BOT_TOKEN or not chat_id:
        print(f'Telegram not configured · message: {message[:50]}')
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            },
            timeout=10
        )
        return r.status_code == 200
    except Exception as e:
        print(f'Telegram send error: {e}')
        db.queue_notification(None, chat_id, message, 'failed')
        return False

def send_admin(message):
    return send_message(ADMIN_CHAT, message)

# ═══════════════════════════════
# RETRY FAILED NOTIFICATIONS
# ═══════════════════════════════
def retry_pending_notifications():
    pending = db.get_pending_notifications()
    sent = 0
    for notif in pending:
        notif_id = notif[0]
        chat_id = notif[2]
        message = notif[3]
        retry_count = notif[5] if len(notif) > 5 else 0

        if retry_count >= 3:
            # Give up after 3 retries
            db.mark_notification_sent(notif_id)
            continue

        success = send_message(chat_id, message)
        if success:
            db.mark_notification_sent(notif_id)
            sent += 1
        else:
            db.increment_notification_retry(notif_id)

    if sent > 0:
        print(f'✅ Sent {sent} pending notifications')

# ═══════════════════════════════
# TRADE NOTIFICATIONS
# ═══════════════════════════════
def notify_trade_open(user_id, coin, direction,
                       price, amount, method, is_paper):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:  # telegram_chat_id
        return

    chat_id = user[3]
    mode = '📄 Paper' if is_paper else '💰 Live'
    emoji = '📈' if direction == 'long' else '📉'

    msg = f"""{emoji} <b>Trade Opened</b> {mode}

Coin: <b>{coin}</b>
Direction: {direction.upper()}
Entry Price: ${price:.6f}
Amount: ${amount:.2f}
Method: {method}
Time: {datetime.utcnow().strftime('%H:%M UTC')}"""

    send_message(chat_id, msg)

def notify_trade_closed(user_id, coin, direction,
                         entry_price, exit_price,
                         profit, fee, dca_count,
                         reason, is_paper):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    chat_id = user[3]
    mode = '📄 Paper' if is_paper else '💰 Live'
    profit_emoji = '✅' if profit > 0 else '❌'
    net_profit = profit - fee

    msg = f"""{profit_emoji} <b>Trade Closed</b> {mode}

Coin: <b>{coin}</b>
Direction: {direction.upper()}
Entry: ${entry_price:.6f}
Exit: ${exit_price:.6f}
DCA Levels: {dca_count}
Gross Profit: ${profit:.2f}
Fee (20%): -${fee:.2f}
<b>Net Profit: ${net_profit:.2f}</b>
Reason: {reason.upper()}
Time: {datetime.utcnow().strftime('%H:%M UTC')}"""

    send_message(chat_id, msg)

def notify_dca(user_id, coin, dca_level,
               price, amount, avg_cost, is_paper):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    chat_id = user[3]
    mode = '📄' if is_paper else '💰'

    msg = f"""{mode} <b>DCA #{dca_level}</b>

Coin: <b>{coin}</b>
Price: ${price:.6f}
Amount: ${amount:.2f}
New Avg Cost: ${avg_cost:.6f}"""

    send_message(chat_id, msg)

# ═══════════════════════════════
# ALERT NOTIFICATIONS
# ═══════════════════════════════
def alert_reserve_low(user_id, balance):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>Reserve Wallet Low</b>

Balance: <b>${balance:.2f}</b>
Performance fees may not be collected.
Please top up your reserve wallet.

<a href="https://averionbot.com/settings">Top Up Now</a>"""

    send_message(user[3], msg)
    db.add_attention_log(user_id, 'red', 'reserve_low',
                         f'Reserve wallet low: ${balance:.2f}')

def alert_reserve_empty(user_id):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""🔴 <b>Reserve Wallet Empty</b>

Fees will be recorded as debt.
Bot continues trading normally.
Top up to clear debt and avoid issues."""

    send_message(user[3], msg)

def alert_api_key_expiring(user_id, exchange_name, days_left):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>API Key Expiring Soon</b>

Exchange: <b>{exchange_name}</b>
Days remaining: <b>{days_left}</b>
Please update your API key before it expires."""

    send_message(user[3], msg)
    db.add_attention_log(user_id, 'red', 'api_expiring',
                         f'{exchange_name} API key expires in {days_left} days')

def alert_api_key_invalid(user_id, exchange_name):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""🔴 <b>API Key Invalid</b>

Exchange: <b>{exchange_name}</b>
Exchange has been paused.
Please update your API key."""

    send_message(user[3], msg)
    db.add_attention_log(user_id, 'red', 'api_invalid',
                         f'{exchange_name} API key invalid · exchange paused')

def alert_st_flag(user_id, coin, pnl):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    emoji = '✅' if pnl >= 0 else '❌'
    msg = f"""🚨 <b>ST Flag Detected</b>

Coin: <b>{coin}</b>
Position closed automatically.
P&L: {emoji} ${pnl:.2f}

Exchange suspended trading on this coin."""

    send_message(user[3], msg)

def alert_checkpoint(user_id, coin, dca_level,
                      next_cost, bot_id, position_id):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>DCA Checkpoint Reached</b>

Coin: <b>{coin}</b>
Level: {dca_level}
Next DCA cost: ${next_cost:.2f}

DCA has been turned OFF automatically.
Open dashboard to continue or wait for TP."""

    send_message(user[3], msg)

def alert_low_balance(user_id, exchange_name):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""⚠️ <b>Insufficient Balance</b>

Exchange: <b>{exchange_name}</b>
No position can be funded right now.
Bot will retry when funds available."""

    send_message(user[3], msg)

# ═══════════════════════════════
# REPORT NOTIFICATIONS
# ═══════════════════════════════
def send_daily_report(user_id, closed_today, profit_today,
                       fees_today, open_positions, reserve):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    profit_emoji = '📈' if profit_today > 0 else '📊'

    msg = f"""{profit_emoji} <b>Daily Report</b>
{datetime.utcnow().strftime('%B %d, %Y')}

Closed today: {closed_today}
Gross profit: ${profit_today:.2f}
Fees paid: ${fees_today:.2f}
Net profit: ${profit_today - fees_today:.2f}

Open positions: {open_positions}
Reserve balance: ${reserve:.2f}"""

    send_message(user[3], msg)

def send_weekly_report(user_id, closed_week, profit_week,
                        fees_week, best_coin, worst_coin):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""📊 <b>Weekly Report</b>
{datetime.utcnow().strftime('%B %d, %Y')}

Positions closed: {closed_week}
Gross profit: ${profit_week:.2f}
Fees paid: ${fees_week:.2f}
Net profit: ${profit_week - fees_week:.2f}

Best coin: {best_coin or 'N/A'}
Worst coin: {worst_coin or 'N/A'}"""

    send_message(user[3], msg)

def send_monthly_report(user_id, closed_month,
                         profit_month, fees_month):
    user = db.get_user_by_id(user_id)
    if not user or not user[3]:
        return

    msg = f"""📅 <b>Monthly Report</b>
{datetime.utcnow().strftime('%B %Y')}

Positions closed: {closed_month}
Gross profit: ${profit_month:.2f}
Fees paid: ${fees_month:.2f}
<b>Net profit: ${profit_month - fees_month:.2f}</b>"""

    send_message(user[3], msg)

# ═══════════════════════════════
# VERIFICATION CODE
# ═══════════════════════════════
def send_verification_code(user_id, chat_id):
    code = db.create_verification_code(user_id)

    msg = f"""🔐 <b>Averion Verification Code</b>

Your code: <b>{code}</b>
Valid for 15 minutes.

If you did not request this, ignore this message."""

    success = send_message(chat_id, msg)
    if success:
        db.log_security_event(user_id, 'verification_code_sent',
                              details={'chat_id': chat_id})
    return success

# ═══════════════════════════════
# ADMIN NOTIFICATIONS
# ═══════════════════════════════
def admin_bot_started(mode):
    send_admin(
        f'🚀 <b>Averion Started</b>\n'
        f'Mode: {"📄 Paper" if mode else "💰 Live"}\n'
        f'Time: {datetime.utcnow().strftime("%H:%M UTC")}'
    )

def admin_bot_stopped(reason='manual'):
    send_admin(
        f'🛑 <b>Averion Stopped</b>\n'
        f'Reason: {reason}\n'
        f'Time: {datetime.utcnow().strftime("%H:%M UTC")}'
    )

def admin_error(error_message, consecutive=1):
    send_admin(
        f'🔴 <b>Bot Error #{consecutive}</b>\n\n'
        f'{error_message[:500]}'
    )

def admin_cron_complete(step, duration, records):
    send_admin(
        f'✅ <b>Cron: {step}</b>\n'
        f'Duration: {duration:.1f}s\n'
        f'Records: {records}'
    )

def admin_cron_failed(step, error):
    send_admin(
        f'❌ <b>Cron Failed: {step}</b>\n\n'
        f'{str(error)[:300]}'
    )

def admin_reclassification(coin, from_cat, to_cat):
    send_admin(
        f'📊 <b>Reclassification</b>\n'
        f'{coin}: {from_cat} → {to_cat}'
    )

if __name__ == '__main__':
    print('✅ Telegram module ready')
    if BOT_TOKEN:
        print(f'Bot token: {BOT_TOKEN[:10]}...')
    else:
        print('⚠️ No bot token configured')

def admin_bot_stopped(reason):
    msg = f"🔴 Averion Bot Stopped\nReason: {reason}\n⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    send_admin(msg)

def admin_cron_started(step):
    msg = f"⚙️ Cron Started: {step}\n⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    send_admin(msg)

def admin_cron_finished(step, duration, records):
    msg = f"✅ Cron Done: {step}\nDuration: {duration:.1f}s · Records: {records}"
    send_admin(msg)

def admin_cron_failed(step, error):
    msg = f"❌ Cron Failed: {step}\nError: {error}"
    send_admin(msg)
