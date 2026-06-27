"""
long_short_market_price.py - Price LOOKUP only, for Long and Short
specifically (Scalper does NOT use this - it receives price pushed
directly via its own on_price_update callback, confirmed from the
real code, not assumed). For the Redis CONNECTION itself, shared by
all 3 systems, see redis_connection.py instead - kept separate on
purpose so this file's name accurately describes only what it does.

Written fresh June 27 2026. Uses the direct, single-key lookup
(Short's original approach), not Long's original wildcard scan
across all exchanges - confirmed every call site in Long's original
code already had the bot's exchange_name available, so the scan was
genuinely unnecessary work, not a real requirement. Direct lookup is
also faster (one exact Redis key vs scanning all keys matching a
pattern).
"""


def get_redis_price(r, coin, exchange_name):
    """Direct, single-key lookup - requires the caller to know which
    exchange this bot trades on (always true: every bot is tied to
    exactly one exchange_id, confirmed). No wildcard scanning."""
    try:
        val = r.get(f'price:{exchange_name}:{coin}/USDT')
        return float(val) if val else None
    except Exception:
        return None
