# admin_notifications.py - Admin-only Telegram notifications, kept
# deliberately separate from any future user/live notifications
# module for safety/isolation - a bug here should never be able to
# send a message to the wrong audience.
#
# Each function checks its own System Control setting before
# sending, so the Tab 5 toggles built earlier today actually do
# something real.

import database as db
import telegram as tg


def notify_daily_report(message):
    if db.get_setting_bool('notify_daily_report', True):
        tg.send_admin(message)


def notify_champion_change(message):
    if db.get_setting_bool('notify_champion_change', True):
        tg.send_admin(message)


def notify_health_alert(message):
    if db.get_setting_bool('notify_health_alerts', True):
        tg.send_admin(message)
