"""
scalper_signals.py — Shared signal logic
Used by both research_scalper_engine.py and live_scalper_engine.py
NO database writes here. Pure signal math only.
"""

def check_entry_signal(bot, coin, price, now, price_history, active, cooldowns):
    """
    Returns jump_pct if entry signal triggered, else None.
    bot: dict with trigger_pct, window_sec, hold_sec, stop_loss_pct
    """
    key = (bot['name'], coin)

    # Skip if already have position
    if key in active:
        return None

    # Check cooldown
    cooldown_end = cooldowns.get(key, 0)
    if now < cooldown_end:
        return None

    # Get price window_sec ago
    window = bot['window_sec']
    history = price_history.get(coin)
    if not history:
        return None

    old_price = None
    for ts, px in reversed(history):
        if now - ts >= window:
            old_price = px
            break

    if old_price is None or old_price == 0:
        return None

    # Calculate jump
    jump_pct = (price - old_price) / old_price * 100

    if jump_pct >= bot['trigger_pct']:
        return jump_pct

    return None


def check_stop_loss(pos, price):
    """
    Returns True if stop loss triggered.
    pos: dict with entry_price, stop_loss_pct
    """
    sl = pos.get('stop_loss_pct')
    if not sl:
        return False
    entry = pos['entry_price']
    if entry == 0:
        return False
    pnl_pct = (price - entry) / entry * 100
    return pnl_pct <= -sl


def calc_pnl(entry_price, exit_price, base_order):
    """Calculate PnL percentage and USDT amount."""
    if entry_price == 0:
        return 0.0, 0.0
    pnl_pct = (exit_price - entry_price) / entry_price * 100
    pnl_usdt = base_order * pnl_pct / 100
    return round(pnl_pct, 4), round(pnl_usdt, 8)


def get_btc_regime(redis_client):
    """Get BTC regime data from Redis cache."""
    try:
        import json
        btc_cached = redis_client.get('btc:regime_data')
        if btc_cached:
            d = json.loads(btc_cached)
            return (d.get('btc_price'), d.get('btc_sma50'),
                    d.get('btc_24h_change'), d.get('btc_regime'),
                    d.get('btc_dominance'))
    except:
        pass
    return None, None, None, None, None
