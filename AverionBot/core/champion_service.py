"""
champion_service.py - Shared by Long and Scalper ONLY. Short does NOT
use this (confirmed and documented June 27 2026: short_dca_engine.py
has zero champion-related logic anywhere - each Short bot is pre-
assigned to one specific coin and never chooses between methods, so
there is nothing for a champion to select between. The original
'3 separate Short champions' plan in 13_LOCKED_DECISIONS.md was
superseded by this simpler design - corrected there too).

Shared logic, NOT shared answers: this takes system_type as a
parameter ('DCA' for Long, 'SCALPER' for Scalper) so each system gets
its own correct, separate 3 champions (bear/bull/sideways) - the
6-champion-slots-total locked decision (2 system types x 3 regimes)
from earlier this session.

Uses Long's original "fetch all 3 regimes at once" pattern, not
Scalper's original narrower "fetch only the current regime" pattern -
confirmed correct because a bot in Smart mode needs to be able to
pick whichever regime's champion matches conditions at any moment,
not just whatever regime happened to be active at load time.
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
import database as db


def load_champions(system_type):
    """system_type must be 'DCA' (Long) or 'SCALPER' (Scalper).
    Returns {regime: {bot_name, bot_params, method_family}} for ALL
    3 regimes at once, or {} on any failure - callers should treat a
    missing regime as 'no champion yet for this regime', not an
    error."""
    try:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT ch.regime, ch.method_id, b.bot_params, b.method
                FROM champion_history ch
                LEFT JOIN bots b ON b.name = ch.method_id
                WHERE ch.is_active_champion=TRUE AND ch.system_type=%s
            """, (system_type,))
            champions = {}
            for regime, bot_name, bot_params, method in cur.fetchall():
                champions[regime] = {
                    'bot_name': bot_name,
                    'bot_params': bot_params or {},
                    'method_family': method or bot_name,
                }
        return champions
    except Exception as e:
        print(f'⚠️ Champion lookup failed ({system_type}): {e}')
        return {}


def get_current_regime(r):
    """Reads the current BTC market regime (bear/bull/sideways) from
    the Redis cache that research_engine.py's run_cycle already
    maintains. Returns 'bear' as a safe default if the cache is
    empty or unreadable, matching the original behavior in both
    Long and Scalper's original code."""
    try:
        import json
        btc_data = r.get('btc:regime_data')
        if btc_data:
            return json.loads(btc_data).get('btc_regime', 'bear')
    except Exception:
        pass
    return 'bear'
