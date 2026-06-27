"""
wallet_service.py - Shared by ALL 3 systems. Built only after
genuinely comparing all 3 systems' original wallet handling (deleted
an earlier, premature version of this file once that comparison
revealed real differences not yet understood):

- Long's original: plain read, no locking, no reservation - just
  checks balance, then later updates it after the exchange order
  succeeds.
- Short's original: no separate load - reads bot['wallet']
  directly, a value cached whenever bots were last loaded, never
  re-read fresh before spending.
- Scalper's original: SELECT ... FOR UPDATE (row lock), checks and
  deducts immediately, all inside one short database transaction.

Locked decision after discussion: with up to 723 bots confirmed
sharing a single wallet, fairness matters - reserve_funds() uses
Scalper's locked-reservation approach for ALL 3 systems. Critically,
the lock is held ONLY for the fast database check-and-reserve step,
then released immediately - the slower exchange order call always
happens AFTER, never while holding the lock. Per explicit
instruction: nothing here should ever add delay to reacting to live
market price - that reaction is a completely separate, already
zero-delay, push-based mechanism (price ticks trigger callbacks
instantly). This only governs fairness between bots sharing one
wallet's money, milliseconds of database time, not market timing.
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
import database as db


def reserve_funds(wallet_id, amount_usdt):
    """Atomically checks and reserves amount_usdt from a wallet, in
    one short, locked database transaction. Returns True if reserved
    successfully, False if insufficient funds (in which case nothing
    is changed). Caller must call release_funds() if the subsequent
    exchange order fails, to undo this reservation."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT current_balance FROM virtual_wallets
            WHERE id=%s FOR UPDATE
        """, (wallet_id,))
        row = cur.fetchone()
        if not row or float(row[0]) < amount_usdt:
            return False

        cur.execute("""
            UPDATE virtual_wallets
            SET current_balance = current_balance - %s,
                committed_usdt = committed_usdt + %s
            WHERE id=%s
        """, (amount_usdt, amount_usdt, wallet_id))
        conn.commit()
    return True


def release_funds(wallet_id, amount_usdt):
    """Undo a reservation - call this if the exchange order placed
    after reserve_funds() ends up failing, so the money genuinely
    goes back to being available rather than staying stuck as
    'committed' for a trade that never actually happened."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE virtual_wallets
            SET current_balance = current_balance + %s,
                committed_usdt = committed_usdt - %s
            WHERE id=%s
        """, (amount_usdt, amount_usdt, wallet_id))
        conn.commit()


def load_wallet(wallet_id):
    """Plain, fresh read - for displaying/checking wallet state, NOT
    for making a spend decision (use reserve_funds() for that, which
    checks and reserves atomically instead of just looking then
    hoping nothing changed in between)."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, is_paper, current_balance, committed_usdt,
                   allocation_amount, exchange_id
            FROM virtual_wallets WHERE id=%s
        """, (wallet_id,))
        row = cur.fetchone()
    if not row:
        return None
    return {
        'id': row[0], 'is_paper': row[1],
        'current_balance': float(row[2] or 0),
        'committed_usdt': float(row[3] or 0),
        'allocation_amount': float(row[4] or 0),
        'exchange_id': row[5],
    }
