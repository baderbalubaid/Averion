"""
coin_params_service.py - Genuinely shared by Long, Short, and
research_engine.py's equivalent (confirmed: the old system itself
already imported this same function across files - Short literally
does `from live_long_dca_engine import load_coin_params_cache` -
this builds it as a real, proper shared module instead of that
awkward cross-file import).

No direction parameter needed at all - this is the exact same
calculation regardless of Long/Short/anything else, by design
(one source of truth, calculate_coin_params.py feeds this table).
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
import database as db


def load_coin_params_cache():
    """Load spacing/TP/trailing/tradeable per coin from
    coin_parameters. Returns {} on any failure rather than raising -
    callers should treat a missing coin as 'use bot-level defaults
    instead', not as an error."""
    cache = {}
    try:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT coin, dca_spacing, take_profit_pct, trailing_pct,
                       tradeable, size_mult, calculation_version
                FROM coin_parameters
            """)
            for row in cur.fetchall():
                cache[row[0]] = {
                    'dca_spacing': float(row[1]),
                    'take_profit': float(row[2]),
                    'trailing': float(row[3]),
                    'tradeable': row[4] if row[4] is not None else True,
                    'size_mult': float(row[5]) if row[5] is not None else None,
                    'calc_version': row[6],
                }
    except Exception as e:
        print(f'⚠️ coin_params load error: {e}')
    return cache
