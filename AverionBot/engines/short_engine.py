"""
short_engine.py - Short-DCA engine, written fresh June 27 2026 as
part of the controlled migration. Built top-down, same as
long_engine.py and scalper_engine.py.

STATUS: skeleton only. _engine_loop is not yet implemented.
"""
import threading
import sys
sys.path.insert(0, '/home/averion/Averion/AverionBot/core')
from redis_connection import get_redis

_running = False
_cycle_thread = None


def is_engine_alive():
    """Watchdog check: is the Short-DCA thread actually running right
    now? Structure confirmed identical to long_engine.py's version."""
    global _cycle_thread
    return _running and _cycle_thread is not None and _cycle_thread.is_alive()


def start_engine():
    """Start the Short-DCA engine as a non-daemon thread. Same
    reasoning as Long: daemon threads can die silently on a process
    restart/reload with zero warning - non-daemon means a crash is
    visible and a watchdog can detect + restart it."""
    global _running, _cycle_thread
    if is_engine_alive():
        return
    _running = True
    _cycle_thread = threading.Thread(target=_engine_loop, daemon=False)
    _cycle_thread.start()
    print('✅ ShortEngine started')


def _engine_loop():
    """Main cycle loop. Connected to the shared get_redis() (June 27
    2026) - same one Long and Scalper use.
    TODO: rest of the loop body not yet built."""
    r = get_redis()
    while _running:
        raise NotImplementedError("rest of loop body not yet built")
