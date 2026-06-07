import os
import ccxt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import database as db

load_dotenv()

# ═══════════════════════════════
# FERNET ENCRYPTION
# ═══════════════════════════════
def get_fernet():
   # Full key mode (Day 1)
   full_key = os.getenv('FERNET_KEY')
   if full_key:
       return Fernet(full_key.encode())
   # Split key mode (Day 2+ · more secure)
   part_a = os.getenv('FERNET_KEY_PART_A')
   hetzner_token = os.getenv('HETZNER_API_TOKEN')
   secret_id = os.getenv('HETZNER_SECRET_ID')
   if part_a and hetzner_token and secret_id:
       import requests
       res = requests.get(
           f'https://api.hetzner.cloud/v1/secrets/{secret_id}',
           headers={'Authorization': f'Bearer {hetzner_token}'}
       )
       part_b = res.json()['secret']['value']
       return Fernet((part_a + part_b).encode())
   raise Exception('No Fernet key found · set FERNET_KEY or split key vars in .env')

def encrypt(text: str) -> str:
   return get_fernet().encrypt(text.encode()).decode()

def decrypt(text: str) -> str:
   return get_fernet().decrypt(text.encode()).decode()

# ═══════════════════════════════
# EXCHANGE INITIALIZATION
# ═══════════════════════════════
def init_exchange(exchange_row):
   exc_id = exchange_row[0]
   exc_name = exchange_row[1]
   api_key_enc = exchange_row[3]
   secret_enc = exchange_row[4]
   passphrase_enc = exchange_row[5]

   try:
       api_key = decrypt(api_key_enc)
       secret = decrypt(secret_enc)
       passphrase = decrypt(passphrase_enc) if passphrase_enc else None

       exchange_class = getattr(ccxt, exc_name)
       config = {
           'apiKey': api_key,
           'secret': decrypt(secret),
           'enableRateLimit': True,
           'options': {'defaultType': 'spot'}
       }
       if passphrase:
           config['password'] = passphrase

       exchange = exchange_class(config)
       return exchange

   except ccxt.AuthenticationError as e:
       db.pause_exchange(exc_id, 'Authentication failed', 'auth_error')
       db.record_bot_event(None, None, 'auth_error',
                          exchange=exc_name,
                          error_message=str(e))
       return None

   except Exception as e:
       print(f'Exchange init error {exc_name}: {e}')
       db.record_bot_event(None, None, 'init_error',
                          exchange=exc_name,
                          error_message=str(e))
       return None

# ═══════════════════════════════
# EXCHANGES THAT NEED PASSPHRASE
# ═══════════════════════════════
PASSPHRASE_REQUIRED = ['kucoin', 'okx', 'bitget']

def requires_passphrase(exchange_name: str) -> bool:
   return exchange_name.lower() in PASSPHRASE_REQUIRED

# ═══════════════════════════════
# BALANCE FETCHING
# ═══════════════════════════════
def get_balance(exchange_obj, currency='USDT'):
   try:
       balance = exchange_obj.fetch_balance()
       free = float(balance.get(currency, {}).get('free') or 0)
       total = float(balance.get(currency, {}).get('total') or 0)
       return {'free': free, 'total': total, 'currency': currency}
   except ccxt.AuthenticationError:
       raise
   except Exception as e:
       print(f'Balance fetch error: {e}')
       return {'free': 0, 'total': 0, 'currency': currency}

def get_all_balances(exchange_obj):
   try:
       balance = exchange_obj.fetch_balance()
       result = {}
       for currency, amounts in balance.items():
           if isinstance(amounts, dict):
               free = float(amounts.get('free') or 0)
               if free > 0:
                   result[currency] = free
       return result
   except Exception as e:
       print(f'All balances error: {e}')
       return {}

# ═══════════════════════════════
# PRICE FETCHING
# ═══════════════════════════════
def fetch_all_tickers(exchange_obj):
   try:
       return exchange_obj.fetch_tickers()
   except ccxt.RateLimitExceeded:
       print('Rate limit exceeded · waiting 30s')
       import time
       time.sleep(30)
       return fetch_all_tickers(exchange_obj)
   except Exception as e:
       print(f'Ticker fetch error: {e}')
       return {}

