"""
rars_champion_promotion.py — Champion eligibility + promotion logic
Reads from rars_scores (written by rars_champion_scoring.py),
applies gates, selects champion per system_type+regime,
writes to champion_history.

Rules (locked June 18 2026):
- Min 30 trades AND min 7 active days to be eligible
- Champion = highest blended RARS (70% 30d + 30% 90d)
- Challenger must beat current champion by 10% to promote
- challenger_method_id + challenger_since tracked on champion row
"""
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv('/home/averion/Averion/.env')
import database as db
from datetime import datetime, timezone, timedelta

db.init_pool()

MIN_TRADES = 30
MIN_ACTIVE_DAYS = {'DCA': 7, 'SCALPER': 3}  # scalper high-frequency, 3 days sufficient
PROMOTION_THRESHOLD = 1.10  # challenger must be 10% better

def get_blended_scores(system_type, regime):
    """Fetch latest 30d and 90d scores, compute 70/30 blend."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (method, score_window)
                method, score_window, rars_score,
                trade_count, active_days, robustness_pct
            FROM rars_scores
            WHERE system_type=%s AND regime=%s
            AND score_window IN ('30d','90d')
            ORDER BY method, score_window, calculated_at DESC
        """, (system_type, regime))
        rows = cur.fetchall()

    by_method = {}
    for method, window, score, trades, days, robustness in rows:
        if method not in by_method:
            by_method[method] = {'30d': None, '90d': None,
                                  'trade_count': trades,
                                  'active_days': days,
                                  'robustness_pct': robustness}
        by_method[method][window] = float(score or 0)

    blended = {}
    for method, d in by_method.items():
        s30 = d['30d'] or 0
        s90 = d['90d'] or 0
        blended_score = round(s30 * 0.70 + s90 * 0.30, 2)
        blended[method] = {
            'blended_rars': blended_score,
            'trade_count': d['trade_count'],
            'active_days': d['active_days'],
            'robustness_pct': d['robustness_pct'],
        }
    return blended

def get_active_champion(system_type, regime):
    """Returns current active champion row or None."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, method_id, blended_rars_score,
                   challenger_method_id, challenger_since
            FROM champion_history
            WHERE system_type=%s AND regime=%s
            AND is_active_champion=TRUE
        """, (system_type, regime))
        return cur.fetchone()

def promote_champion(system_type, regime, new_method,
                     new_score, robustness, old_method, reason):
    """Deactivate old champion, insert new one."""
    with db.get_db() as conn:
        cur = conn.cursor()
        if old_method:
            cur.execute("""
                UPDATE champion_history
                SET is_active_champion=FALSE
                WHERE system_type=%s AND regime=%s
                AND is_active_champion=TRUE
            """, (system_type, regime))
        cur.execute("""
            INSERT INTO champion_history (
                system_type, regime, method_id,
                blended_rars_score, robustness_pct,
                is_active_champion, previous_champion_method_id,
                reason, promoted_at
            ) VALUES (%s,%s,%s,%s,%s,TRUE,%s,%s,NOW())
        """, (system_type, regime, new_method, new_score,
              robustness, old_method, reason))
        conn.commit()
    print(f"👑 NEW CHAMPION: {system_type}/{regime} → {new_method} "
          f"(RARS={new_score}, was {old_method})")

def update_challenger_tracking(champion_id, challenger_method, challenger_since):
    """Update challenger tracking on the active champion row."""
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE champion_history
            SET challenger_method_id=%s, challenger_since=%s
            WHERE id=%s
        """, (challenger_method, challenger_since, champion_id))
        conn.commit()

def run_promotion(system_type, regime):
    """Full promotion logic for one system+regime."""
    blended = get_blended_scores(system_type, regime)
    if not blended:
        print(f"⚠️  No scores found for {system_type}/{regime}")
        return

    # Apply eligibility gates
    eligible = {m: d for m, d in blended.items()
                if d['trade_count'] >= MIN_TRADES
                and d['active_days'] >= MIN_ACTIVE_DAYS.get(system_type, 7)}

    if not eligible:
        print(f"⚠️  No eligible methods for {system_type}/{regime} "
              f"(need {MIN_TRADES} trades + {MIN_ACTIVE_DAYS} days)")
        return

    # Find best eligible challenger
    best = max(eligible.items(), key=lambda x: x[1]['blended_rars'])
    best_method, best_data = best
    best_score = best_data['blended_rars']

    champion = get_active_champion(system_type, regime)

    if not champion:
        # No champion yet - promote best eligible method
        promote_champion(system_type, regime, best_method, best_score,
                        best_data['robustness_pct'], None,
                        'Initial champion - no previous champion existed')
        try:
            import admin_notifications as an
            an.notify_champion_change(
                f'New Champion Set\n\n'
                f'{system_type}/{regime}: {best_method} (RARS={best_score})\n'
                f'No previous champion existed for this slot.'
            )
        except Exception:
            pass
        return

    champ_id, champ_method, champ_score, challenger_id, challenger_since = champion
    champ_score = float(champ_score or 0)

    if best_method == champ_method:
        print(f"✅ {system_type}/{regime}: {champ_method} remains champion "
              f"(RARS={best_score})")
        # Clear any challenger tracking since champion is still best
        if challenger_id:
            update_challenger_tracking(champ_id, None, None)
        return

    # Check 10% promotion threshold
    required_score = champ_score * PROMOTION_THRESHOLD
    if best_score >= required_score:
        # Check if challenger has been consistently ahead
        now = datetime.now(timezone.utc)
        if challenger_id == best_method and challenger_since:
            days_ahead = (now - challenger_since).days
            if days_ahead >= MIN_ACTIVE_DAYS.get(system_type, 7):
                promote_champion(
                    system_type, regime, best_method, best_score,
                    best_data['robustness_pct'], champ_method,
                    f'Promoted after {days_ahead} days ahead by '
                    f'{round((best_score/champ_score-1)*100,1)}%')
                try:
                    import admin_notifications as an
                    an.notify_champion_change(
                        f'Champion Change\n\n'
                        f'{system_type}/{regime}: {champ_method} -> {best_method}\n'
                        f'New RARS={best_score} vs old {champ_score}\n'
                        f'Ahead {days_ahead} days by {round((best_score/champ_score-1)*100,1)}%'
                    )
                except Exception:
                    pass
            else:
                print(f"⏳ {system_type}/{regime}: {best_method} leads by "
                      f"{round((best_score/champ_score-1)*100,1)}% "
                      f"but only {days_ahead}/{MIN_ACTIVE_DAYS} days ahead")
        else:
            # Start tracking this challenger
            update_challenger_tracking(champ_id, best_method, now)
            print(f"👀 {system_type}/{regime}: {best_method} starts challenging "
                  f"{champ_method} (RARS {best_score} vs {champ_score})")
    else:
        print(f"✅ {system_type}/{regime}: {champ_method} holds "
              f"(challenger {best_method} at {best_score} needs "
              f"{required_score:.1f} to promote)")
        if challenger_id:
            update_challenger_tracking(champ_id, None, None)

def run_all_promotions():
    """Run promotion logic for all system+regime combinations."""
    total = 0
    for system_type in ['DCA', 'SCALPER']:
        for regime in ['bull', 'bear', 'sideways']:
            run_promotion(system_type, regime)
            total += 1
    print(f"RECORDS_PROCESSED:{total}")

if __name__ == '__main__':
    print("=== RARS Champion Promotion Run ===")
    run_all_promotions()
    print("=== Done ===")
