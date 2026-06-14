"""
executor.py — Averion Execution Layer
======================================
PaperAdapter  → simulates fills, updates paper wallet in DB
LiveAdapter   → places real CCXT market orders, wallet syncs separately

Engine never knows which adapter it received.
Both return identical OrderResult structure.
"""

import time
import redis as _redis
import ccxt
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
import database as db
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# ── Standard result returned by both adapters ──────────────────────
@dataclass
class OrderResult:
    success:       bool
    side:          str           # 'buy' or 'sell'
    coin:          str
    fill_price:    float
    quantity:      float
    fee_usdt:      float
    order_id:      str
    price_age_ms:  Optional[int] # None for live, ms for paper
    timestamp:     str
    error:         Optional[str] = None


# ── Fee rates per exchange (fallback if not in DB) ─────────────────
DEFAULT_FEE_RATES = {
    'mexc':     0.001,   # 0.1%
    'binance':  0.001,
    'bybit':    0.001,
    'okx':      0.001,
    'kucoin':   0.001,
}

def get_fee_rate(exchange_name: str) -> float:
    try:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT taker_fee FROM exchange_coin_limits
                WHERE exchange=%s LIMIT 1
            """, (exchange_name.lower(),))
            row = cur.fetchone()
            if row and row[0]:
                return float(row[0])
    except Exception:
        pass
    return DEFAULT_FEE_RATES.get(exchange_name.lower(), 0.001)


def get_executor(wallet):
    """Returns the correct adapter based on wallet type."""
    if wallet['is_paper']:
        return PaperAdapter()
    else:
        return LiveAdapter()


# ── Redis price helper ─────────────────────────────────────────────
def get_redis_price(coin: str) -> tuple:
    """
    Returns (price, age_ms) from Redis.
    Raises ValueError if price not found or too stale (>10s).
    """
    try:
        r = _redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT,
            password=REDIS_PASSWORD, decode_responses=True
        )
        # Try MEXC format first
        keys = r.keys(f'price:*:{coin}/USDT')
        val = r.get(keys[0]) if keys else None
        ts_key = f'price_ts:MEXC:{coin}/USDT'
        ts_val = r.get(ts_key)

        if not val:
            raise ValueError(f'No Redis price for {coin}')

        price = float(val)
        now_ms = int(time.time() * 1000)

        if ts_val:
            price_ts = int(ts_val)
            age_ms = now_ms - price_ts
        else:
            age_ms = 0

        if age_ms > 10000:  # 10 seconds stale
            raise ValueError(f'Redis price for {coin} is stale ({age_ms}ms)')

        return price, age_ms

    except _redis.RedisError as e:
        raise ValueError(f'Redis error: {e}')


# ══════════════════════════════════════════════════════════════════
# PAPER ADAPTER
# ══════════════════════════════════════════════════════════════════
class PaperAdapter:

    def place_order(self, side: str, coin: str, usdt_amount: float,
                    wallet: dict, conn) -> OrderResult:
        """
        Simulate a market order.
        - Gets Redis price
        - Applies tiny spread (0.05%)
        - Calculates fee from exchange fee rate
        - Updates paper wallet atomically
        """
        try:
            # Get price from Redis
            raw_price, age_ms = get_redis_price(coin)

            # Simulate spread
            if side == 'buy':
                fill_price = raw_price * 1.0005   # 0.05% above
            else:
                fill_price = raw_price * 0.9995   # 0.05% below

            # Fee
            exchange_name = wallet.get('exchange_name', 'mexc')
            fee_rate = get_fee_rate(exchange_name)

            if side == 'buy':
                quantity = (usdt_amount / fill_price) * (1 - fee_rate)
                fee_usdt = usdt_amount * fee_rate
            else:
                # usdt_amount is quantity to sell for sell orders
                quantity = usdt_amount
                gross_usdt = quantity * fill_price
                fee_usdt = gross_usdt * fee_rate

            # Update paper wallet atomically
            cur = conn.cursor()
            cur.execute("""
                SELECT current_balance, committed_usdt
                FROM virtual_wallets WHERE id=%s FOR UPDATE
            """, (wallet['id'],))
            row = cur.fetchone()
            if not row:
                return OrderResult(
                    success=False, side=side, coin=coin,
                    fill_price=fill_price, quantity=0,
                    fee_usdt=0, order_id='', price_age_ms=age_ms,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    error='Wallet not found'
                )

            available = float(row[0])
            committed = float(row[1])

            if side == 'buy':
                if available < usdt_amount:
                    return OrderResult(
                        success=False, side=side, coin=coin,
                        fill_price=fill_price, quantity=0,
                        fee_usdt=0, order_id='', price_age_ms=age_ms,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        error='insufficient_funds'
                    )
                # Deduct from available, add to committed
                cur.execute("""
                    UPDATE virtual_wallets
                    SET current_balance = current_balance - %s,
                        committed_usdt  = committed_usdt + %s,
                        updated_at      = NOW()
                    WHERE id = %s
                """, (usdt_amount, usdt_amount, wallet['id']))

            else:  # sell
                # Return committed, add proceeds minus fee
                proceeds = (quantity * fill_price) - fee_usdt
                cur.execute("""
                    UPDATE virtual_wallets
                    SET current_balance = current_balance + %s,
                        committed_usdt  = GREATEST(0, committed_usdt - %s),
                        updated_at      = NOW()
                    WHERE id = %s
                """, (proceeds, usdt_amount * fill_price, wallet['id']))

            # Generate paper order ID (finalized after position insert)
            order_id = f'paper_{int(time.time() * 1000)}'

            return OrderResult(
                success=True,
                side=side,
                coin=coin,
                fill_price=fill_price,
                quantity=round(quantity, 8),
                fee_usdt=round(fee_usdt, 8),
                order_id=order_id,
                price_age_ms=age_ms,
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        except ValueError as e:
            return OrderResult(
                success=False, side=side, coin=coin,
                fill_price=0, quantity=0, fee_usdt=0,
                order_id='', price_age_ms=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=str(e)
            )
        except Exception as e:
            return OrderResult(
                success=False, side=side, coin=coin,
                fill_price=0, quantity=0, fee_usdt=0,
                order_id='', price_age_ms=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=f'paper_error: {e}'
            )


# ══════════════════════════════════════════════════════════════════
# LIVE ADAPTER
# ══════════════════════════════════════════════════════════════════
class LiveAdapter:

    def place_order(self, side: str, coin: str, usdt_amount: float,
                    wallet: dict, conn) -> OrderResult:
        """
        Place a real market order via CCXT.
        Wallet balance is NOT updated here — real wallet sync handles it.
        """
        exchange_obj = None
        try:
            # Load exchange credentials
            cur = conn.cursor()
            cur.execute("""
                SELECT e.exchange, e.api_key, e.secret
                FROM exchanges e
                WHERE e.id = %s
            """, (wallet['exchange_id'],))
            exc_row = cur.fetchone()
            if not exc_row:
                raise ValueError('Exchange not found')

            exc_name, api_key, secret = exc_row
            from exchanges import decrypt
            api_key = decrypt(api_key)
            secret  = decrypt(secret)

            # Init CCXT exchange
            exchange_class = getattr(ccxt, exc_name.lower())
            exchange_obj = exchange_class({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True,
            })

            symbol = f'{coin}/USDT'

            if side == 'buy':
                # Market buy with USDT amount
                # CCXT createMarketBuyOrderWithCost or use quoteOrderQty
                try:
                    order = exchange_obj.create_order(
                        symbol, 'market', 'buy', None,
                        params={'quoteOrderQty': usdt_amount}
                    )
                except Exception:
                    # Fallback: calculate quantity from price
                    ticker = exchange_obj.fetch_ticker(symbol)
                    price = ticker['last']
                    qty = usdt_amount / price
                    order = exchange_obj.create_order(
                        symbol, 'market', 'buy', qty
                    )
            else:
                # Market sell quantity
                order = exchange_obj.create_order(
                    symbol, 'market', 'sell', usdt_amount
                )

            # Extract fill details from order response
            fill_price = float(order.get('average') or
                               order.get('price') or
                               order.get('fills', [{}])[0].get('price', 0))

            filled_qty = float(order.get('filled') or
                               order.get('amount', 0))

            # Fee from order response
            fee_usdt = 0.0
            if order.get('fees'):
                for f in order['fees']:
                    fee_usdt += float(f.get('cost', 0))
            elif order.get('fee'):
                fee_usdt = float(order['fee'].get('cost', 0))
            else:
                # Estimate from fill
                fee_rate = get_fee_rate(exc_name)
                fee_usdt = usdt_amount * fee_rate

            order_id = str(order.get('id', ''))

            return OrderResult(
                success=True,
                side=side,
                coin=coin,
                fill_price=fill_price,
                quantity=round(filled_qty, 8),
                fee_usdt=round(fee_usdt, 8),
                order_id=order_id,
                price_age_ms=None,  # Live = no Redis age
                timestamp=datetime.now(timezone.utc).isoformat()
            )

        except ccxt.InsufficientFunds:
            return OrderResult(
                success=False, side=side, coin=coin,
                fill_price=0, quantity=0, fee_usdt=0,
                order_id='', price_age_ms=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error='insufficient_funds'
            )
        except ccxt.NetworkError as e:
            return OrderResult(
                success=False, side=side, coin=coin,
                fill_price=0, quantity=0, fee_usdt=0,
                order_id='', price_age_ms=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=f'network_error: {e}'
            )
        except ccxt.ExchangeError as e:
            return OrderResult(
                success=False, side=side, coin=coin,
                fill_price=0, quantity=0, fee_usdt=0,
                order_id='', price_age_ms=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=f'exchange_error: {e}'
            )
        except Exception as e:
            return OrderResult(
                success=False, side=side, coin=coin,
                fill_price=0, quantity=0, fee_usdt=0,
                order_id='', price_age_ms=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=f'live_error: {e}'
            )
