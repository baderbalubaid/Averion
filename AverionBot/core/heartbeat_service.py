"""
heartbeat_service.py - Shared by ALL 3 systems (Long, Short,
Scalper). Confirmed Long and Short both already had an identical
heartbeat pattern (just a different Redis key name each) - genuinely
shared logic, not just similar-looking code.

GAP FOUND AND FIXED HERE: Scalper had NO heartbeat at all in the
original code, confirmed by checking - meaning if its thread died
silently, nothing would ever detect or restart it, unlike Long/Short
which both have watchdog coverage in research_engine.py. Since this
is a fresh build, Scalper gets the same safety net here too.
"""
import time

HEARTBEAT_TTL_SECONDS = 150


def write_heartbeat(r, engine_name):
    """engine_name should be 'long_dca', 'short_dca', or 'scalper' -
    keeps the exact same Redis key naming the original watchdog code
    already expects (engine:{engine_name}:heartbeat), so nothing else
    needs to change to start using this."""
    try:
        r.setex(f'engine:{engine_name}:heartbeat', HEARTBEAT_TTL_SECONDS, str(time.time()))
    except Exception:
        pass


def is_heartbeat_alive(r, engine_name):
    """For a watchdog (in any process) to check if an engine is alive
    without needing to import that engine's module directly - reads
    purely from Redis."""
    try:
        val = r.get(f'engine:{engine_name}:heartbeat')
        return val is not None
    except Exception:
        return False
