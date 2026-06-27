"""
bot_loader.py - Shared by Long and Short (NOT Scalper - confirmed
Scalper's _load_bots() queries method='S58' specifically and has a
genuinely different column set, stays in scalper_engine.py).

Takes direction as a parameter ('long' or 'short') so each system
gets its own correctly-filtered bots, while the actual SQL and
dict-building logic only exists once. Selects the full union of
fields either system needs - the underlying bots table has all of
these columns regardless of direction, so this is safe.

FIXED here for BOTH systems (June 27 2026): no trading_on filter in
the WHERE clause. Long's original had this filter removed June 25
after it was found to silently freeze DCA/TP on existing positions
the moment a bot stopped (manually, by debt, or by expiry) - per the
locked rule, trading_on=FALSE should only ever block NEW positions,
never existing ones. Short's original STILL has this same filter
(confirmed, logged in OPEN_INVESTIGATIONS.md #13) - this shared
function fixes it for Short too, by simply never having the bug in
the first place here.
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
import database as db


def load_bots(direction, require_dca_method_naming=False):
    """direction: 'long' or 'short'.
    require_dca_method_naming: if True, also requires method LIKE
    'DCA%' OR method LIKE 'E%' - Long's original query has this,
    Short's original does not (kept as an explicit, opt-in boolean
    rather than guessing whether Short secretly needs the same
    filter - not confirmed either way, so not assumed).

    FIXED June 27 2026: an earlier version of this function took the
    filter as a raw SQL string and f-string-inserted it directly into
    the query, which broke immediately - the '%' inside 'DCA%' LIKE
    wildcards collided with psycopg2's own '%s' parameter-substitution
    syntax, causing it to miscount expected parameters. A plain
    boolean with the real SQL hardcoded here avoids that entirely."""
    base_query = """
        SELECT
            b.id, b.user_id, b.exchange_id, b.wallet_id,
            b.name, b.method, b.entry_method, b.bot_params,
            b.base_order, b.dca_percent, b.spacing_multiplier,
            b.size_multiplier, b.take_profit_percent, b.trailing_percent,
            b.trades_per_bot, b.trades_per_coin,
            b.trading_on, b.dca_on, b.profit_coin,
            b.reserve_floor, b.resume_threshold, b.auto_resume, b.floor_paused,
            vw.is_paper, vw.current_balance, vw.committed_usdt,
            vw.allocation_amount, vw.coin as wallet_coin,
            e.exchange as exchange_name
        FROM bots b
        JOIN virtual_wallets vw ON b.wallet_id = vw.id
        JOIN exchanges e ON b.exchange_id = e.id
        WHERE b.is_research = FALSE
        AND b.is_template = FALSE
        AND b.direction = %s
        AND b.status = 'open'
        AND b.status != 'deleted'
    """
    if require_dca_method_naming:
        # FIXED June 27 2026, second attempt: even a hardcoded string
        # still needs its literal '%' escaped as '%%' for psycopg2's
        # parameter substitution - the problem was never about WHERE
        # the string came from, it is that ANY '%' in a query string
        # passed alongside a params tuple gets treated as psycopg2's
        # own placeholder syntax, full stop.
        base_query += " AND (b.method LIKE 'DCA%%' OR b.method LIKE 'E%%') "
    base_query += " ORDER BY b.user_id, b.id "

    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute(base_query, (direction,))
        rows = cur.fetchall()

    bots = []
    for r in rows:
        bots.append({
            'id': r[0], 'user_id': r[1], 'exchange_id': r[2], 'wallet_id': r[3],
            'name': r[4], 'method': r[5], 'entry_method': r[6],
            'bot_params': r[7] or {},
            'base_order': float(r[8] or 10), 'dca_percent': float(r[9] or 7),
            'spacing_multiplier': float(r[10] or 1.4),
            'size_multiplier': float(r[11] or 1.5),
            'tp_percent': float(r[12] or 5),
            'trailing_percent': float(r[13] or 2),
            'trades_per_bot': int(r[14] or 5), 'trades_per_coin': int(r[15] or 1),
            'trading_on': r[16], 'dca_on': r[17],
            'profit_coin': r[18] or 'USDT',
            'reserve_floor': float(r[19]) if r[19] is not None else None,
            'resume_threshold': float(r[20]) if r[20] is not None else None,
            'auto_resume': r[21] if r[21] is not None else True,
            'floor_paused': r[22] or False,
            'wallet': {
                'id': r[3], 'is_paper': r[23],
                'current_balance': float(r[24] or 0),
                'committed_usdt': float(r[25] or 0),
                'allocation_amount': float(r[26] or 0),
                'coin': r[27],
                'exchange_id': r[2],
                'exchange_name': r[28],
            },
        })
    return bots
