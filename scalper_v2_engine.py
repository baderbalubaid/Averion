"""
scalper_v2_engine.py — Velocity-Based Scalper Engine (E58v2)
Detects price ACCELERATION (not just total jump) to enter earlier in pumps.
Runs alongside scalper_engine.py (E58) as a controlled A/B experiment.
Uses scalper_positions table — same as E58, separated by method='E58v2'.
"""
import threading
import time
from collections import defaultdict, deque
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db

# ═══════════════════════════════
# FIXED CONFIG (all 120 bots)
# ═══════════════════════════════
BASE_ORDER          = 100.0   # USDT per scalp
STOP_LOSS_PCT       = 5.0     # fixed for all bots
TRAIL_ACTIVATE_PCT  = 2.0     # profit % before trailing activates
COOLDOWN_SEC        = 60      # seconds between entries same coin+bot
MIN_PRICE_AGE_SEC   = 30      # min seconds of price history before entry
REJECT_5S           = 8.0     # reject if jumped >8% in last 5s
REJECT_30S          = 40.0    # reject if jumped >40% in last 30s
REJECT_60S          = 60.0    # reject if jumped >60% in last 60s
REJECT_MULT         = 1.6     # reject if price > 1.6x 60s low

# ═══════════════════════════════
# EXIT PROFILES
# ═══════════════════════════════
EXIT_PROFILES = {
    'tight':  {'max_hold_sec': 60,  'trail_pct': 1.5, 'stop_loss_pct': 3.0},
    'normal': {'max_hold_sec': 120, 'trail_pct': 2.5, 'stop_loss_pct': 5.0},
    'loose':  {'max_hold_sec': 180, 'trail_pct': 4.0, 'stop_loss_pct': 7.0},
}

