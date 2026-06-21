"""
data_retention_cleanup.py — Retention policy enforcement
Added June 20 2026, after auditing real table growth rates.

FINDINGS:
- scalper_positions: PURE research (0 live rows), 179k rows/day growth
- positions: MIXED (8,206 live rows out of 251,991) - research+live share this table
- trades: MIXED (12,778 live rows) - same situation
- ohlcv_hourly: pure market data, no research/live distinction

POLICY:
- Research rows (is_research=TRUE bots): 90-day retention
- Live/real user rows (is_research=FALSE bots): 3-year retention (locked spec)
- ohlcv_hourly: 1-year retention (locked spec, no user-data concern)

Run with --dry-run (default) to see counts WITHOUT deleting anything.
Run with --execute to actually delete.
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv('/home/averion/Averion/.env')
import database as db

RESEARCH_RETENTION_DAYS = 90
LIVE_RETENTION_DAYS = 365 * 3
OHLCV_RETENTION_DAYS = 365

def run(dry_run=True):
    db.init_pool()
    print(f"{'DRY RUN' if dry_run else 'EXECUTING'} - retention cleanup\n")

    with db.get_db() as conn:
        cur = conn.cursor()

        # scalper_positions: pure research, blanket 90-day window
        cur.execute("""
            SELECT COUNT(*) FROM scalper_positions
            WHERE exit_time < NOW() - INTERVAL '%s days'
        """ % RESEARCH_RETENTION_DAYS)
        print(f"scalper_positions older than {RESEARCH_RETENTION_DAYS}d: {cur.fetchone()[0]}")

        # positions: SELECTIVE - only research-bot rows older than 90d
        cur.execute("""
            SELECT COUNT(*) FROM positions p
            JOIN bots b ON p.bot_id = b.id
            WHERE b.is_research = TRUE
            AND p.opened_at < NOW() - INTERVAL '%s days'
        """ % RESEARCH_RETENTION_DAYS)
        print(f"positions (research-only) older than {RESEARCH_RETENTION_DAYS}d: {cur.fetchone()[0]}")

        # trades: SELECTIVE - only research-bot rows older than 90d
        cur.execute("""
            SELECT COUNT(*) FROM trades t
            JOIN bots b ON t.bot_id = b.id
            WHERE b.is_research = TRUE
            AND t.timestamp < NOW() - INTERVAL '%s days'
        """ % RESEARCH_RETENTION_DAYS)
        print(f"trades (research-only) older than {RESEARCH_RETENTION_DAYS}d: {cur.fetchone()[0]}")

        # ohlcv_hourly: pure market data, 1-year window
        cur.execute("""
            SELECT COUNT(*) FROM ohlcv_hourly
            WHERE timestamp < NOW() - INTERVAL '%s days'
        """ % OHLCV_RETENTION_DAYS)
        print(f"ohlcv_hourly older than {OHLCV_RETENTION_DAYS}d: {cur.fetchone()[0]}")

        if not dry_run:
            print("\nExecuting deletions...")
            cur.execute("DELETE FROM scalper_positions WHERE exit_time < NOW() - INTERVAL '%s days'" % RESEARCH_RETENTION_DAYS)
            print(f"Deleted {cur.rowcount} scalper_positions")
            cur.execute("""
                DELETE FROM positions WHERE id IN (
                    SELECT p.id FROM positions p JOIN bots b ON p.bot_id = b.id
                    WHERE b.is_research = TRUE AND p.opened_at < NOW() - INTERVAL '%s days'
                )
            """ % RESEARCH_RETENTION_DAYS)
            print(f"Deleted {cur.rowcount} positions (research)")
            cur.execute("""
                DELETE FROM trades WHERE id IN (
                    SELECT t.id FROM trades t JOIN bots b ON t.bot_id = b.id
                    WHERE b.is_research = TRUE AND t.timestamp < NOW() - INTERVAL '%s days'
                )
            """ % RESEARCH_RETENTION_DAYS)
            print(f"Deleted {cur.rowcount} trades (research)")
            cur.execute("DELETE FROM ohlcv_hourly WHERE timestamp < NOW() - INTERVAL '%s days'" % OHLCV_RETENTION_DAYS)
            print(f"Deleted {cur.rowcount} ohlcv_hourly")
            conn.commit()
            print("\nDone.")
        else:
            print("\n(Dry run - nothing deleted. Run with --execute to actually delete.)")

if __name__ == '__main__':
    run(dry_run='--execute' not in sys.argv)
