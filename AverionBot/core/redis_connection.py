"""
redis_connection.py - The ONE shared Redis connection, used by ALL 3
systems (Long, Short, Scalper). Split out from market price logic
deliberately, since Scalper needs a Redis connection (for its price
history cache and active-position locking) but does NOT use the
price-lookup function in long_short_market_price.py - it receives
price pushed directly via its own callback instead.
"""
import os
import redis as _redis
from dotenv import load_dotenv

load_dotenv('/home/averion/Averion/.env')

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

_shared_redis_conn = None


def get_redis():
    """One shared, reusable connection - never create a new Redis
    connection per call. Original code in multiple files once created
    a fresh connection on every single price tick, causing a real
    memory leak - fixed there earlier, built correctly from the start
    here."""
    global _shared_redis_conn
    if _shared_redis_conn is None:
        _shared_redis_conn = _redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
        )
    return _shared_redis_conn