def fetch_ticker(exchange_obj, symbol):
   try:
       ticker = exchange_obj.fetch_ticker(symbol)
       return {
           'last': float(ticker.get('last') or 0),
           'bid': float(ticker.get('bid') or 0),
           'ask': float(ticker.get('ask') or 0),
           'volume': float(ticker.get('baseVolume') or 0),
           'symbol': symbol
       }
   except Exception as e:
       print(f'Ticker error {symbol}: {e}')
       return None

# ═══════════════════════════════
# ORDER EXECUTION
# ═══════════════════════════════
def market_buy(exchange_obj, symbol, usdt_amount, bot_id=None, position_id=None, dca_level=0):
   try:
       order = exchange_obj.create_market_buy_order(
           symbol, None,
           params={'quoteOrderQty': usdt_amount}
       )
       return parse_order(order)
   except ccxt.InsufficientFunds as e:
       return {'error': 'insufficient_funds', 'message': str(e)}
   except ccxt.AuthenticationError as e:
       return {'error': 'auth_error', 'message': str(e)}
   except ccxt.BadSymbol as e:
       return {'error': 'bad_symbol', 'message': str(e)}
   except Exception as e:
       return {'error': 'unknown', 'message': str(e)}

def market_sell(exchange_obj, symbol, quantity):
   try:
       order = exchange_obj.create_market_sell_order(
           symbol, quantity
       )
       return parse_order(order)
   except ccxt.InsufficientFunds as e:
       return {'error': 'insufficient_funds', 'message': str(e)}
   except ccxt.AuthenticationError as e:
       return {'error': 'auth_error', 'message': str(e)}
   except Exception as e:
       return {'error': 'unknown', 'message': str(e)}

def limit_buy(exchange_obj, symbol, quantity, price):
   try:
       order = exchange_obj.create_limit_buy_order(
           symbol, quantity, price
       )
       return parse_order(order)
   except ccxt.InsufficientFunds as e:
       return {'error': 'insufficient_funds', 'message': str(e)}
   except Exception as e:
       return {'error': 'unknown', 'message': str(e)}

def cancel_order(exchange_obj, order_id, symbol):
   try:
       exchange_obj.cancel_order(order_id, symbol)
       return True
   except ccxt.OrderNotFound:
       return True  # Already cancelled
   except Exception as e:
       print(f'Cancel order error: {e}')
       return False

def fetch_order(exchange_obj, order_id, symbol):
   try:
       order = exchange_obj.fetch_order(order_id, symbol)
       return parse_order(order)
   except Exception as e:
       print(f'Fetch order error: {e}')
       return None

def fetch_recent_orders(exchange_obj, limit=100):
   try:
       orders = exchange_obj.fetch_orders(limit=limit)
       return [parse_order(o) for o in orders]
   except Exception as e:
       print(f'Fetch orders error: {e}')
       return []

def parse_order(order):
   return {
       'id': order.get('id'),
       'symbol': order.get('symbol'),
       'side': order.get('side'),
       'type': order.get('type'),
       'status': order.get('status'),
       'price': float(order.get('price') or 0),
       'average': float(order.get('average') or 0),
       'amount': float(order.get('amount') or 0),
       'filled': float(order.get('filled') or 0),
       'remaining': float(order.get('remaining') or 0),
       'cost': float(order.get('cost') or 0),
       'fee': float(order.get('fee', {}).get('cost') or 0),
       'fee_currency': order.get('fee', {}).get('currency', 'USDT'),
       'timestamp': order.get('timestamp')
   }

