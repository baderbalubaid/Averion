"""
scalper_engine.py - Live Scalper (S58) engine, written fresh June 27
2026 as part of the controlled migration. Built top-down, same as
long_engine.py: skeleton first, deeper pieces only after tracing the
original. Writes to live_positions (confirmed from the real code -
NOT scalper_positions, which is a different, separate table used by
something else - this distinction is exactly why bot 747 was being
double-processed).

STATUS: skeleton only. _load_bots, _start_cleanup_thread,
_start_bot_refresh_thread, on_price_update are not yet implemented -
next step after comparing this shape against Long and Short's own
startup shape.
"""
import threading
from collections import defaultdict, deque
import sys
sys.path.insert(0, '/home/averion/Averion')
import database as db
sys.path.insert(0, '/home/averion/Averion/AverionBot/core')
from redis_connection import get_redis
from heartbeat_service import write_heartbeat

BOT_REFRESH_INTERVAL = 60


class ScalperEngine:
    """Class-based, unlike Long/Short which are plain functions plus
    a module-level thread. Confirmed genuinely different shape from
    the original - not assumed, checked."""

    def __init__(self):
        db.init_pool()
        self.price_history = defaultdict(lambda: deque(maxlen=1000))
        self.active = {}        # {(bot_id, coin): position_data}
        self.cooldowns = {}     # {(bot_id, coin): timestamp}
        self.live_bots = []     # loaded from DB
        self._lock = threading.Lock()
        # Connected to the shared redis_connection.py (June 27 2026) -
        # confirmed Scalper genuinely needs a Redis connection too
        # (price history cache, active-position state), just not the
        # price-LOOKUP function in long_short_market_price.py, since
        # price arrives pushed directly via on_price_update instead.
        self.r = get_redis()
        self._load_bots()
        self._cleanup_stuck_positions()
        self._start_cleanup_thread()
        self._start_bot_refresh_thread()
        print(f'✅ ScalperEngine initialized · {len(self.live_bots)} active bots')

    def _load_bots(self):
        """TODO: not yet implemented - next step is tracing the real
        _load_bots() in live_scalper_engine.py."""
        raise NotImplementedError("_load_bots not yet built")

    def _cleanup_stuck_positions(self):
        """TODO: not yet implemented."""
        raise NotImplementedError("_cleanup_stuck_positions not yet built")

    def _start_cleanup_thread(self):
        """TODO: not yet implemented."""
        raise NotImplementedError("_start_cleanup_thread not yet built")

    def _start_bot_refresh_thread(self):
        """TODO: not yet implemented. GAP FOUND June 27 2026: the
        original live_scalper_engine.py had NO heartbeat at all,
        unlike Long/Short which both write one every cycle - meaning
        a dead Scalper thread would never be detected or restarted.
        write_heartbeat(self.r, 'scalper') must be called here once
        this periodic refresh loop is actually built, fixing that gap
        as part of this rebuild rather than carrying it forward."""
        raise NotImplementedError("_start_bot_refresh_thread not yet built")
