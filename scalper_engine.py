"""
scalper_engine.py — WebSocket Momentum Scalper Engine
E58: Detects sudden price jumps and enters/exits within seconds
Completely separate from DCA bot logic
"""
import threading
import time
from datetime import datetime
from collections import defaultdict, deque
import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db

# ═══════════════════════════════
# SCALPER CONFIG
# ═══════════════════════════════
BASE_ORDER = 100  # USDT per scalp

# E58 bot definitions
E58_BOTS = [
    {'name': 'E58-1', 'trigger_pct': 1.5, 'window_sec': 1.0, 'hold_sec': 10, 'stop_loss_pct': 2.0},
    {'name': 'E58-10', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 60, 'stop_loss_pct': None},
    {'name': 'E58-100', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-101', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-102', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-103', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-104', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-105', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-106', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-107', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-108', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-109', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-11', 'trigger_pct': 3.0, 'window_sec': 1.0, 'hold_sec': 5, 'stop_loss_pct': 2.0},
    {'name': 'E58-110', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-111', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-112', 'trigger_pct': 10.0, 'window_sec': 3.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-113', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-114', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-115', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-116', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-117', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-118', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-119', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-12', 'trigger_pct': 5.0, 'window_sec': 1.0, 'hold_sec': 5, 'stop_loss_pct': 3.0},
    {'name': 'E58-120', 'trigger_pct': 10.0, 'window_sec': 1.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-13', 'trigger_pct': 1.0, 'window_sec': 0.5, 'hold_sec': 8, 'stop_loss_pct': 1.5},
    {'name': 'E58-14', 'trigger_pct': 2.0, 'window_sec': 1.0, 'hold_sec': 20, 'stop_loss_pct': 2.0},
    {'name': 'E58-15', 'trigger_pct': 5.0, 'window_sec': 1.0, 'hold_sec': 3, 'stop_loss_pct': 3.0},
    {'name': 'E58-16', 'trigger_pct': 3.0, 'window_sec': 5.0, 'hold_sec': 45, 'stop_loss_pct': None},
    {'name': 'E58-17', 'trigger_pct': 8.0, 'window_sec': 2.0, 'hold_sec': 15, 'stop_loss_pct': 4.0},
    {'name': 'E58-18', 'trigger_pct': 2.0, 'window_sec': 3.0, 'hold_sec': 60, 'stop_loss_pct': 2.0},
    {'name': 'E58-19', 'trigger_pct': 1.5, 'window_sec': 0.5, 'hold_sec': 5, 'stop_loss_pct': 1.5},
    {'name': 'E58-2', 'trigger_pct': 2.0, 'window_sec': 1.0, 'hold_sec': 10, 'stop_loss_pct': 2.0},
    {'name': 'E58-20', 'trigger_pct': 2.0, 'window_sec': 0.5, 'hold_sec': 5, 'stop_loss_pct': 2.0},
    {'name': 'E58-21', 'trigger_pct': 3.0, 'window_sec': 1.0, 'hold_sec': 3, 'stop_loss_pct': 2.0},
    {'name': 'E58-22', 'trigger_pct': 1.5, 'window_sec': 1.0, 'hold_sec': 8, 'stop_loss_pct': 1.5},
    {'name': 'E58-23', 'trigger_pct': 2.5, 'window_sec': 1.0, 'hold_sec': 5, 'stop_loss_pct': 2.0},
    {'name': 'E58-24', 'trigger_pct': 4.0, 'window_sec': 2.0, 'hold_sec': 8, 'stop_loss_pct': 2.5},
    {'name': 'E58-25', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-26', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-27', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-28', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-29', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-3', 'trigger_pct': 2.0, 'window_sec': 2.0, 'hold_sec': 15, 'stop_loss_pct': 2.5},
    {'name': 'E58-30', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-31', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-32', 'trigger_pct': 20.0, 'window_sec': 10.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-33', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-34', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-35', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-36', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-37', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-38', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-39', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-4', 'trigger_pct': 3.0, 'window_sec': 2.0, 'hold_sec': 15, 'stop_loss_pct': 2.5},
    {'name': 'E58-40', 'trigger_pct': 20.0, 'window_sec': 5.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-41', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-42', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-43', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-44', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-45', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-46', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-47', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-48', 'trigger_pct': 20.0, 'window_sec': 3.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-49', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-5', 'trigger_pct': 3.0, 'window_sec': 2.0, 'hold_sec': 30, 'stop_loss_pct': 3.0},
    {'name': 'E58-50', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-51', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-52', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-53', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-54', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-55', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-56', 'trigger_pct': 20.0, 'window_sec': 1.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-57', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-58', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-59', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-6', 'trigger_pct': 4.0, 'window_sec': 3.0, 'hold_sec': 30, 'stop_loss_pct': 3.0},
    {'name': 'E58-60', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-61', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-62', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-63', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-64', 'trigger_pct': 15.0, 'window_sec': 10.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-65', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-66', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-67', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-68', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-69', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-7', 'trigger_pct': 5.0, 'window_sec': 3.0, 'hold_sec': 30, 'stop_loss_pct': 3.0},
    {'name': 'E58-70', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-71', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-72', 'trigger_pct': 15.0, 'window_sec': 5.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-73', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-74', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-75', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-76', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-77', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-78', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-79', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-8', 'trigger_pct': 7.0, 'window_sec': 5.0, 'hold_sec': 60, 'stop_loss_pct': 5.0},
    {'name': 'E58-80', 'trigger_pct': 15.0, 'window_sec': 3.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-81', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-82', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-83', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-84', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-85', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-86', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-87', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-88', 'trigger_pct': 15.0, 'window_sec': 1.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-89', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-9', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 60, 'stop_loss_pct': 5.0},
    {'name': 'E58-90', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-91', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 30, 'stop_loss_pct': None},
    {'name': 'E58-92', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 20, 'stop_loss_pct': None},
    {'name': 'E58-93', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 10, 'stop_loss_pct': None},
    {'name': 'E58-94', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 5, 'stop_loss_pct': None},
    {'name': 'E58-95', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 3, 'stop_loss_pct': None},
    {'name': 'E58-96', 'trigger_pct': 10.0, 'window_sec': 10.0, 'hold_sec': 1, 'stop_loss_pct': None},
    {'name': 'E58-97', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 50, 'stop_loss_pct': None},
    {'name': 'E58-98', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 40, 'stop_loss_pct': None},
    {'name': 'E58-99', 'trigger_pct': 10.0, 'window_sec': 5.0, 'hold_sec': 30, 'stop_loss_pct': None},
]

class ScalperEngine:
    def __init__(self):
        db.init_pool()
        # Rolling price history per coin: deque of (timestamp, price)
        self.price_history = defaultdict(lambda: deque(maxlen=1000))
        # Active scalper positions: {(bot_name, coin): position_id}
        self.active = {}
        # Cooldown per coin per bot: {(bot_name, coin): timestamp}
        self.cooldowns = {}
        # Bot IDs from DB
        self.bot_ids = {}
        self._load_bot_ids()
        self._lock = threading.Lock()
        # Clean up stuck positions from previous run
        # Redis connection
        import redis as _redis
        self.r = _redis.Redis(host='localhost', port=6379, decode_responses=True)
        self._cleanup_stuck_positions()
        # Start background cleanup thread
        self._start_cleanup_thread()
        print(f'✅ ScalperEngine initialized · {len(E58_BOTS)} bots')

    def _cleanup_stuck_positions(self):
        """Close positions stuck open longer than 2x hold_seconds."""
        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT s.id, s.coin, s.entry_price, s.hold_seconds,
                           EXTRACT(EPOCH FROM (NOW() - s.entry_time))::int as seconds_open
                    FROM scalper_positions s
                    WHERE s.status = 'open'
                    AND EXTRACT(EPOCH FROM (NOW() - s.entry_time)) > s.hold_seconds * 2
                """)
                stuck = cur.fetchall()

            closed = 0
            for pos_id, coin, entry_price, hold_sec, seconds_open in stuck:
                # Get latest price
                history = self.price_history.get(coin)
                exit_price = float(history[-1][1]) if history else float(entry_price)
                pnl_pct = (exit_price - float(entry_price)) / float(entry_price) * 100 if float(entry_price) > 0 else 0
                pnl_usdt = 100 * pnl_pct / 100

                with db.get_db() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE scalper_positions SET
                            exit_price = %s, exit_time = NOW(),
                            pnl_pct = %s, pnl_usdt = %s,
                            exit_reason = 'timer_recovery', status = 'closed'
                        WHERE id = %s
                    """, (exit_price, round(pnl_pct,4), round(pnl_usdt,8), pos_id))
                closed += 1

            if closed > 0:
                print(f'🔧 Cleaned {closed} stuck scalper positions')
        except Exception as e:
            print(f'⚠️ Cleanup error: {e}')

    def _start_cleanup_thread(self):
        """Background thread that cleans stuck positions every 30s."""
        def cleanup_loop():
            while True:
                time.sleep(30)
                self._cleanup_stuck_positions()

        t = threading.Thread(target=cleanup_loop, daemon=True)
        t.start()

    def _load_bot_ids(self):
        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, name FROM bots WHERE method='E58'")
                for row in cur.fetchall():
                    self.bot_ids[row[1]] = row[0]
            print(f'✅ Loaded {len(self.bot_ids)} E58 bot IDs')
        except Exception as e:
            print(f'⚠️ ScalperEngine bot ID load error: {e}')

    def on_price(self, coin, price):
        """Called by WebSocket on every price update."""
        now = time.time()
        self.price_history[coin].append((now, price))

        # Check each bot
        for bot in E58_BOTS:
            self._check_entry(bot, coin, price, now)

        # Update active positions
        self._update_active(coin, price, now)

    def _check_entry(self, bot, coin, price, now):
        key = (bot['name'], coin)

        # Skip if already have position for this bot+coin
        if key in self.active:
            return

        # Check cooldown (5 min)
        cooldown_end = self.cooldowns.get(key, 0)
        if now < cooldown_end:
            return

        # Get price window_sec ago
        window = bot['window_sec']
        history = self.price_history[coin]
        old_price = None
        for ts, px in reversed(history):
            if now - ts >= window:
                old_price = px
                break

        if old_price is None or old_price == 0:
            return

        # Calculate jump
        jump_pct = (price - old_price) / old_price * 100

        if jump_pct >= bot['trigger_pct']:
            self._open_position(bot, coin, price, jump_pct, now)

    def _open_position(self, bot, coin, price, trigger_jump, now):
        key = (bot['name'], coin)
        bot_id = self.bot_ids.get(bot['name'])

        try:
            with db.get_db() as conn:
                cur = conn.cursor()
                # Get BTC regime from Redis
                btc_price = None; btc_sma50 = None
                btc_24h = None; btc_regime = None; btc_dom = None
                try:
                    import json as _json
                    btc_cached = self.r.get('btc:regime_data')
                    if btc_cached:
                        btc_data = _json.loads(btc_cached)
                        btc_price = btc_data.get('btc_price')
                        btc_sma50 = btc_data.get('btc_sma50')
                        btc_24h = btc_data.get('btc_24h_change')
                        btc_regime = btc_data.get('btc_regime')
                        btc_dom = btc_data.get('btc_dominance')
                except:
                    pass

                cur.execute("""
                    INSERT INTO scalper_positions
                        (bot_id, coin, entry_price, hold_seconds,
                         trigger_jump_pct, trigger_window_sec,
                         stop_loss_pct, base_order, status,
                         btc_price_at_entry, btc_sma50_at_entry,
                         btc_24h_change_pct, btc_regime, btc_dominance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'open',
                            %s, %s, %s, %s, %s)
                    RETURNING id
                """, (bot_id, coin, price, bot['hold_sec'],
                      trigger_jump, bot['window_sec'],
                      bot.get('stop_loss_pct'), BASE_ORDER,
                      btc_price, btc_sma50, btc_24h, btc_regime, btc_dom))
                pos_id = cur.fetchone()[0]

            with self._lock:
                self.active[key] = {
                    'pos_id': pos_id,
                    'entry_price': price,
                    'entry_time': now,
                    'hold_sec': bot['hold_sec'],
                    'stop_loss_pct': bot.get('stop_loss_pct'),
                    'max_profit': 0.0,
                    'max_loss': 0.0,
                    'bot': bot,
                }

            print(f'⚡ SCALP OPEN: {bot["name"]} {coin} @ ${price:.8f} jump={trigger_jump:.2f}%')

            # Schedule auto-exit
            t = threading.Timer(bot['hold_sec'], self._exit_position, args=[key, 'timer'])
            t.daemon = True
            t.start()

        except Exception as e:
            print(f'⚠️ Scalper open error: {e}')

    def _update_active(self, coin, price, now):
        """Update max profit/loss and check stop loss for active positions."""
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

                # Stop loss check
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
        # Get latest price
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
                        exit_price      = %s,
                        exit_time       = NOW(),
                        max_profit_seen = %s,
                        max_loss_seen   = %s,
                        pnl_pct         = %s,
                        pnl_usdt        = %s,
                        exit_reason     = %s,
                        status          = 'closed'
                    WHERE id = %s
                """, (exit_price, pos['max_profit'], pos['max_loss'],
                      pnl_pct, pnl_usdt, reason, pos['pos_id']))

            # Set cooldown (5 min)
            self.cooldowns[key] = time.time() + 300

            emoji = '💚' if pnl_pct > 0 else '❤'
            print(f'{emoji} SCALP CLOSE: {key[0]} {coin} {reason} pnl={pnl_pct:.2f}% (${pnl_usdt:.2f})')

        except Exception as e:
            print(f'⚠️ Scalper exit error: {e}')

# Global instance
_scalper = None

def get_scalper():
    global _scalper
    if _scalper is None:
        _scalper = ScalperEngine()
    return _scalper

def on_price_update(coin, price):
    """Called from WebSocket price handler."""
    try:
        get_scalper().on_price(coin, price)
    except Exception as e:
        pass

if __name__ == '__main__':
    print('ScalperEngine test mode')
    db.init_pool()
    engine = ScalperEngine()
    print(f'Bot IDs loaded: {engine.bot_ids}')
