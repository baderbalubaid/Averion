"""
websocket_prices.py — Real-time MEXC price streaming via WebSocket + Protobuf
Replaces REST polling fetch_and_cache_prices() in bot_loop.py
Runs as a background thread, writes prices to Redis every ~1 second
"""

import sys
import json
import time
import threading
import redis
try:
    from scalper_engine import on_price_update as scalper_on_price
except Exception:
    scalper_on_price = None

try:
    from live_scalper_engine import on_price_update as live_scalper_on_price
except Exception:
    live_scalper_on_price = None

try:
    from scalper_v2_engine import on_price_update as scalper_v2_on_price
except Exception:
    scalper_v2_on_price = None

_live_dca_tp = None
def _init_live_dca():
    global _live_dca_tp
    try:
        from live_long_dca_engine import get_live_tp_callback, start_engine as start_dca_engine
        _live_dca_tp = get_live_tp_callback()
        start_dca_engine()
        print('✅ LiveLongDCA engine wired to WebSocket')
    except Exception as _e:
        print(f'⚠️ LiveLongDCA engine not loaded: {_e}')
import websocket
from datetime import datetime

sys.path.insert(0, '/home/averion/Averion')
import PushDataV3ApiWrapper_pb2 as wrapper

# ═══════════════════════════════
# CONFIG
# ═══════════════════════════════
WS_URL = "wss://wbs-api.mexc.com/ws"
SUBSCRIPTION = "spot@public.miniTickers.v3.api.pb@UTC+8"
REDIS_TTL = 120          # seconds
PING_INTERVAL = 20       # send ping every 20s
RECONNECT_DELAY = 5      # seconds between reconnects
EXCHANGE_NAME = "MEXC Paper"

def get_redis():
    return redis.Redis(host='localhost', port=6379, decode_responses=True)

class MexcWebSocketPrices:
    def __init__(self, tp_callback=None):
        # Init live DCA engine after DB pool is ready
        global _live_dca_tp
        if _live_dca_tp is None:
            _init_live_dca()
        self.r = get_redis()
        self.ws = None
        self.running = False
        self.price_count = 0
        self.last_update = None
        self.errors = 0
        self._tp_callback = tp_callback  # persists through reconnects

    @property
    def tp_callback(self):
        return self._tp_callback

    @tp_callback.setter
    def tp_callback(self, value):
        self._tp_callback = value  # always stored, survives reconnect

    def on_message(self, ws, msg):
        if isinstance(msg, bytes):
            try:
                data = wrapper.PushDataV3ApiWrapper()
                data.ParseFromString(msg)
                tickers = data.publicMiniTickers.items
                pipe = self.r.pipeline()
                for t in tickers:
                    if t.price and t.symbol.endswith('USDT'):
                        coin = t.symbol.replace('USDT', '')
                        pipe.setex(
                            f'price:{EXCHANGE_NAME}:{coin}/USDT',
                            REDIS_TTL,
                            t.price
                        )
                        self.price_count += 1
                        # Feed scalper engine
                        if scalper_on_price:
                            try:
                                scalper_on_price(coin, float(t.price))
                            except Exception:
                                pass
                        # Feed scalper v2 engine
                        if scalper_v2_on_price:
                            try:
                                scalper_v2_on_price(coin, float(t.price))
                            except Exception:
                                pass

                        # Feed live scalper engine
                        if live_scalper_on_price:
                            try:
                                live_scalper_on_price(coin, float(t.price))
                            except Exception:
                                pass
                        # Event-driven TP check
                        if self.tp_callback:
                            try:
                                self.tp_callback(coin, float(t.price))
                            except Exception:
                                pass
                        # Live Long DCA TP check
                        if _live_dca_tp:
                            try:
                                _live_dca_tp(coin, float(t.price))
                            except Exception:
                                pass
                pipe.execute()
                self.last_update = datetime.utcnow()
                self.r.setex('ws:mexc:status', 60, 'connected')
                self.r.setex('ws:mexc:last_update', 60, str(self.last_update))
                self.r.setex('ws:mexc:price_count', 60, str(self.price_count))
            except Exception as e:
                print(f'❌ WS decode error: {e}')
        elif isinstance(msg, str):
            try:
                data = json.loads(msg)
                if data.get('code') == 0:
                    print(f'✅ MEXC WS subscribed: {data.get("msg", "")}')
            except:
                pass

    def on_error(self, ws, error):
        self.errors += 1
        print(f'❌ WS error #{self.errors}: {error}')
        self.r.setex('ws:mexc:status', 60, f'error: {error}')

    def on_close(self, ws, *args):
        print(f'⚠️ WS closed · reconnecting in {RECONNECT_DELAY}s')
        self.r.setex('ws:mexc:status', 60, 'disconnected')

    def on_open(self, ws):
        print(f'✅ MEXC WebSocket connected!')
        ws.send(json.dumps({
            "method": "SUBSCRIPTION",
            "params": [SUBSCRIPTION]
        }))

    def connect(self):
        self.ws = websocket.WebSocketApp(
            WS_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever(
            ping_interval=PING_INTERVAL,
            ping_timeout=10,
            reconnect=5
        )

    def run(self):
        """Main loop with auto-reconnect."""
        self.running = True
        print('🚀 MEXC WebSocket price stream starting...')
        while self.running:
            try:
                self.connect()
            except Exception as e:
                print(f'❌ WS connection error: {e}')
            if self.running:
                print(f'🔄 Reconnecting in {RECONNECT_DELAY}s...')
                time.sleep(RECONNECT_DELAY)

    def start_background(self, tp_callback=None):
        if tp_callback:
            self.tp_callback = tp_callback
        """Start WebSocket in background thread."""
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        print('✅ WebSocket price stream started in background')
        return t

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()

# ═══════════════════════════════
# STANDALONE RUN
# ═══════════════════════════════
if __name__ == '__main__':
    ws = MexcWebSocketPrices()
    try:
        ws.run()
    except KeyboardInterrupt:
        print('\nStopping...')
        ws.stop()