# ═══════════════════════════════
# E58v2 BOT GRID — 120 bots
# ═══════════════════════════════
def _generate_grid():
    bots = []
    
    # 96 structured bots: 4×4×2×3 = 96
    vel_3s_values   = [2.0, 3.0, 4.0, 5.0]
    vel_10s_values  = [4.0, 6.0, 8.0, 10.0]
    accel_values    = [1.3, 1.6]
    exit_profiles   = ['tight', 'normal', 'loose']
    
    n = 1
    for v3 in vel_3s_values:
        for v10 in vel_10s_values:
            # Skip contradictory combos (vel_3s=5.0 + vel_10s=4.0 impossible)
            if v3 >= v10:
                continue
            for accel in accel_values:
                for ep in exit_profiles:
                    ep_cfg = EXIT_PROFILES[ep]
                    bots.append({
                        'name': f'E58v2-{n}',
                        'vel_3s': v3,
                        'vel_10s': v10,
                        'accel_ratio': accel,
                        'exit_profile': ep,
                        'max_hold_sec': ep_cfg['max_hold_sec'],
                        'trail_pct': ep_cfg['trail_pct'],
                        'stop_loss_pct': ep_cfg['stop_loss_pct'],
                    })
                    n += 1

    # 16 center duplicates + boundary bots (fill to 120)
    center_variants = [
        (3.0, 6.0, 1.6, 'normal', 120, 2.5, 5.0),
        (3.0, 6.0, 1.6, 'normal', 120, 2.5, 5.0),
        (3.0, 6.0, 1.6, 'normal', 120, 2.5, 5.0),
        (3.0, 6.0, 1.6, 'normal', 120, 2.5, 5.0),
        (2.0, 6.0, 1.5, 'tight',  60,  1.5, 3.0),
        (3.0, 8.0, 1.5, 'tight',  60,  1.5, 3.0),
        (4.0, 6.0, 1.5, 'normal', 120, 2.5, 5.0),
        (3.0, 6.0, 1.4, 'normal', 120, 2.5, 5.0),
        (2.5, 5.0, 1.5, 'tight',  60,  1.5, 3.0),
        (3.5, 7.0, 1.5, 'normal', 120, 2.5, 5.0),
        (4.0, 10.0, 1.6, 'loose', 180, 4.0, 7.0),
        (2.0, 8.0, 1.6, 'loose',  180, 4.0, 7.0),
        (3.0, 6.0, 1.6, 'tight',  60,  1.5, 3.0),
        (3.0, 6.0, 1.6, 'loose',  180, 4.0, 7.0),
        (2.5, 6.0, 1.5, 'normal', 120, 2.5, 5.0),
        (3.5, 8.0, 1.6, 'normal', 120, 2.5, 5.0),
    ]
    for v3, v10, accel, ep, hold, trail, sl in center_variants:
        bots.append({
            'name': f'E58v2-{n}',
            'vel_3s': v3, 'vel_10s': v10, 'accel_ratio': accel,
            'exit_profile': ep,
            'max_hold_sec': hold, 'trail_pct': trail, 'stop_loss_pct': sl,
        })
        n += 1

    # 10 aggressive wildcards (early entry)
    aggressive = [
        (1.5, 3.0, 1.2, 'tight'),
        (1.8, 3.5, 1.2, 'tight'),
        (2.0, 4.0, 1.2, 'tight'),
        (2.0, 3.5, 1.3, 'tight'),
        (1.5, 3.0, 1.3, 'tight'),
        (2.5, 4.5, 1.2, 'tight'),
        (1.5, 4.0, 1.2, 'tight'),
        (2.0, 4.5, 1.3, 'tight'),
        (1.8, 4.0, 1.3, 'tight'),
        (2.5, 5.0, 1.2, 'tight'),
    ]
    for v3, v10, accel, ep in aggressive:
        ep_cfg = EXIT_PROFILES[ep]
        bots.append({
            'name': f'E58v2-{n}',
            'vel_3s': v3, 'vel_10s': v10, 'accel_ratio': accel,
            'exit_profile': ep,
            'max_hold_sec': ep_cfg['max_hold_sec'],
            'trail_pct': ep_cfg['trail_pct'],
            'stop_loss_pct': ep_cfg['stop_loss_pct'],
        })
        n += 1

    # 5 high-confirmation wildcards
    highconf = [
        (5.0, 10.0, 1.8, 'normal'),
        (6.0, 12.0, 1.8, 'normal'),
        (7.0, 14.0, 2.0, 'loose'),
        (5.0, 12.0, 2.0, 'loose'),
        (6.0, 14.0, 1.8, 'loose'),
    ]
    for v3, v10, accel, ep in highconf:
        ep_cfg = EXIT_PROFILES[ep]
        bots.append({
            'name': f'E58v2-{n}',
            'vel_3s': v3, 'vel_10s': v10, 'accel_ratio': accel,
            'exit_profile': ep,
            'max_hold_sec': ep_cfg['max_hold_sec'],
            'trail_pct': ep_cfg['trail_pct'],
            'stop_loss_pct': ep_cfg['stop_loss_pct'],
        })
        n += 1

    # 5 moonshot wildcards (long hold + wide trail)
    moonshot = [
        (3.0, 6.0, 1.5, 300, 5.0, 6.0),
        (3.5, 7.0, 1.5, 300, 5.0, 6.0),
        (4.0, 8.0, 1.5, 300, 5.0, 7.0),
        (3.0, 7.0, 1.6, 300, 4.0, 6.0),
        (2.0, 5.0, 1.5, 300, 5.0, 6.0),
    ]
    for v3, v10, accel, hold, trail, sl in moonshot:
        bots.append({
            'name': f'E58v2-{n}',
            'vel_3s': v3, 'vel_10s': v10, 'accel_ratio': accel,
            'exit_profile': 'moonshot',
            'max_hold_sec': hold, 'trail_pct': trail, 'stop_loss_pct': sl,
        })
        n += 1

    return bots

E58V2_BOTS = _generate_grid()

