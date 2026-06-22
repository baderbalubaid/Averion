import database as db


def is_new_trade_allowed(direction, entry_method=None, exchange_name=None, is_research=False):
    if db.get_setting_bool('emergency_halt', False):
        return False
    if not db.get_setting_bool('new_trade_opening_enabled', True):
        return False

    if is_research:
        if not db.get_setting_bool('research_trading_enabled', True):
            return False
    else:
        if not db.get_setting_bool('live_trading_enabled', True):
            return False

    if direction == 'long':
        if not db.get_setting_bool('long_dca_enabled', True):
            return False
        if entry_method in ('dca_smart', 'smart') and not db.get_setting_bool('long_smart_enabled', True):
            return False
        if entry_method == 'dca_templates' and not db.get_setting_bool('long_customized_enabled', True):
            return False
        if entry_method == 'dca_asap' and not db.get_setting_bool('long_asap_enabled', True):
            return False
    elif direction == 'short':
        if not db.get_setting_bool('short_dca_enabled', True):
            return False
        if entry_method == 'smart' and not db.get_setting_bool('short_smart_enabled', True):
            return False
        if entry_method == 'customized' and not db.get_setting_bool('short_customized_enabled', True):
            return False
    elif direction == 'scalper':
        if not db.get_setting_bool('scalper_enabled', True):
            return False

    if exchange_name:
        exc_key = f'exchange_{exchange_name.lower().replace(" ", "_")}_enabled'
        if not db.get_setting_bool(exc_key, True):
            return False

    return True


def is_new_bot_creation_allowed():
    if db.get_setting_bool('emergency_halt', False):
        return False
    return db.get_setting_bool('new_bot_creation_enabled', True)


def is_dca_continuation_allowed():
    return db.get_setting_bool('dca_continuation_enabled', True)


def is_tp_trailing_allowed():
    return db.get_setting_bool('tp_trailing_enabled', True)


def is_short_buyback_allowed():
    return db.get_setting_bool('short_buyback_enabled', True)
