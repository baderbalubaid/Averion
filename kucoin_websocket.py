import json
import time
import threading
import requests
import websocket
import redis
from datetime import datetime

try:
    from scalper_engine import on_price_update as scalper_on_price
except Exception:
    scalper_on_price = None

try:
    from live_scalper_engine import on_price_update as live_scalper_on_price
except Exception:
    live_scalper_on_price = None

try:
    from short_dca_engine import on_price_update as short_on_price
except Exception:
    short_on_price = None

try:
    from scalper_v2_engine import on_price_update as scalper_v2_on_price
except Exception:
    scalper_v2_on_price = None

try:
    from live_long_dca_engine import get_live_tp_callback
    _live_dca_tp = get_live_tp_callback()
except Exception:
    _live_dca_tp = None

REDIS_TTL = 120
RECONNECT_DELAY = 5
EXCHANGE_NAME = "KuCoin Live"
EXCHANGE_TYPE = "kucoin"
BULLET_URL = "https://api.kucoin.com/api/v1/bullet-public"

def get_redis():
    return redis.Redis(host='localhost', port=6379, decode_responses=True)


class KucoinWebSocketPrices:
    def __init__(self):
        self.r = get_redis()
        self.ws = None
        self.running = False
        self.price_count = 0
        self.last_update = None
        self.errors = 0
        self._ping_interval = 18000
        self._ping_thread = None

    def get_connection_token(self):
        resp = requests.post(BULLET_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()['data']
        token = data['token']
        endpoint = data['instanceServers'][0]['endpoint']
        ping_interval = data['instanceServers'][0].get('pingInterval', 18000)
        connect_id = str(int(time.time() * 1000))
        ws_url = f"{endpoint}?token={token}&connectId={connect_id}"
        return ws_url, ping_interval

    def send_ping_loop(self, ws, interval_ms):
        interval_s = max(interval_ms / 1000.0 - 2, 5)
        while self.running and ws.sock and ws.sock.connected:
            try:
                ws.send(json.dumps({"id": str(int(time.time() * 1000)), "type": "ping"}))
            except Exception:
                break
            time.sleep(interval_s)

    def on_message(self, ws, msg):
        try:
            data = json.loads(msg)
        except Exception as e:
            print(f'KuCoin WS decode error: {e}')
            return

        msg_type = data.get('type')
        if msg_type == 'welcome':
            print('KuCoin WS welcomed, subscribing to all-market ticker feed')
            ws.send(json.dumps({
                "id": str(int(time.time() * 1000)),
                "type": "subscribe",
                "topic": "/market/ticker:all",
                "privateChannel": False,
                "response": True
            }))
            return
        if msg_type == 'ack':
            print('KuCoin WS subscription acknowledged')
            return
        if msg_type != 'message':
            return

        # FIXED: topic is always literally "/market/ticker:all" for
        # this firehose channel - the actual symbol is in the separate
        # 'subject' field (confirmed via real raw message inspection,
        # e.g. subject="BTC-USDT"), NOT parsed from the topic string.
        ticker_data = data.get('data', {})
        symbol = data.get('subject', '')
        if not symbol.endswith('-USDT'):
            return
        coin = symbol.replace('-USDT', '')
        price = ticker_data.get('price') or ticker_data.get('lastTradedPrice') or ticker_data.get('bestAsk')
        if not price:
            return

        try:
            self.r.setex(f'price:{EXCHANGE_NAME}:{coin}/USDT', REDIS_TTL, price)
            self.price_count += 1

            if scalper_on_price:
                try: scalper_on_price(coin, float(price))
                except Exception: pass
            if scalper_v2_on_price:
                try: scalper_v2_on_price(coin, float(price))
                except Exception: pass
            if live_scalper_on_price:
                try: live_scalper_on_price(coin, float(price))
                except Exception: pass
            if short_on_price:
                try: short_on_price(coin, float(price))
                except Exception: pass
            if _live_dca_tp:
                try: _live_dca_tp(coin, float(price))
                except Exception: pass

            self.last_update = datetime.utcnow()
            self.r.setex(f'ws:{EXCHANGE_TYPE}:status', 60, 'connected')
            self.r.setex(f'ws:{EXCHANGE_TYPE}:last_update', 60, str(self.last_update))
            self.r.setex(f'ws:{EXCHANGE_TYPE}:total_updates', 60, str(self.price_count))
        except Exception as e:
            print(f'KuCoin price write error for {coin}: {e}')

    def on_error(self, ws, error):
        self.errors += 1
        print(f'KuCoin WS error #{self.errors}: {error}')
        try:
            self.r.setex(f'ws:{EXCHANGE_TYPE}:status', 60, f'error: {error}')
        except Exception:
            pass

    def on_close(self, ws, *args):
        print(f'KuCoin WS closed, reconnecting in {RECONNECT_DELAY}s')
        try:
            self.r.setex(f'ws:{EXCHANGE_TYPE}:status', 60, 'disconnected')
        except Exception:
            pass

    def on_open(self, ws):
        print('KuCoin WebSocket connected')
        self._ping_thread = threading.Thread(
            target=self.send_ping_loop, args=(ws, self._ping_interval), daemon=False
        )
        self._ping_thread.start()

    def connect(self):
        ws_url, ping_interval = self.get_connection_token()
        self._ping_interval = ping_interval
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever()

    def run(self):
        self.running = True
        print('KuCoin WebSocket price stream starting...')
        while self.running:
            try:
                self.connect()
            except Exception as e:
                print(f'KuCoin WS connection error: {e}')
            if self.running:
                print(f'KuCoin reconnecting in {RECONNECT_DELAY}s...')
                time.sleep(RECONNECT_DELAY)

    def start_background(self):
        thread = threading.Thread(target=self.run, daemon=False)
        thread.start()
        return thread
