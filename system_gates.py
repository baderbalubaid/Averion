import database as db


def is_new_trade_allowed(direction, entry_method=None, exchange_name=None, is_research=False, user_id=None, is_admin=False):
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

    # FIXED June 23 2026 - moved outside the if/else, since the
    # 100-total cap and 30-paper sub-cap both need checking for EITHER
    # paper or live attempts, not just live. Only checked when user_id
    # is actually passed - existing callers that don't pass it are
    # unaffected until wired in.
    if user_id is not None and not is_within_trade_limit(user_id, is_admin, is_research):
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
        # FIXED June 23 2026: real bug found while reviewing System
        # Control - exchange custom_names are "MEXC Paper" and
        # "KuCoin Live", but this was transforming the FULL name
        # (exchange_mexc_paper_enabled), never matching the actual
        # setting keys (exchange_mexc_enabled). The toggles in Tab 5
        # have never actually done anything as a result. Now matches
        # on a substring instead of the exact full name.
        name_lower = exchange_name.lower()
        if 'mexc' in name_lower:
            exc_key = 'exchange_mexc_enabled'
        elif 'kucoin' in name_lower:
            exc_key = 'exchange_kucoin_enabled'
        else:
            exc_key = None
        if exc_key and not db.get_setting_bool(exc_key, True):
            return False

    return True


def is_within_trade_limit(user_id, is_admin=False, is_research=False):
    # REVISED June 23 2026 - 100 total open trades (paper+live
    # combined) is the free-tier hard cap, and within that, paper
    # specifically cannot exceed 30 - per explicit clarification, a
    # user must close paper trades to free room for live ones, not
    # two separate independent caps. Admin/owner exempt entirely.
    if is_admin:
        return True
    total, paper = db.get_open_trade_counts_for_user(user_id)
    if total >= 100:
        return False
    if is_research and paper >= 30:
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
