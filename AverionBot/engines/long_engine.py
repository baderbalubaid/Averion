"""
long_engine.py - Long-DCA engine, written fresh June 27 2026 as part
of the controlled migration to AverionBot/. Built top-down: start
here with just the entry point, then each piece below gets filled in
only after tracing what the original code genuinely connects to -
nothing copy-pasted, nothing assumed shared until confirmed against
Short and Scalper too.

STATUS: skeleton only. _engine_loop is not yet implemented - this is
intentional, the next step is tracing what the original
_engine_loop() in live_long_dca_engine.py actually does.
"""
import threading
import sys
sys.path.insert(0, '/home/averion/Averion/AverionBot/core')
from redis_connection import get_redis
from heartbeat_service import write_heartbeat
from champion_service import load_champions, get_current_regime
from bot_loader import load_bots

_running = False
_cycle_thread = None


def is_engine_alive():
    """Watchdog check: is the Long-DCA thread actually running right
    now? Verified logic matches the original 1:1 - this exact check
    (not just _running) is what lets research_engine.py's watchdog
    detect a genuinely dead thread, not just a flag someone forgot to
    reset."""
    global _cycle_thread
    return _running and _cycle_thread is not None and _cycle_thread.is_alive()


def start_engine():
    """Start the Long-DCA engine as a non-daemon thread.
    NOT a daemon thread on purpose: daemon threads die silently with
    zero warning if the main process restarts/reloads internally -
    this caused a real 16.5 hour silent outage in the original system
    (June 16 2026). Non-daemon means a crash is visible, so the
    watchdog can detect and restart it."""
    global _running, _cycle_thread
    if is_engine_alive():
        return
    _running = True
    _cycle_thread = threading.Thread(target=_engine_loop, daemon=False)
    _cycle_thread.start()
    print('✅ LongEngine started')


def _engine_loop():
    """Main cycle loop. Connected to the shared get_redis(),
    write_heartbeat(), and champion_service (June 27 2026) - this
    system_type='DCA' call is what makes Long's champions genuinely
    different from Scalper's, even though both use the same shared
    function.
    TODO: rest of the loop body not yet built - next piece to trace
    is the bots list itself."""
    r = get_redis()
    while _running:
        write_heartbeat(r, 'long_dca')
        champions = load_champions('DCA')
        current_regime = get_current_regime(r)
        bots = load_bots('long', require_dca_method_naming=True)
        raise NotImplementedError("rest of loop body not yet built")
