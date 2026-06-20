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

load_dotenv('/home/averion/Averion/.env')

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


@dataclass
class LimitOrderResult:
    """Result of placing a Short DCA buyback limit order (ADDED June
    20 2026, first limit-order infrastructure in the platform - every
    other order type so far has been market-only)."""
    success:        bool
    order_id:        str = ''
    limit_price:     float = 0
    quantity:        float = 0
    usdt_reserved:   float = 0
    error:           Optional[str] = None

@dataclass
class LimitFillResult:
    """Result of checking whether a pending limit buyback has filled."""
    filled:          bool
    fill_price:      float = 0
    fill_quantity:   float = 0


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
    def place_short_sell(self, coin: str, quantity: float, wallet: dict, conn):
        """Sells `quantity` units of `coin` from a Short wallet
        (ADDED June 20 2026). Deliberately SEPARATE from place_order()
        - that function's sell branch assumes wallet.current_balance is
        USDT and credits proceeds into it. Short wallets hold COIN
        quantity in current_balance, not USDT - reusing place_order()
        here would incorrectly add USDT into a coin-denominated
        balance. Proceeds (USDT) are NOT credited to any wallet here -
        the caller tracks them on the position's
        short_buyback_reserved_usdt field instead, matching the locked
        spec's 'reserved, untouchable by the queue' requirement."""
        try:
            raw_price, age_ms = get_redis_price(coin)
            fill_price = raw_price * 0.9995  # 0.05% below, same spread as normal sells
            fee_rate = get_fee_rate(wallet.get('exchange_name', 'mexc'))
            gross_usdt = quantity * fill_price
            fee_usdt = gross_usdt * fee_rate

            cur = conn.cursor()
            cur.execute("""
                SELECT current_balance FROM virtual_wallets WHERE id=%s FOR UPDATE
            """, (wallet['id'],))
            row = cur.fetchone()
            if not row:
                return OrderResult(
                    success=False, side='sell', coin=coin,
                    fill_price=fill_price, quantity=0, fee_usdt=0,
                    order_id='', price_age_ms=age_ms,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    error='Wallet not found'
                )
            available_coin = float(row[0])
            if available_coin < quantity:
                return OrderResult(
                    success=False, side='sell', coin=coin,
                    fill_price=fill_price, quantity=0, fee_usdt=0,
                    order_id='', price_age_ms=age_ms,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    error='insufficient_coin'
                )

            cur.execute("""
                UPDATE virtual_wallets
                SET current_balance = current_balance - %s, updated_at=NOW()
                WHERE id = %s
            """, (quantity, wallet['id']))

            order_id = f'paper_short_sell_{int(time.time() * 1000)}'
            return OrderResult(
                success=True, side='sell', coin=coin,
                fill_price=fill_price, quantity=round(quantity, 8),
                fee_usdt=round(fee_usdt, 8), order_id=order_id,
                price_age_ms=age_ms,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except ValueError as e:
            return OrderResult(
                success=False, side='sell', coin=coin,
                fill_price=0, quantity=0, fee_usdt=0,
                order_id='', price_age_ms=None,
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=str(e)
            )

    def place_limit_buyback(self, position_id, coin, limit_price, quantity, wallet, conn):
        """Records a pending buyback limit order (paper simulation -
        no real exchange order, just tracked in short_buyback_orders).
        Fill is checked separately each cycle via check_limit_fill()."""
        usdt_reserved = quantity * limit_price
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO short_buyback_orders
                (position_id, exchange_order_id, limit_price, quantity,
                 usdt_reserved, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            RETURNING id
        """, (position_id, f'paper_limit_{int(time.time()*1000)}',
              limit_price, quantity, usdt_reserved))
        order_id = cur.fetchone()[0]
        return LimitOrderResult(
            success=True, order_id=str(order_id),
            limit_price=limit_price, quantity=quantity,
            usdt_reserved=usdt_reserved
        )

    def check_limit_fill(self, order_id, coin, wallet, conn):
        """Paper simulation: a limit BUY fills when price drops to or
        below the limit price (mirrors a real exchange limit buy)."""
        cur = conn.cursor()
        cur.execute("""
            SELECT limit_price, quantity, status FROM short_buyback_orders
            WHERE id=%s
        """, (order_id,))
        row = cur.fetchone()
        if not row or row[2] != 'pending':
            return LimitFillResult(filled=False)
        limit_price, quantity, status = row
        try:
            current_price, _ = get_redis_price(coin)
        except ValueError:
            return LimitFillResult(filled=False)
        if current_price <= float(limit_price):
            cur.execute("""
                UPDATE short_buyback_orders SET status='filled', filled_at=NOW()
                WHERE id=%s
            """, (order_id,))
            return LimitFillResult(filled=True, fill_price=float(limit_price),
                                    fill_quantity=float(quantity))
        return LimitFillResult(filled=False)

    def cancel_limit_order(self, order_id, coin, wallet, conn):
        cur = conn.cursor()
        cur.execute("""
            UPDATE short_buyback_orders SET status='cancelled', cancelled_at=NOW()
            WHERE id=%s AND status='pending'
        """, (order_id,))
        return True

    def credit_buyback_to_wallet(self, wallet_id, quantity, conn):
        """Increases the Short wallet's coin balance by the
        bought-back quantity, once a buyback fill is confirmed (ADDED
        June 20 2026). Separate step from check_limit_fill() since the
        caller decides when to actually apply the wallet credit -
        keeps the 'did it fill' check and 'apply the result' action
        independently callable/testable."""
        cur = conn.cursor()
        cur.execute("""
            UPDATE virtual_wallets
            SET current_balance = current_balance + %s, updated_at=NOW()
            WHERE id = %s
        """, (quantity, wallet_id))
        return True


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

    def place_short_sell(self, coin, quantity, wallet, conn):
        """Delegates to the existing place_order() - LiveAdapter's
        sell logic already never touches wallet balance directly
        (real wallet sync handles it separately), so no Short-specific
        version is needed here, unlike PaperAdapter."""
        return self.place_order('sell', coin, quantity, wallet, conn)

    def _get_exchange_obj(self, wallet, conn):
        """Shared credential-loading helper for the limit-order
        methods below, mirroring place_order()'s existing pattern."""
        cur = conn.cursor()
        cur.execute("""
            SELECT e.exchange, e.api_key, e.secret
            FROM exchanges e WHERE e.id = %s
        """, (wallet['exchange_id'],))
        exc_row = cur.fetchone()
        if not exc_row:
            raise ValueError('Exchange not found')
        exc_name, api_key, secret = exc_row
        from exchanges import decrypt
        api_key = decrypt(api_key)
        secret = decrypt(secret)
        exchange_class = getattr(ccxt, exc_name.lower())
        return exchange_class({
            'apiKey': api_key, 'secret': secret, 'enableRateLimit': True,
        })

    def place_limit_buyback(self, position_id, coin, limit_price, quantity, wallet, conn):
        """Places a real limit buy order on the exchange (ADDED June
        20 2026, first limit-order placement in the platform)."""
        try:
            exchange_obj = self._get_exchange_obj(wallet, conn)
            symbol = f'{coin}/USDT'
            order = exchange_obj.create_limit_buy_order(symbol, quantity, limit_price)
            return LimitOrderResult(
                success=True, order_id=str(order.get('id', '')),
                limit_price=limit_price, quantity=quantity,
                usdt_reserved=quantity * limit_price
            )
        except Exception as e:
            return LimitOrderResult(success=False, error=f'limit_order_error: {e}')

    def check_limit_fill(self, order_id, coin, wallet, conn):
        """Polls the real exchange for this limit order's status."""
        try:
            exchange_obj = self._get_exchange_obj(wallet, conn)
            symbol = f'{coin}/USDT'
            order = exchange_obj.fetch_order(order_id, symbol)
            status = order.get('status')
            if status == 'closed':  # CCXT convention: closed = fully filled
                return LimitFillResult(
                    filled=True,
                    fill_price=float(order.get('average') or order.get('price') or 0),
                    fill_quantity=float(order.get('filled') or 0)
                )
            return LimitFillResult(filled=False)
        except Exception as e:
            print(f'Limit fill check error: {e}')
            return LimitFillResult(filled=False)

    def cancel_limit_order(self, order_id, coin, wallet, conn):
        try:
            exchange_obj = self._get_exchange_obj(wallet, conn)
            symbol = f'{coin}/USDT'
            exchange_obj.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            print(f'Cancel limit order error: {e}')
            return False