# ═══════════════════════════════
# EXCHANGE MINIMUM ORDER SIZE
# ═══════════════════════════════
def get_min_order_size(exchange_obj, symbol):
   try:
       markets = exchange_obj.load_markets()
       market = markets.get(symbol, {})
       limits = market.get('limits', {})
       min_amount = limits.get('amount', {}).get('min') or 0
       min_cost = limits.get('cost', {}).get('min') or 0
       return {
           'min_amount': float(min_amount),
           'min_cost': float(min_cost),
           'symbol': symbol
       }
   except Exception as e:
       print(f'Min order error {symbol}: {e}')
       return {'min_amount': 0, 'min_cost': 0, 'symbol': symbol}

def get_all_min_orders(exchange_obj, base_currency='USDT'):
   try:
       markets = exchange_obj.load_markets()
       result = {}
       for symbol, market in markets.items():
           if not symbol.endswith(f'/{base_currency}'):
               continue
           limits = market.get('limits', {})
           min_amount = limits.get('amount', {}).get('min') or 0
           min_cost = limits.get('cost', {}).get('min') or 0
           result[symbol] = {
               'min_amount': float(min_amount),
               'min_cost': float(min_cost)
           }
       return result
   except Exception as e:
       print(f'All min orders error: {e}')
       return {}

# ═══════════════════════════════
# ST FLAG DETECTION
# ═══════════════════════════════
def check_st_flag_exchange(exchange_obj, symbol):
   try:
       ticker = exchange_obj.fetch_ticker(symbol)
       info = ticker.get('info', {})

       # MEXC specific
       if info.get('status') in ['ST', 'SUSPENDED', '3']:
           return True

       # Generic: no trading volume for 24h
       volume = float(ticker.get('baseVolume') or 0)
       if volume == 0:
           return True

       return False
   except ccxt.BadSymbol:
       return True  # Symbol not found = likely suspended
   except Exception:
       return False

# ═══════════════════════════════
# RECONCILIATION
# ═══════════════════════════════
def reconcile_exchange_orders(exchange_obj, exchange_id):
   orders = fetch_recent_orders(exchange_obj, limit=100)
   reconciled = 0

   for order in orders:
       if not order.get('id'):
           continue
       if order.get('status') not in ['closed', 'filled']:
           continue

       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("""
               SELECT id FROM trades
               WHERE exchange_order_id = %s
           """, (order['id'],))

           if not cur.fetchone():
               # Missing trade · insert it
               symbol = order.get('symbol', '')
               coin = symbol.split('/')[0] if '/' in symbol else symbol
               cur.execute("""
                   INSERT INTO trades (
                       exchange_id, coin, side, price,
                       quantity, usdt_amount, order_type,
                       exchange_order_id, is_paper, timestamp
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE, NOW())
               """, (
                   exchange_id, coin,
                   order.get('side', ''),
                   order.get('average') or order.get('price') or 0,
                   order.get('filled') or 0,
                   order.get('cost') or 0,
                   order.get('type', 'market'),
                   order['id']
               ))
               reconciled += 1
               print(f'✅ Reconciled order: {order["id"]}')

   print(f'✅ Reconciliation complete: {reconciled} orders added')
   return reconciled

# ═══════════════════════════════
# SUPPORTED EXCHANGES
# ═══════════════════════════════
SUPPORTED_EXCHANGES = [
   {'id': 'mexc', 'name': 'MEXC', 'passphrase': False},
   {'id': 'kucoin', 'name': 'KuCoin', 'passphrase': True},
   {'id': 'binance', 'name': 'Binance', 'passphrase': False},
   {'id': 'bybit', 'name': 'Bybit', 'passphrase': False},
   {'id': 'okx', 'name': 'OKX', 'passphrase': True},
   {'id': 'bitget', 'name': 'Bitget', 'passphrase': True},
   {'id': 'gate', 'name': 'Gate.io', 'passphrase': False},
]

def get_supported_exchanges():
   return SUPPORTED_EXCHANGES

if __name__ == '__main__':
   print('✅ Exchanges module ready')
   print(f'Supported: {[e["name"] for e in SUPPORTED_EXCHANGES]}')
   print(f'Passphrase required: {[e["name"] for e in SUPPORTED_EXCHANGES if e["passphrase"]]}')