# ═══════════════════════════════
# ENGINE
# ═══════════════════════════════
class ScalperV2Engine:
    def __init__(self):
        self.price_history = defaultdict(lambda: deque(maxlen=300))
        self.active = {}
        self.cooldowns = {}
        self.bot_ids = {}
        self.peak_prices = {}  # for trailing stop
        self._lock = threading.Lock()
        import redis as _redis
        self.r = _redis.Redis(host='localhost', port=6379, decode_responses=True)
        self._load_bot_ids()
        self._cleanup_stuck_positions()
        self._start_cleanup_thread()
        print(f'✅ ScalperV2Engine initialized · {len(E58V2_BOTS)} bots')

    def _load_bot_ids(self):
        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, name FROM bots WHERE method='E58v2'")
                for row in cur.fetchall():
                    self.bot_ids[row[1]] = row[0]
            print(f'✅ Loaded {len(self.bot_ids)} E58v2 bot IDs')
        except Exception as e:
            print(f'⚠️ ScalperV2 bot ID load error: {e}')

    def _cleanup_stuck_positions(self):
        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT s.id, s.coin, s.entry_price, s.hold_seconds,
                           EXTRACT(EPOCH FROM (NOW() - s.entry_time))::int
                    FROM scalper_positions s
                    JOIN bots b ON b.id = s.bot_id
                    WHERE s.status='open' AND b.method='E58v2'
                    AND EXTRACT(EPOCH FROM (NOW() - s.entry_time)) > s.hold_seconds * 2
                """)
                stuck = cur.fetchall()
            for pos_id, coin, entry_price, hold_sec, seconds_open in stuck:
                history = self.price_history.get(coin)
                exit_price = float(history[-1][1]) if history else float(entry_price)
                pnl_pct = (exit_price - float(entry_price)) / float(entry_price) * 100
                pnl_usdt = BASE_ORDER * pnl_pct / 100
                with db.get_db() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE scalper_positions SET exit_price=%s, exit_time=NOW(),
                        pnl_pct=%s, pnl_usdt=%s, exit_reason='timer_recovery', status='closed'
                        WHERE id=%s
                    """, (exit_price, round(pnl_pct,4), round(pnl_usdt,8), pos_id))
        except Exception as e:
            print(f'⚠️ V2 cleanup error: {e}')

    def _start_cleanup_thread(self):
        def loop():
            while True:
                time.sleep(30)
                try:
                    self._cleanup_stuck_positions()
                except Exception as e:
                    print(f'\u26a0\ufe0f ScalperV2 cleanup loop error (continuing): {e}')
        threading.Thread(target=loop, daemon=True).start()

    def _get_price_at(self, coin, seconds_ago):
        """Get price N seconds ago from history."""
        history = self.price_history[coin]
        now = time.time()
        target = now - seconds_ago
        best = None
        for ts, px in reversed(history):
            if ts <= target:
                best = px
                break
        return best

    def _pump_chase_guard(self, coin, price):
        """Returns True if coin already pumped too much — reject entry."""
        history = self.price_history[coin]
        if len(history) < 3:
            return False

        now = time.time()
        prices = [px for ts, px in history]
        times  = [ts for ts, px in history]

        # Check min age
        if now - times[0] < MIN_PRICE_AGE_SEC:
            return False

        # Get reference prices
        p5s  = self._get_price_at(coin, 5)
        p30s = self._get_price_at(coin, 30)
        p60s_min = min(prices[-60:]) if len(prices) >= 60 else min(prices)

        if p5s and p5s > 0:
            jump_5s = (price - p5s) / p5s * 100
            if jump_5s > REJECT_5S:
                return True

        if p30s and p30s > 0:
            jump_30s = (price - p30s) / p30s * 100
            if jump_30s > REJECT_30S:
                return True

        if p60s_min > 0:
            jump_60s = (price - p60s_min) / p60s_min * 100
            if jump_60s > REJECT_60S:
                return True
            if price > p60s_min * REJECT_MULT:
                return True

        return False

    def _velocity_signal(self, bot, coin, price, now):
        """Returns True if velocity + acceleration conditions met."""
        p3s  = self._get_price_at(coin, 3)
        p10s = self._get_price_at(coin, 10)

        if not p3s or not p10s or p3s <= 0 or p10s <= 0:
            return False

        change_3s  = (price - p3s)  / p3s  * 100
        change_10s = (price - p10s) / p10s * 100

        if change_3s < bot['vel_3s']:
            return False
        if change_10s < bot['vel_10s']:
            return False

        # Acceleration: recent 3s vs expected rate from 10s window
        expected_3s = change_10s * (3.0 / 10.0)
        if expected_3s <= 0:
            return False
        accel = change_3s / expected_3s
        if accel < bot['accel_ratio']:
            return False

        return True

    def on_price(self, coin, price):
        """Called by WebSocket on every price update."""
        now = time.time()
        self.price_history[coin].append((now, price))

        # Pre-calculate deltas once per coin
        pumped = self._pump_chase_guard(coin, price)

        for bot in E58V2_BOTS:
            self._check_entry(bot, coin, price, now, pumped)

        self._update_active(coin, price, now)

    def _check_entry(self, bot, coin, price, now, pumped):
        key = (bot['name'], coin)

        # FIXED June 23 2026: real race condition found during a deep
        # memory leak investigation - same pattern as the other two
        # Scalper variants, no lock on the check, self.active[key]
        # only set much later inside _open_position. Reserves the
        # slot atomically with the check now.
        with self._lock:
            if key in self.active:
                return
            self.active[key] = 'RESERVED'

        try:
            if now < self.cooldowns.get(key, 0):
                with self._lock:
                    if self.active.get(key) == 'RESERVED':
                        del self.active[key]
                return
            if pumped:
                with self._lock:
                    if self.active.get(key) == 'RESERVED':
                        del self.active[key]
                return
            if not self._velocity_signal(bot, coin, price, now):
                with self._lock:
                    if self.active.get(key) == 'RESERVED':
                        del self.active[key]
                return

            self._open_position(bot, coin, price, now)
        except Exception:
            with self._lock:
                if self.active.get(key) == 'RESERVED':
                    del self.active[key]
            raise

    def _open_position(self, bot, coin, price, now):
        key = (bot['name'], coin)
        bot_id = self.bot_ids.get(bot['name'])
        if not bot_id:
            return

        try:
            btc_price = btc_regime = None
            btc_24h = btc_dominance = btc_sma50 = None
            try:
                import json as _j
                btc_cached = self.r.get('btc:regime_data')
                if btc_cached:
                    btc_data = _j.loads(btc_cached)
                    btc_price     = btc_data.get('btc_price')
                    btc_regime    = btc_data.get('btc_regime')
                    btc_24h       = btc_data.get('btc_24h_change')
                    btc_dominance = btc_data.get('btc_dominance')
                    btc_sma50     = btc_data.get('btc_sma50')
            except:
                pass

            market_age = db.get_market_age_days(coin)

            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO scalper_positions
                        (bot_id, coin, entry_price, hold_seconds,
                         trigger_jump_pct, trigger_window_sec,
                         stop_loss_pct, base_order, status,
                         btc_price_at_entry, btc_regime,
                         btc_24h_change_pct, btc_dominance,
                         btc_sma50_at_entry, market_age_days)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'open',
                            %s,%s,%s,%s,%s,%s)
                    RETURNING id
                """, (bot_id, coin, price,
                      bot['max_hold_sec'],
                      bot['vel_3s'], 3.0,
                      bot['stop_loss_pct'], BASE_ORDER,
                      btc_price, btc_regime,
                      btc_24h, btc_dominance,
                      btc_sma50, market_age))
                pos_id = cur.fetchone()[0]

            with self._lock:
                self.active[key] = {
                    'pos_id':       pos_id,
                    'entry_price':  price,
                    'entry_time':   now,
                    'max_hold_sec': bot['max_hold_sec'],
                    'trail_pct':    bot['trail_pct'],
                    'stop_loss_pct':bot['stop_loss_pct'],
                    'peak_price':   price,
                    'trail_active': False,
                    'max_profit':   0.0,
                    'max_loss':     0.0,
                }

            # Schedule timeout exit (wrapped June 20 2026)
            def _safe_timeout_exit():
                try:
                    self._exit_position(key, 'timeout')
                except Exception as e:
                    print(f'\u26a0\ufe0f ScalperV2 timeout-exit error for {key}: {e}')
            t = threading.Timer(bot['max_hold_sec'], _safe_timeout_exit)
            t.daemon = True
            t.start()

            print(f'⚡V2 OPEN: {bot["name"]} {coin} @ ${price:.8f} '
                  f'vel3s={bot["vel_3s"]} accel={bot["accel_ratio"]}')

        except Exception as e:
            print(f'⚠️ V2 open error: {e}')

    def _update_active(self, coin, price, now):
        with self._lock:
            keys_to_exit = []
            for key, pos in self.active.items():
                if key[1] != coin:
                    continue
                entry = pos['entry_price']
                if entry == 0:
                    continue
                pnl_pct = (price - entry) / entry * 100

                pos['max_profit'] = max(pos['max_profit'], pnl_pct)
                pos['max_loss']   = min(pos['max_loss'],   pnl_pct)

                # Update peak for trailing
                if price > pos['peak_price']:
                    pos['peak_price'] = price

                # Activate trailing stop
                if pnl_pct >= TRAIL_ACTIVATE_PCT:
                    pos['trail_active'] = True

                # Trailing stop check
                if pos['trail_active']:
                    trail_pct = pos['trail_pct']
                    if price < pos['peak_price'] * (1 - trail_pct / 100):
                        keys_to_exit.append((key, 'trailing_stop'))
                        continue

                # Hard stop loss
                sl = pos.get('stop_loss_pct')
                if sl and pnl_pct <= -sl:
                    keys_to_exit.append((key, 'stop_loss'))

        for key, reason in keys_to_exit:
            self._exit_position(key, reason)

    def _exit_position(self, key, reason):
        with self._lock:
            pos = self.active.pop(key, None)
        if pos is None:
            return

        coin = key[1]
        history = self.price_history[coin]
        exit_price = history[-1][1] if history else pos['entry_price']
        entry = pos['entry_price']
        pnl_pct  = (exit_price - entry) / entry * 100 if entry > 0 else 0
        pnl_usdt = BASE_ORDER * pnl_pct / 100

        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE scalper_positions SET
                        exit_price=%s, exit_time=NOW(),
                        max_profit_seen=%s, max_loss_seen=%s,
                        pnl_pct=%s, pnl_usdt=%s,
                        exit_reason=%s, status='closed'
                    WHERE id=%s
                """, (exit_price, pos['max_profit'], pos['max_loss'],
                      round(pnl_pct,4), round(pnl_usdt,8),
                      reason, pos['pos_id']))

            self.cooldowns[key] = time.time() + COOLDOWN_SEC
            emoji = '💚' if pnl_pct > 0 else '❤️'
            print(f'{emoji} V2 CLOSE: {key[0]} {coin} {reason} '
                  f'pnl={pnl_pct:.2f}% (${pnl_usdt:.4f})')

        except Exception as e:
            print(f'⚠️ V2 exit error: {e}')


# Global instance
_scalper_v2 = None

def get_scalper_v2():
    global _scalper_v2
    if _scalper_v2 is None:
        _scalper_v2 = ScalperV2Engine()
    return _scalper_v2

def on_price_update(coin, price):
    try:
        get_scalper_v2().on_price(coin, price)
    except Exception:
        pass

if __name__ == '__main__':
    db.init_pool()
    engine = ScalperV2Engine()
    print(f'Grid size: {len(E58V2_BOTS)} bots')
    for b in E58V2_BOTS[:5]:
        print(b)
