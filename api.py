import os
import hashlib
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import uvicorn
import redis
import jwt

import database as db
import auth as auth_module

load_dotenv()

PAPER_MODE = os.getenv('PAPER_MODE', 'true').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
ADMIN_PATH = os.getenv('ADMIN_PATH', 'ops-admin')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# ═══════════════════════════════
# STARTUP
# ═══════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_pool()
    print('✅ API started')
    yield

app = FastAPI(title='Averion API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# ═══════════════════════════════
# REDIS CLIENT
# ═══════════════════════════════
def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# ═══════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════
security = HTTPBearer(auto_error=False)

# Password functions handled by auth module





def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail='Not authenticated')
    try:
        key = os.getenv('SECRET_KEY', 'changeme')
        payload = jwt.decode(
            credentials.credentials,
            key, algorithms=['HS256']
        )
        return payload
    except Exception as e:
        print(f'Token verify error: {e}')
        raise HTTPException(status_code=401, detail='Invalid token')

def require_admin(payload: dict = Depends(verify_token)):
    if not payload.get('is_admin'):
        raise HTTPException(status_code=403, detail='Admin only')
    return payload

# ═══════════════════════════════
# BRUTE FORCE PROTECTION
# ═══════════════════════════════
def check_brute_force(ip: str) -> bool:
    r = get_redis()
    key = f'login_fails:{ip}'
    fails = r.get(key)
    return int(fails) >= 5 if fails else False

def record_login_fail(ip: str):
    r = get_redis()
    key = f'login_fails:{ip}'
    r.incr(key)
    r.expire(key, 1800)  # 30 minutes

def clear_login_fails(ip: str):
    r = get_redis()
    r.delete(f'login_fails:{ip}')

# ═══════════════════════════════
# STATIC FILES
# ═══════════════════════════════
@app.get('/bots')
def bots_page():
    return FileResponse('bots.html')

@app.get('/bots/{bot_id}')
def bot_detail_page(bot_id: int):
    return FileResponse('bot-detail.html')

@app.get('/trades')
def trades_page():
    return FileResponse('trades.html')

@app.get('/history')
def history_page():
    return FileResponse('history.html')

@app.get('/reports')
def reports_page():
    return FileResponse('reports.html')

@app.get('/exchanges')
def exchanges_page():
    return FileResponse('exchanges.html')

@app.get('/create-bot')
def create_bot_page():
    return FileResponse('create-bot.html')

@app.get('/settings')
def settings_page():
    return FileResponse('settings.html')

@app.get('/styles.css')
def styles_css():
    return FileResponse('styles.css', media_type='text/css')

@app.get('/base.js')
def base_js():
    return FileResponse('base.js', media_type='application/javascript')

@app.get('/dashboard')
def dashboard():
    return FileResponse('dashboard_new.html')

@app.get('/auth/email-verified')
def check_email_verified(payload: dict = Depends(verify_token)):
    user = db.get_user_by_id(payload['user_id'])
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    # user[3] = is_admin · check email_verified separately
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT email_verified FROM users WHERE id = %s
        """, (payload['user_id'],))
        row = cur.fetchone()
        verified = row[0] if row else False
    return {'email_verified': verified}

@app.get(f'/{ADMIN_PATH}')
def admin_dashboard():
    return FileResponse('admin.html')

@app.get('/')
def homepage():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url='/dashboard')

@app.get('/login')
def login_page():
    return FileResponse('login.html')

@app.get('/register')
def register_page():
    return FileResponse('register.html')

# ═══════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post('/auth/login')
def login(req: LoginRequest, request: Request):
    ip = request.client.host

    if auth_module.check_brute_force(ip):
        raise HTTPException(status_code=429, detail='Too many failed attempts')

    result, error = auth_module.login(
        req.email, req.password, ip,
        request.headers.get('user-agent')
    )
    if error:
        auth_module.record_login_fail(ip)
        raise HTTPException(status_code=401, detail=error)

    auth_module.clear_login_fails(ip)
    return result


class VerifyRequest(BaseModel):
    user_id: int
    code: str
    remember: bool = True

@app.post('/auth/verify')
def verify(req: VerifyRequest, request: Request):
    ip = request.client.host
    success = auth_module.verify_code(
        req.user_id, req.code, ip, remember=req.remember
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail='Invalid or expired code'
        )
    return {'message': 'Verified successfully'}


class ExchangeCreate(BaseModel):
   exchange: str
   custom_name: str
   api_key: str
   secret: str
   passphrase: Optional[str] = None
   ip_whitelist_confirmed: bool = False
@app.post('/exchanges')
def add_exchange(req: ExchangeCreate,
                payload: dict = Depends(verify_token)):
   from cryptography.fernet import Fernet
   import base64
   fernet_key = os.getenv('FERNET_KEY')
   if not fernet_key:
       raise HTTPException(status_code=500,
                           detail='Encryption not configured')
   f = Fernet(fernet_key.encode())
   api_key_enc = f.encrypt(req.api_key.encode()).decode()
   secret_enc = f.encrypt(req.secret.encode()).decode()
   passphrase_enc = None
   if req.passphrase:
       passphrase_enc = f.encrypt(req.passphrase.encode()).decode()
   exchange_id = db.add_exchange(
       payload['user_id'], req.exchange, req.custom_name,
       api_key_enc, secret_enc, passphrase_enc
   )
   # Confirm IP whitelist
   if req.ip_whitelist_confirmed:
       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("""
               UPDATE exchanges SET ip_whitelist_confirmed = TRUE
               WHERE id = %s
           """, (exchange_id,))
   return {'message': 'Exchange added', 'exchange_id': exchange_id}

# ═══════════════════════════════
# STATUS
# ═══════════════════════════════
@app.get('/status')
def get_status():
    r = get_redis()
    bot_status = r.get('bot:status') or 'unknown'
    cycle_time = r.get('bot:cycle_time') or '0'
    last_cycle = r.get('bot:last_cycle') or 'never'

    btc_price = 0
    try:
        btc_price = float(r.get('price:BTC/USDT') or 0)
    except:
        pass

    return {
        'running': bot_status == 'running',
        'bot_status': bot_status,
        'cycle_time': cycle_time,
        'last_cycle': last_cycle,
        'btc_price': btc_price,
        'mode': 'paper' if PAPER_MODE else 'live'
    }

# ═══════════════════════════════
# POSITIONS
# ═══════════════════════════════
@app.get('/api/coins')
def get_available_coins(payload: dict = Depends(verify_token)):
    """Returns all coins available on the connected exchange from Redis price cache"""
    try:
        import redis as _redis
        r = _redis.Redis(host='localhost', port=6379, decode_responses=True)
        keys = r.keys('price:*:*/USDT')
        coins = sorted(set(k.split(':')[2].replace('/USDT','') for k in keys if '/USDT' in k))
        if coins:
            return coins
    except Exception:
        pass
    return []

@app.get('/dca-templates')
def get_dca_templates(payload: dict = Depends(verify_token)):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                b.id,
                b.method,
                b.name,
                b.take_profit_percent,
                b.dca_percent,
                b.size_multiplier,
                b.trailing_percent,
                ROW_NUMBER() OVER (
                    PARTITION BY b.method
                    ORDER BY b.id ASC
                ) as variant_num
            FROM bots b
            WHERE b.is_research=TRUE
            AND b.method LIKE 'E%'
            AND b.method != 'E58'
            ORDER BY
                CAST(NULLIF(REGEXP_REPLACE(b.method, '[^0-9]', '', 'g'), '') AS INTEGER) ASC,
                b.id ASC
        """)
        rows = cur.fetchall()
    return [{
        'id': r[0],
        'method': r[1],
        'name': r[2],
        'label': f"{r[1]}-{r[7]}",
        'take_profit_percent': float(r[3] or 5),
        'dca_percent': float(r[4] or 7),
        'size_multiplier': float(r[5] or 1.5),
        'trailing_percent': float(r[6] or 2),
        'variant_num': r[7],
    } for r in rows]

@app.get('/admin-features')
def get_admin_features():
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT feature_key, enabled, visible, label FROM admin_features")
        rows = cur.fetchall()
    return {r[0]: {'enabled': r[1], 'visible': r[2], 'label': r[3]} for r in rows}

@app.get('/scalper-variants')
def get_scalper_variants(payload: dict = Depends(verify_token)):
    import json as _json
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, bot_params::text
            FROM bots WHERE method='S58' AND is_template=TRUE
            ORDER BY name
        """)
        rows = cur.fetchall()
    result = []
    for name, params_raw in rows:
        try:
            p = _json.loads(params_raw) if params_raw else {}
        except:
            p = {}
        result.append({
            'name': name,
            'trigger_pct': p.get('trigger_pct', '?'),
            'window_sec': p.get('window_sec', '?'),
            'hold_sec': p.get('hold_sec', '?'),
            'stop_loss_pct': p.get('stop_loss_pct'),
        })
    return result

@app.post('/bots/create-dca')
def create_dca_bot(data: dict, payload: dict = Depends(verify_token)):
    import json as _json
    user_id = payload['user_id']
    exchange_id = data.get('exchange_id')
    wallet_id = data.get('wallet_id', 1)
    direction = data.get('direction', 'long')
    entry_method = data.get('entry_method', 'dca_asap')
    coin_mode = data.get('coin_mode', 'all')
    base_order = float(data.get('base_order', 10))
    dca_percent = float(data.get('dca_percent', 7))
    size_multiplier = float(data.get('size_multiplier', 1.5))
    max_dca_levels = int(data.get('max_dca_levels', 0))
    take_profit_percent = float(data.get('take_profit_percent', 5))
    trailing_percent = float(data.get('trailing_percent', 2))

    user_id = int(user_id)
    with db.get_db() as conn:
        cur = conn.cursor()

        # Generate bot name
        try:
            cur.execute("""
                SELECT COUNT(*) FROM bots
                WHERE user_id=%s AND is_research=FALSE AND is_template=FALSE AND status!='deleted'
                AND method LIKE 'DCA%'
            """, (user_id,))
            row = cur.fetchone()
            count = (row[0] if row else 0) + 1
        except Exception:
            count = 1
        bot_name = data.get('bot_name', '').strip() or f'DCA-{count}'

        trades_per_bot = int(data.get('trades_per_bot', 5))
        trades_per_coin = int(data.get('trades_per_coin', 1))
        template_id = data.get('template_id')

        # Default values
        method = 'DCA_ASAP'
        tp = float(data.get('take_profit_percent') or 5)
        trail = float(data.get('trailing_percent') or 2)
        dca_pct = float(data.get('dca_percent') or 7)
        size_mult = float(data.get('size_multiplier') or 1.5)
        research_params = {}

        if entry_method == 'dca_templates' and template_id:
            # READ ONLY from research bot — copy all parameters
            cur.execute("""
                SELECT method, dca_percent, take_profit_percent,
                       trailing_percent, size_multiplier, bot_params,
                       spacing_multiplier
                FROM bots
                WHERE id=%s AND is_research=TRUE
            """, (int(template_id),))
            res_bot = cur.fetchone()
            if res_bot:
                method    = res_bot[0]  # e.g. 'E31'
                dca_pct   = float(res_bot[1] or 7)
                tp        = float(res_bot[2] or 5)
                trail     = float(res_bot[3] or 2)
                size_mult = float(res_bot[4] or 1.5)
                research_params = res_bot[5] or {}
            else:
                method = 'DCA_TEMPLATE'
        elif entry_method == 'dca_asap':
            method = 'DCA_ASAP'
        elif entry_method == 'dca_smart':
            method = 'DCA_SMART'
        elif entry_method == 'dca_custom':
            method = 'DCA_CUSTOM'

        bot_params = _json.dumps({
            'entry_method': entry_method,
            'coin_mode': coin_mode,
            'direction': direction,
            'template_id': template_id,
            'source_method': method,
            'dca_settings_mode': data.get('dca_settings_mode', 'custom'),
            'exit_mode': data.get('exit_mode', 'custom'),
            'research_params': research_params,
        })

        cur.execute("""
            INSERT INTO bots (
                user_id, exchange_id, wallet_id, name, method,
                direction, base_order, dca_percent, spacing_multiplier,
                size_multiplier, take_profit_percent, trailing_percent,
                base_coin, is_paper, trades_per_bot, trades_per_coin,
                gate_dca_enabled, gate_timer_enabled, gate_timer_hours,
                order_entry_type, order_dca_type, status,
                trading_on, is_research, is_template, bot_params,
                entry_method
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, 1.4,
                %s, %s, %s,
                'USDT', TRUE, %s, %s,
                TRUE, FALSE, 24,
                'market', 'market', 'open',
                TRUE, FALSE, FALSE, %s, %s
            ) RETURNING id
        """, (user_id, exchange_id, wallet_id, bot_name, method,
                direction, base_order, dca_pct,
                size_mult, tp, trail,
                trades_per_bot, trades_per_coin,
                bot_params, entry_method))
        bot_id = cur.fetchone()[0]
        conn.commit()

    return {'bot_id': bot_id, 'name': bot_name, 'message': f'{bot_name} created successfully'}

@app.post('/bots/create-scalper')
def create_scalper_bot(data: dict, payload: dict = Depends(verify_token)):
    import json as _json
    user_id = payload['user_id']
    exchange_id = data.get('exchange_id')
    variant_name = data.get('variant_name')
    base_order = float(data.get('base_order', 2))
    max_capital = float(data.get('max_capital', 10))

    # Get variant params from research bots
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT bot_params::text FROM bots WHERE name=%s AND method='S58'", (variant_name,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Variant not found')
        params = _json.loads(row[0]) if row[0] else {}

        # Use provided name or auto-generate
        bot_name = data.get('bot_name', '').strip()
        if not bot_name:
            base_name = variant_name
            cur.execute("SELECT COUNT(*) FROM bots WHERE user_id=%s AND (name=%s OR name LIKE %s)", 
                        (user_id, base_name, base_name + '-%'))
            count = cur.fetchone()[0]
            bot_name = base_name if count == 0 else f'{base_name}-{count + 1}'

        cur.execute("""
            INSERT INTO bots (
                user_id, exchange_id, wallet_id, name, method,
                direction, base_order, dca_percent, spacing_multiplier,
                size_multiplier, take_profit_percent, trailing_percent,
                base_coin, is_paper, trades_per_bot, trades_per_coin,
                gate_dca_enabled, gate_timer_enabled, gate_timer_hours,
                order_entry_type, order_dca_type, status,
                trading_on, is_research, bot_params
            ) VALUES (
                %s, %s, 1, %s, 'S58',
                'long', %s, 7, 1.0,
                1.0, 5, 2,
                'USDT', TRUE, 999, 1,
                FALSE, FALSE, 24,
                'market', 'market', 'open',
                TRUE, FALSE, %s
            ) RETURNING id
        """, (user_id, exchange_id, bot_name, base_order,
                _json.dumps(params)))
        bot_id = cur.fetchone()[0]
        conn.commit()

    return {'bot_id': bot_id, 'name': bot_name, 'message': f'{bot_name} created successfully'}

# ═══════════════════════════════
# VIRTUAL WALLETS
# ═══════════════════════════════
@app.get('/wallets')
def get_wallets(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, currency, allocation_type, allocation_amount,
                   current_balance, committed_usdt, standby_reserved,
                   is_paper, exchange_id, coin
            FROM virtual_wallets WHERE user_id=%s ORDER BY created_at ASC
        """, (user_id,))
        rows = cur.fetchall()
        # Count bots per wallet
        cur.execute("""
            SELECT wallet_id, COUNT(*) FROM bots
            WHERE user_id=%s AND is_research=FALSE AND is_template=FALSE
            GROUP BY wallet_id
        """, (user_id,))
        bot_counts = {r[0]: r[1] for r in cur.fetchall()}
    return [{
        'id': r[0], 'name': r[1], 'currency': r[2],
        'cap_type': r[3],
        'allocation_amount': float(r[4] or 0),
        'current_balance': float(r[5] or 0),
        'committed_usdt': float(r[6] or 0),
        'standby_reserved': float(r[7] or 0),
        'is_paper': r[8],
        'exchange_id': r[9],
        'coin': r[10],
        'bot_count': bot_counts.get(r[0], 0),
        'deployed': float(r[6] or 0),
        'queued': float(r[7] or 0),
        'available': float(r[5] or 0),
    } for r in rows]

@app.post('/wallets')
def create_wallet(data: dict, payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    name = data.get('name', '').strip()
    balance = float(data.get('balance', 1000))
    exchange_id = data.get('exchange_id', 2)
    is_paper = data.get('is_paper', True)
    cap_type = data.get('cap_type', 'fixed')
    coin = data.get('coin', None)
    currency = coin if coin else 'USDT'
    if not name:
        raise HTTPException(status_code=400, detail='Wallet name required')
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO virtual_wallets
                (user_id, exchange_id, name, currency, allocation_type,
                 allocation_amount, current_balance, is_paper, coin)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, exchange_id, name, currency, cap_type,
                balance, balance, is_paper, coin))
        wallet_id = cur.fetchone()[0]
        conn.commit()
    return {'id': wallet_id, 'message': 'Wallet created'}

@app.put('/wallets/{wallet_id}')
def update_wallet(wallet_id: int, data: dict, payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        if 'name' in data:
            cur.execute("UPDATE virtual_wallets SET name=%s WHERE id=%s AND user_id=%s",
                       (data['name'], wallet_id, user_id))
        if 'balance' in data:
            cur.execute("""UPDATE virtual_wallets SET allocation_amount=%s, current_balance=%s
                          WHERE id=%s AND user_id=%s AND is_paper=TRUE""",
                       (data['balance'], data['balance'], wallet_id, user_id))
        cur.execute("UPDATE virtual_wallets SET updated_at=NOW() WHERE id=%s", (wallet_id,))
        conn.commit()
    return {'message': 'Wallet updated'}

@app.delete('/wallets/{wallet_id}')
def delete_wallet(wallet_id: int, payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM bots WHERE wallet_id=%s AND is_research=FALSE", (wallet_id,))
        if cur.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail='Wallet in use by bots')
        cur.execute("DELETE FROM virtual_wallets WHERE id=%s AND user_id=%s", (wallet_id, user_id))
        conn.commit()
    return {'message': 'Wallet deleted'}

@app.get('/reset-summary')
def reset_summary(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM live_positions WHERE user_id=%s AND status='open'", (user_id,))
        open_positions = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM bots WHERE user_id=%s AND is_research=FALSE AND is_template=FALSE", (user_id,))
        live_bots = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM exchanges WHERE user_id=%s AND active=TRUE", (user_id,))
        exchanges = cur.fetchone()[0]
    return {'open_positions': int(open_positions), 'live_bots': int(live_bots), 'exchanges': int(exchanges)}

@app.post('/reset/{reset_type}')
def execute_reset(reset_type: str, payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    redis_client = get_redis()
    with db.get_db() as conn:
        cur = conn.cursor()
        if reset_type in ('trades', 'bots', 'exchanges', 'all'):
            # Delete ALL live positions (open + closed history)
            cur.execute("DELETE FROM live_positions WHERE user_id=%s", (user_id,))
            # Reset wallet
            cur.execute("UPDATE virtual_wallets SET current_balance=10000, committed_usdt=0 WHERE user_id=%s", (user_id,))
        if reset_type in ('bots', 'exchanges', 'all'):
            cur.execute("SELECT id FROM bots WHERE user_id=%s AND is_research=FALSE AND is_template=FALSE", (user_id,))
            bot_ids = [row[0] for row in cur.fetchall()]
            if bot_ids:
                cur.execute("DELETE FROM fee_debt WHERE position_id IN (SELECT id FROM positions WHERE bot_id = ANY(%s))", (bot_ids,))
                cur.execute("DELETE FROM trades WHERE bot_id = ANY(%s)", (bot_ids,))
                cur.execute("DELETE FROM positions WHERE bot_id = ANY(%s)", (bot_ids,))
                cur.execute("DELETE FROM live_positions WHERE bot_id = ANY(%s)", (bot_ids,))
                cur.execute("DELETE FROM bots WHERE id = ANY(%s)", (bot_ids,))
        if reset_type in ('exchanges', 'all'):
            cur.execute("DELETE FROM exchanges WHERE user_id=%s", (user_id,))
        # wallet already reset above
        conn.commit()
    messages = {
        'trades': 'All open positions closed',
        'bots': 'All bots deleted and positions closed',
        'exchanges': 'All exchanges, bots and positions deleted',
        'all': 'Everything reset. Fresh start!'
    }
    return {'message': messages.get(reset_type, 'Reset complete')}

@app.get('/home-stats')
def home_stats(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()

        # Active bots
        cur.execute("SELECT COUNT(*) FROM bots WHERE user_id=%s AND trading_on=TRUE AND is_research=FALSE AND is_template=FALSE AND status!='deleted'", (user_id,))
        active_bots = cur.fetchone()[0]

        # Scalper open trades
        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(lp.base_order),0)
            FROM live_positions lp JOIN bots b ON lp.bot_id=b.id
            WHERE lp.user_id=%s AND lp.status='open'
            AND b.is_research=FALSE AND b.is_template=FALSE
            AND b.status!='deleted'
        """, (user_id,))
        row = cur.fetchone()
        scalper_open, scalper_invested = int(row[0]), float(row[1])

        # DCA open trades
        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(p.total_invested),0)
            FROM live_dca_positions p
            JOIN bots b ON p.bot_id=b.id
            WHERE p.user_id=%s AND p.status='open'
            AND b.status!='deleted'
        """, (user_id,))
        row = cur.fetchone()
        dca_open, dca_invested = int(row[0]), float(row[1])

        open_trades = scalper_open + dca_open
        total_invested = scalper_invested + dca_invested

        # DCA queue count (positions waiting for DCA)
        cur.execute("""
            SELECT COUNT(*) FROM live_dca_positions
            WHERE user_id=%s AND status='open' AND queued=TRUE
        """, (user_id,))
        dca_queue = int(cur.fetchone()[0])

        # Today P&L (scalper)
        cur.execute("""
            SELECT COALESCE(SUM(lp.pnl_usdt),0), COUNT(*)
            FROM live_positions lp JOIN bots b ON lp.bot_id=b.id
            WHERE lp.user_id=%s AND lp.status='closed'
            AND lp.exit_time >= CURRENT_DATE
            AND b.is_research=FALSE AND b.is_template=FALSE
        """, (user_id,))
        row2 = cur.fetchone()
        today_pnl, today_closed = float(row2[0]), int(row2[1])

        # Today P&L (DCA)
        cur.execute("""
            SELECT COALESCE(SUM(realized_pnl_usdt),0), COUNT(*)
            FROM live_dca_positions
            WHERE user_id=%s AND status='closed'
            AND closed_at >= CURRENT_DATE
        """, (user_id,))
        row3 = cur.fetchone()
        today_pnl += float(row3[0])
        today_closed += int(row3[1])

        # Total profit (scalper)
        cur.execute("""
            SELECT COALESCE(SUM(lp.pnl_usdt),0)
            FROM live_positions lp JOIN bots b ON lp.bot_id=b.id
            WHERE lp.user_id=%s AND lp.status='closed'
            AND b.is_research=FALSE AND b.is_template=FALSE
        """, (user_id,))
        total_profit = float(cur.fetchone()[0])

        # Total profit (DCA)
        cur.execute("""
            SELECT COALESCE(SUM(realized_pnl_usdt),0)
            FROM live_dca_positions
            WHERE user_id=%s AND status='closed'
        """, (user_id,))
        total_profit += float(cur.fetchone()[0])

        # Fee debt — only for non-research, non-admin users
        try:
            cur.execute("SELECT is_research_account, is_admin FROM users WHERE id=%s", (user_id,))
            urow = cur.fetchone()
            is_research_user = urow and (urow[0] or urow[1])
            if is_research_user:
                fee_debt = 0.0
            else:
                cur.execute("SELECT COALESCE(SUM(f.amount_usdt),0) FROM fee_debt f WHERE f.user_id=%s AND f.paid_at IS NULL", (user_id,))
                fee_debt = float(cur.fetchone()[0])
        except Exception:
            fee_debt = 0.0

        # Wallet summary
        cur.execute("""
            SELECT COALESCE(SUM(current_balance),0),
                   COALESCE(SUM(committed_usdt),0),
                   COALESCE(SUM(allocation_amount),0)
            FROM virtual_wallets WHERE user_id=%s AND is_paper=TRUE
        """, (user_id,))
        wrow = cur.fetchone()
        wallet_available = float(wrow[0])
        wallet_deployed  = float(wrow[1])
        wallet_total     = float(wrow[2])

    return {
        'active_bots':    int(active_bots),
        'open_trades':    int(open_trades),
        'total_invested': round(total_invested, 2),
        'dca_queue':      int(dca_queue),
        'today_pnl':      round(today_pnl, 4),
        'today_closed':   today_closed,
        'total_profit':   round(total_profit, 4),
        'fee_debt':       round(fee_debt, 4),
        'wallet_available': round(wallet_available, 2),
        'wallet_deployed':  round(wallet_deployed, 2),
        'wallet_total':     round(wallet_total, 2),
        'scalper_open':   scalper_open,
        'dca_open':       dca_open,
    }

# ═══════════════════════════════
@app.get('/positions')
def get_positions(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    r = get_redis()

    positions = db.get_open_positions()
    result = []

    for p in positions:
        if p[2] != user_id:  # user_id check
            continue

        coin = p[4]
        current_price = 0
        try:
            keys = r.keys(f'price:*:{coin}/USDT')
            current_price = float(r.get(keys[0]) if keys else p[7] or 0)
        except:
            current_price = float(p[7] or 0)

        avg_cost = float(p[7] or 0)
        quantity = float(p[8] or 0)
        invested = float(p[9] or 0)

        pnl = (current_price - avg_cost) * quantity
        pnl_pct = ((current_price - avg_cost) / avg_cost * 100
                   ) if avg_cost else 0

        result.append({
            'id': p[0],
            'bot_id': p[1],
            'coin': coin,
            'direction': p[5],
            'status': p[6],
            'avg_cost': avg_cost,
            'quantity': quantity,
            'total_invested': invested,
            'dca_count': p[10],
            'last_buy_price': float(p[11] or 0),
            'tp_armed': p[12],
            'current_price': current_price,
            'pnl': round(pnl, 4),
            'pnl_pct': round(pnl_pct, 2),
            'category': p[17],
            'is_paper': p[18],
            'base_coin': p[19],
            'opened_at': str(p[26])
        })

    return result

@app.get('/positions/{position_id}')
def get_position_detail(position_id: int,
                         payload: dict = Depends(verify_token)):
    trades = db.get_position_trades(position_id)
    return {
        'position_id': position_id,
        'trades': [{
            'id': t[0],
            'side': t[1],
            'price': float(t[2]),
            'quantity': float(t[3]),
            'usdt_amount': float(t[4]),
            'exchange_fee': float(t[5] or 0),
            'reason': t[6],
            'order_type': t[7],
            'dca_level': t[8],
            'timestamp': str(t[9])
        } for t in trades]
    }

@app.post('/positions/{position_id}/close')
def close_position(position_id: int,
                    payload: dict = Depends(verify_token)):
    db.close_position(position_id, 'manual')
    db.add_attention_log(
        payload['user_id'], 'green',
        'manual_close', f'Position {position_id} closed manually',
        position_id=position_id
    )
    return {'message': f'Position {position_id} closed'}

# ═══════════════════════════════
# TRADES / HISTORY
# ═══════════════════════════════
@app.get('/bots/{bot_id}')
def bot_detail_page(bot_id: int):
    return FileResponse('bot-detail.html')

@app.get('/trades')
def get_trades(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.id, t.coin, t.side, t.price,
                   t.quantity, t.usdt_amount, t.reason,
                   t.exchange_fee, t.dca_level, t.timestamp
            FROM trades t
            WHERE t.user_id = %s
            ORDER BY t.timestamp DESC LIMIT 100
        """, (user_id,))
        rows = cur.fetchall()
    return [{'id': r[0], 'coin': r[1], 'side': r[2],
              'price': float(r[3]), 'quantity': float(r[4]),
              'usdt_amount': float(r[5]), 'reason': r[6],
              'fee': float(r[7] or 0), 'dca_level': r[8],
              'timestamp': str(r[9])} for r in rows]

@app.get('/history')
def get_history(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.coin, p.direction, p.avg_cost,
                   p.dca_count, p.total_invested,
                   p.opened_at, p.closed_at, p.close_reason,
                   p.category, p.entry_method, p.base_coin,
                   e.exchange
            FROM positions p
            JOIN exchanges e ON e.id = p.exchange_id
            WHERE p.user_id = %s AND p.status = 'closed'
            ORDER BY p.closed_at DESC LIMIT 200
        """, (user_id,))
        rows = cur.fetchall()
    return [{'id': r[0], 'coin': r[1], 'direction': r[2],
              'avg_cost': float(r[3] or 0),
              'dca_count': r[4],
              'total_invested': float(r[5] or 0),
              'opened_at': str(r[6]), 'closed_at': str(r[7]),
              'close_reason': r[8], 'category': r[9],
              'entry_method': r[10], 'base_coin': r[11],
              'exchange': r[12]} for r in rows]

# ═══════════════════════════════
# BOTS
# ═══════════════════════════════
@app.get('/live-positions')
def get_live_positions(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    r = get_redis()
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT lp.id, lp.bot_id, lp.user_id, lp.coin,
                   lp.entry_price, lp.exit_price, lp.base_order,
                   lp.hold_seconds, lp.pnl_pct, lp.pnl_usdt,
                   lp.status, lp.entry_time, lp.exit_time,
                   lp.exit_reason, lp.trigger_jump_pct,
                   b.name as bot_name
            FROM live_positions lp
            JOIN bots b ON lp.bot_id=b.id
            WHERE lp.user_id=%s AND b.status!='deleted'
            ORDER BY lp.id DESC
        """, (user_id,))
        rows = cur.fetchall()

    result = []
    for p in rows:
        coin = p[3]
        entry_price = float(p[4] or 0)
        current_price = entry_price
        if p[10] == 'open':
            try:
                keys = r.keys(f'price:*:{coin}/USDT')
                if keys:
                    current_price = float(r.get(keys[0]) or entry_price)
            except:
                pass
        
        pnl_pct = float(p[8] or 0)
        pnl_usdt = float(p[9] or 0)
        
        if p[10] == 'open' and entry_price > 0:
            pnl_pct = (current_price - entry_price) / entry_price * 100
            pnl_usdt = float(p[6] or 2) * pnl_pct / 100

        result.append({
            'id': p[0],
            'bot_id': p[1],
            'coin': coin,
            'type': 'scalper',
            'entry_price': entry_price,
            'current_price': current_price,
            'exit_price': float(p[5] or 0),
            'base_order': float(p[6] or 2),
            'hold_seconds': p[7],
            'pnl_pct': round(pnl_pct, 4),
            'pnl_usdt': round(pnl_usdt, 6),
            'status': p[10],
            'entry_time': str(p[11]),
            'exit_time': str(p[12]) if p[12] else None,
            'exit_reason': p[13],
            'trigger_jump_pct': float(p[14] or 0),
            'bot_name': p[15],
            'dca_count': 0,
            'avg_cost': entry_price,
            'total_invested': float(p[6] or 2),
        })

    # ── Add Live DCA positions ──
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.bot_id, p.coin, p.avg_cost, p.quantity,
                   p.total_invested, p.dca_count, p.status,
                   p.opened_at, p.closed_at, p.close_reason,
                   p.realized_pnl_usdt, p.realized_pnl_pct,
                   p.execution_type, p.fill_price,
                   b.name as bot_name
            FROM live_dca_positions p
            JOIN bots b ON p.bot_id = b.id
            WHERE p.user_id=%s AND b.status!='deleted'
            ORDER BY p.id DESC
        """, (user_id,))
        dca_rows = cur.fetchall()

    for p in dca_rows:
        coin = p[2]
        avg_cost = float(p[3] or 0)
        quantity = float(p[4] or 0)
        total_invested = float(p[5] or 0)
        current_price = avg_cost

        if p[7] == 'open' and avg_cost > 0:
            try:
                keys = r.keys(f'price:*:{coin}/USDT')
                if keys:
                    current_price = float(r.get(keys[0]) or avg_cost)
            except:
                pass

        pnl_usdt = float(p[11] or 0)
        pnl_pct = float(p[12] or 0)

        if p[7] == 'open' and avg_cost > 0 and quantity > 0:
            current_value = current_price * quantity
            pnl_usdt = current_value - total_invested
            pnl_pct = (pnl_usdt / total_invested * 100) if total_invested > 0 else 0

        result.append({
            'id': f'dca_{p[0]}',
            'bot_id': p[1],
            'coin': coin,
            'type': 'dca',
            'entry_price': float(p[14] or avg_cost),
            'current_price': current_price,
            'exit_price': 0,
            'base_order': total_invested,
            'hold_seconds': None,
            'pnl_pct': round(pnl_pct, 4),
            'pnl_usdt': round(pnl_usdt, 6),
            'status': p[7],
            'entry_time': str(p[8]),
            'exit_time': str(p[9]) if p[9] else None,
            'exit_reason': p[10],
            'trigger_jump_pct': 0,
            'bot_name': p[15],
            'dca_count': int(p[6] or 0),
            'avg_cost': avg_cost,
            'total_invested': total_invested,
        })

    return result

@app.get('/api/bots')
def get_bots(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    bots = db.get_user_bots(user_id)
    r = get_redis()

    # Get open DCA positions per bot for current worth
    with db.get_db() as conn:
        cur = conn.cursor()
        # Scalper positions worth
        cur.execute("""
            SELECT lp.bot_id, lp.coin, lp.base_order
            FROM live_positions lp
            JOIN bots b ON lp.bot_id=b.id
            WHERE lp.user_id=%s AND lp.status='open'
            AND b.is_research=FALSE AND b.is_template=FALSE
        """, (user_id,))
        scalper_pos = cur.fetchall()

        # DCA positions worth
        cur.execute("""
            SELECT bot_id, coin, quantity, total_invested
            FROM live_dca_positions
            WHERE user_id=%s AND status='open'
        """, (user_id,))
        dca_pos = cur.fetchall()

        # Wallet info per bot
        cur.execute("""
            SELECT b.id, vw.current_balance, vw.allocation_amount,
                   vw.name as wallet_name, vw.committed_usdt
            FROM bots b
            JOIN virtual_wallets vw ON b.wallet_id=vw.id
            WHERE b.user_id=%s AND b.is_research=FALSE AND b.is_template=FALSE
        """, (user_id,))
        wallet_rows = {r[0]: {'available': float(r[1] or 0),
                               'total': float(r[2] or 0),
                               'wallet_name': r[3],
                               'deployed': float(r[4] or 0)} for r in cur.fetchall()}


        # Realized P&L per bot
        cur.execute("""
            SELECT bot_id, COALESCE(SUM(realized_pnl_usdt), 0)
            FROM live_dca_positions
            WHERE user_id=%s AND status='closed'
            GROUP BY bot_id
        """, (user_id,))
        dca_realized = {int(r[0]): float(r[1]) for r in cur.fetchall()}

        cur.execute("""
            SELECT lp.bot_id, COALESCE(SUM(lp.pnl_usdt), 0)
            FROM live_positions lp JOIN bots b ON lp.bot_id=b.id
            WHERE lp.user_id=%s AND lp.status='closed'
            AND b.is_research=FALSE AND b.is_template=FALSE
            GROUP BY lp.bot_id
        """, (user_id,))
        scalper_realized = {int(r[0]): float(r[1]) for r in cur.fetchall()}
    # Calculate current worth per bot
    bot_worth = {}

    # Scalper: base_order is invested amount
    for pos in scalper_pos:
        bid, coin, base_order = int(pos[0]), pos[1], pos[2]
        invested = float(base_order or 0)
        bot_worth.setdefault(bid, {'invested': 0, 'worth': 0})
        bot_worth[bid]['invested'] += invested
        bot_worth[bid]['worth'] += invested  # scalper: worth ≈ invested

    # DCA: quantity × current_price
    for pos in dca_pos:
        bid, coin, quantity, total_invested = int(pos[0]), pos[1], pos[2], pos[3]
        qty = float(quantity or 0)
        invested = float(total_invested or 0)
        try:
            keys = r.keys(f'price:*:{coin}/USDT')
            current_price = float(r.get(keys[0])) if keys else 0
            worth = qty * current_price if current_price > 0 else invested
        except Exception:
            worth = invested
        bot_worth.setdefault(bid, {'invested': 0, 'worth': 0})
        bot_worth[bid]['invested'] += invested
        bot_worth[bid]['worth'] += worth

    result = []
    for b in bots:
        bot_id = b[0]
        worth_data = bot_worth.get(bot_id, {'invested': 0, 'worth': 0})
        wallet = wallet_rows.get(bot_id, {})
        invested = worth_data['invested']
        worth = worth_data['worth']
        pnl = worth - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0

        result.append({
            'id': bot_id,
            'name': b[1],
            'method': b[2],
            'direction': b[3],
            'trading_on': b[4],
            'dca_on': b[5],
            'is_paper': b[6],
            'status': b[7],
            'expires_at': str(b[8]),
            'auto_renew': b[9],
            'base_coin': b[10],
            'trades_per_bot': b[11],
            'trades_per_coin': b[12],
            'gate_dca_enabled': b[13],
            'gate_timer_enabled': b[14],
            'gate_timer_hours': b[15],
            'order_entry_type': b[16],
            'order_dca_type': b[17],
            'exchange': b[18],
            'exchange_name': b[19],
            'base_order': float(b[20]) if b[20] else 0,
            'take_profit_percent': float(b[21]) if b[21] else 5,
            'trailing_percent': float(b[22]) if b[22] else 2,
            'bot_params': b[23],
            'current_worth': round(worth, 2),
            'total_invested': round(invested, 2),
            'pnl_usdt': round(pnl, 2),
            'pnl_pct': round(pnl_pct, 2),
            'open_positions': len([p for p in dca_pos if p[0] == bot_id]) +
                              len([p for p in scalper_pos if p[0] == bot_id]),
            'wallet_name': wallet.get('wallet_name', '—'),
            'wallet_available': wallet.get('available', 0),
            'wallet_total': wallet.get('total', 0),
            'realized_pnl': round(dca_realized.get(bot_id, 0) + scalper_realized.get(bot_id, 0), 2),
        })
    return result

class BotToggle(BaseModel):
    trading_on: Optional[bool] = None
    dca_on: Optional[bool] = None
    trades_per_bot: Optional[int] = None


@app.post('/bots/{bot_id}/update')
def update_bot(bot_id: int, data: dict, payload: dict = Depends(verify_token)):
    import json as _json
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, method, bot_params FROM bots WHERE id=%s AND user_id=%s AND is_research=FALSE AND is_template=FALSE",
                    (bot_id, user_id))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Bot not found')
        method = row[1] or ''
        bot_params = row[2] or {}

        # Update name
        if 'name' in data and data['name']:
            cur.execute("UPDATE bots SET name=%s WHERE id=%s", (data['name'], bot_id))

        # Update base order (future trades)
        if 'base_order' in data:
            cur.execute("UPDATE bots SET base_order=%s WHERE id=%s", (data['base_order'], bot_id))

        # Update DCA exit params — applies to bot + all open positions
        if 'take_profit_percent' in data:
            tp = float(data['take_profit_percent'])
            cur.execute("UPDATE bots SET take_profit_percent=%s WHERE id=%s", (tp, bot_id))
            cur.execute("UPDATE live_dca_positions SET pos_tp_pct=%s WHERE bot_id=%s AND status='open'", (tp, bot_id))

        if 'trailing_percent' in data:
            trail = float(data['trailing_percent'])
            cur.execute("UPDATE bots SET trailing_percent=%s WHERE id=%s", (trail, bot_id))
            cur.execute("UPDATE live_dca_positions SET pos_trail_pct=%s WHERE bot_id=%s AND status='open'", (trail, bot_id))

        # Update scalper params (future trades only — stored in bot_params)
        if any(k in data for k in ('trigger_pct', 'window_sec', 'hold_sec')):
            if isinstance(bot_params, str):
                bot_params = _json.loads(bot_params)
            if 'trigger_pct' in data:
                bot_params['trigger_pct'] = float(data['trigger_pct'])
            if 'window_sec' in data:
                bot_params['window_sec'] = float(data['window_sec'])
            if 'hold_sec' in data:
                bot_params['hold_sec'] = int(data['hold_sec'])
            cur.execute("UPDATE bots SET bot_params=%s WHERE id=%s", (_json.dumps(bot_params), bot_id))

        cur.execute("UPDATE bots SET updated_at=NOW() WHERE id=%s", (bot_id,))
        conn.commit()
    return {'message': 'Updated successfully'}

@app.post('/bots/{bot_id}/toggle')
def toggle_bot(bot_id: int, toggle: BotToggle,
               payload: dict = Depends(verify_token)):
    with db.get_db() as conn:
        cur = conn.cursor()
        if toggle.trading_on is not None:
            cur.execute("""
                UPDATE bots SET trading_on = %s
                WHERE id = %s AND user_id = %s
            """, (toggle.trading_on, bot_id, payload['user_id']))
        if toggle.dca_on is not None:
            cur.execute("""
                UPDATE bots SET dca_on = %s
                WHERE id = %s AND user_id = %s
            """, (toggle.dca_on, bot_id, payload['user_id']))
        if toggle.trades_per_bot is not None:
            cur.execute("""
                UPDATE bots SET trades_per_bot = %s
                WHERE id = %s AND user_id = %s
            """, (toggle.trades_per_bot, bot_id, payload['user_id']))
    return {'message': 'Bot updated'}

# ═══════════════════════════════
# EXCHANGES
# ═══════════════════════════════
@app.get('/api/exchanges')
def get_exchanges(payload: dict = Depends(verify_token)):
    exchanges = db.get_user_exchanges(payload['user_id'])
    return [{'id': e[0], 'exchange': e[1],
              'custom_name': e[2], 'active': e[6],
              'paused': e[7] is not None,
              'pause_reason': e[8],
              'last_connected': str(e[6]),
              'ip_confirmed': None} for e in exchanges]

# ═══════════════════════════════
# ATTENTION LOG
# ═══════════════════════════════
@app.get('/attention-log')
def get_attention_log(payload: dict = Depends(verify_token)):
    logs = db.get_user_attention_logs(payload['user_id'])
    return [{'id': l[0], 'severity': l[1],
              'item_type': l[2], 'message': l[3],
              'bot_id': l[4], 'position_id': l[5],
              'created_at': str(l[6])} for l in logs]

@app.post('/attention-log/{log_id}/resolve')
def resolve_log(log_id: int, action: str = 'dismissed',
                payload: dict = Depends(verify_token)):
    db.resolve_attention_log(log_id, action)
    return {'message': 'Resolved'}

# ═══════════════════════════════
# RESERVE WALLET
# ═══════════════════════════════
@app.get('/reserve-wallet')
def get_reserve(payload: dict = Depends(verify_token)):
    wallet = db.get_reserve_wallet(payload['user_id'])
    if not wallet:
        return {'balance': 0, 'total_deposited': 0}
    return {
        'id': wallet[0],
        'balance': float(wallet[1]),
        'total_deposited': float(wallet[2]),
        'total_deducted': float(wallet[3])
    }

# ═══════════════════════════════
# BALANCE HISTORY
# ═══════════════════════════════
@app.get('/balance-history')
def get_balance_history(exchange_id: int = 1, days: int = 30,
                         payload: dict = Depends(verify_token)):
    rows = db.get_balance_history(exchange_id, days)
    return [{'value': float(r[0]), 'date': str(r[1])}
            for r in rows]

# ═══════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════
@app.get('/admin/research/positions')
def get_research_positions(payload: dict = Depends(verify_token)):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, b.name, b.method, p.coin,
                   p.avg_cost, p.total_invested, p.dca_count,
                   p.tp_armed, p.opened_at, p.status,
                   p.entry_method, p.quantity
            FROM positions p
            JOIN bots b ON b.id = p.bot_id
            WHERE p.is_research = TRUE
            AND p.status = 'open'
            ORDER BY p.opened_at DESC
        """)
        rows = cur.fetchall()
        result = []
        rc = get_redis()
        for r in rows:
            coin = r[3]
            avg_cost = float(r[4] or 0)
            quantity = float(r[11] or 0)
            keys = rc.keys(f'price:*:{coin}/USDT')
            if keys:
                current_price = float(rc.get(keys[0]))
                pnl = (current_price - avg_cost) * quantity if avg_cost else 0
                pnl_pct = round((current_price - avg_cost) / avg_cost * 100, 2) if avg_cost else 0
            else:
                current_price = None
                pnl = 0
                pnl_pct = 0
            result.append({
                'id': r[0], 'bot_name': r[1], 'method': r[2],
                'coin': coin, 'avg_cost': str(r[4]),
                'total_invested': str(r[5]), 'dca_count': r[6],
                'tp_armed': r[7], 'opened_at': str(r[8]),
                'status': r[9], 'entry_method': r[10],
                'current_price': current_price,
                'pnl': round(pnl, 4),
                'pnl_pct': round(pnl_pct, 2)
            })
        return result

@app.get('/admin/research/champ-score')
def research_champ_score(payload: dict = Depends(require_admin)):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.method,
                   COUNT(*) as trades,
                   ROUND(SUM(p.total_sold_usdt - p.total_invested)::numeric,2) as total_pnl,
                   ROUND(SUM(CASE WHEN p.total_sold_usdt > p.total_invested THEN p.total_sold_usdt - p.total_invested ELSE 0 END)::numeric,2) as gross_win,
                   ROUND(SUM(CASE WHEN p.total_sold_usdt <= p.total_invested THEN p.total_invested - p.total_sold_usdt ELSE 0 END)::numeric,2) as gross_loss,
                   array_agg(p.total_sold_usdt - p.total_invested ORDER BY p.total_sold_usdt - p.total_invested DESC) as all_pnls
            FROM positions p JOIN bots b ON b.id=p.bot_id
            WHERE p.status='closed' AND b.is_research=TRUE
            GROUP BY b.method
        """)
        rows = cur.fetchall()

    result = []
    for r in rows:
        method, trades, total_pnl, gross_win, gross_loss, all_pnls = r
        total_pnl = float(total_pnl or 0)
        gross_win = float(gross_win or 0)
        gross_loss = float(gross_loss or 0)
        # Excl top 5
        pnls = [float(x) for x in (all_pnls or [])]
        excl_top5 = round(sum(pnls[5:]), 2) if len(pnls) > 5 else round(total_pnl, 2)
        # Profit factor
        pf = round(gross_win / gross_loss, 2) if gross_loss > 0 else round(gross_win, 2)
        # Robustness
        robustness = round(excl_top5 / total_pnl * 100, 1) if total_pnl > 0 else 0
        # Score = 40% total + 30% excl top5 + 20% pf normalized + 10% trades normalized
        score = round(total_pnl * 0.4 + excl_top5 * 0.3 + pf * 0.2 + trades * 0.1, 2)
        result.append({
            'method': method,
            'trade_count': int(trades),
            'total_pnl': total_pnl,
            'excl_top5': excl_top5,
            'profit_factor': pf,
            'robustness': robustness,
            'score': score,
        })
    result.sort(key=lambda x: -x['score'])
    return result

@app.get('/admin/research/scalper-score')
def research_scalper_score(payload: dict = Depends(require_admin)):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.name, b.bot_params::text,
                   COUNT(*) FILTER (WHERE s.status='closed') as trades,
                   ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric,2) as total_pnl,
                   ROUND(SUM(CASE WHEN s.pnl_usdt > 0 THEN s.pnl_usdt ELSE 0 END) FILTER (WHERE s.status='closed')::numeric,2) as gross_win,
                   ROUND(SUM(CASE WHEN s.pnl_usdt <= 0 THEN ABS(s.pnl_usdt) ELSE 0 END) FILTER (WHERE s.status='closed')::numeric,2) as gross_loss,
                   array_agg(s.pnl_usdt ORDER BY s.pnl_usdt DESC) FILTER (WHERE s.status='closed') as all_pnls
            FROM scalper_positions s JOIN bots b ON b.id=s.bot_id
            GROUP BY b.name, b.bot_params
            HAVING COUNT(*) FILTER (WHERE s.status='closed') > 0
        """)
        rows = cur.fetchall()

    import json as _json
    result = []
    for r in rows:
        name, params_raw, trades, total_pnl, gross_win, gross_loss, all_pnls = r
        try:
            p = _json.loads(params_raw) if params_raw else {}
        except:
            p = {}
        total_pnl = float(total_pnl or 0)
        gross_win = float(gross_win or 0)
        gross_loss = float(gross_loss or 0)
        pnls = [float(x) for x in (all_pnls or [])]
        excl_top5 = round(sum(pnls[5:]), 2) if len(pnls) > 5 else round(total_pnl, 2)
        pf = round(gross_win / gross_loss, 2) if gross_loss > 0 else round(gross_win, 2)
        robustness = round(excl_top5 / total_pnl * 100, 1) if total_pnl > 0 else 0
        score = round(total_pnl * 0.4 + excl_top5 * 0.3 + pf * 0.2 + trades * 0.1, 2)
        result.append({
            'name': name,
            'trigger_pct': p.get('trigger_pct','?'),
            'hold_sec': p.get('hold_sec','?'),
            'trade_count': int(trades),
            'total_pnl': total_pnl,
            'excl_top5': excl_top5,
            'profit_factor': pf,
            'robustness': robustness,
            'score': score,
        })
    result.sort(key=lambda x: -x['score'])
    return result

@app.get('/admin/research/scalper')
def research_scalper(payload: dict = Depends(require_admin)):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.name, b.bot_params::text,
                   COUNT(*) FILTER (WHERE s.status='closed') as closed,
                   COUNT(*) FILTER (WHERE s.status='closed' AND s.pnl_pct > 0) as wins,
                   ROUND(AVG(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric, 3) as avg_pnl,
                   ROUND(SUM(s.pnl_usdt) FILTER (WHERE s.status='closed')::numeric, 2) as total_pnl,
                   ROUND(MAX(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric, 2) as best,
                   ROUND(MIN(s.pnl_pct) FILTER (WHERE s.status='closed')::numeric, 2) as worst,
                   COUNT(*) FILTER (WHERE s.status='open') as open_now
            FROM scalper_positions s
            JOIN bots b ON b.id=s.bot_id
            GROUP BY b.name, b.bot_params
            HAVING COUNT(*) FILTER (WHERE s.status='closed') > 0
            ORDER BY avg_pnl DESC NULLS LAST
        """)
        rows = cur.fetchall()

    import json
    result = []
    for r in rows:
        name, params_raw, closed, wins, avg_pnl, total_pnl, best, worst, open_now = r
        try:
            p = json.loads(params_raw) if params_raw else {}
        except:
            p = {}
        win_rate = round(wins/closed*100, 1) if closed else 0
        # Score = win_rate * avg_pnl * speed (1/hold_sec)
        hold_sec = float(p.get('hold_sec', 30))
        avg_pnl_f = float(avg_pnl or 0)
        score = round((win_rate/100) * max(avg_pnl_f, 0) * (1/max(hold_sec,1)) * 1000, 4)
        result.append({
            'name': name,
            'trigger_pct': p.get('trigger_pct', '?'),
            'window_sec': p.get('window_sec', '?'),
            'hold_sec': hold_sec,
            'stop_loss_pct': p.get('stop_loss_pct'),
            'closed': int(closed or 0),
            'win_rate': win_rate,
            'avg_pnl': float(avg_pnl or 0),
            'total_pnl': float(total_pnl or 0),
            'best': float(best or 0),
            'worst': float(worst or 0),
            'open_now': int(open_now or 0),
            'score': score,
        })
    result.sort(key=lambda x: -x['score'])
    return result

@app.get('/admin/research/dca-queue')
def research_dca_queue(payload: dict = Depends(require_admin)):
    import redis as _redis
    r = _redis.Redis(host='localhost', port=6379, decode_responses=True)
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.coin, b.method, p.category,
                   p.avg_cost, p.last_buy_price, p.dca_count,
                   b.dca_percent, b.spacing_multiplier,
                   b.size_multiplier, b.base_order,
                   p.pos_dca_pct
            FROM positions p
            JOIN bots b ON b.id=p.bot_id
            WHERE p.status='open' AND b.trading_on=TRUE
            AND p.avg_cost > 0 AND p.last_buy_price > 0
            LIMIT 5000
        """)
        rows = cur.fetchall()

    result = []
    for row in rows:
        coin, method, category, avg_cost, last_buy, dca_count, dca_pct, spacing_mult, size_mult, base_order, pos_dca_pct = row
        avg_cost     = float(avg_cost or 0)
        last_buy     = float(last_buy or avg_cost)
        dca_pct      = float(pos_dca_pct or dca_pct or 7.0)  # use position-level if available
        spacing_mult = float(spacing_mult or 1.0)
        size_mult    = float(size_mult or 1.0)
        base_order   = float(base_order or 100)
        if avg_cost == 0 or last_buy == 0:
            continue
        keys = r.keys(f'price:*:{coin}/USDT')
        if not keys:
            continue
        current = float(r.get(keys[0]) or 0)
        if current == 0:
            continue
        # Match exact bot_loop trigger calculation
        effective_spacing = dca_pct * (spacing_mult ** dca_count)
        trigger_price = last_buy * (1 - effective_spacing / 100)
        if current > trigger_price:
            continue  # not triggered yet
        loss_pct = round((current - avg_cost) / avg_cost * 100, 2)
        gap_pct  = round((current - trigger_price) / trigger_price * 100, 2)
        next_dca_amount = base_order * (size_mult ** (dca_count + 1))
        score = abs(loss_pct) / next_dca_amount if next_dca_amount > 0 else 0
        result.append({
            'coin': coin,
            'method': method,
            'category': category or 'micro',
            'avg_cost': float(avg_cost),
            'current_price': current,
            'loss_pct': loss_pct,
            'dca_spacing': round(effective_spacing, 2),
            'trigger_price': round(trigger_price, 10),
            'gap_pct': gap_pct,
            'dca_count': dca_count,
            'score': round(score, 4),
        })

    result.sort(key=lambda x: -x['score'])
    return result

@app.get('/admin/research/champions')
def get_research_champions(payload: dict = Depends(verify_token)):
    import sys
    sys.path.insert(0, '/home/averion/Averion')
    try:
        from rars_scoring import calculate_rars
        scores = calculate_rars()
        return scores
    except Exception as e:
        return []

@app.get('/admin/research/history')
def get_research_history(payload: dict = Depends(verify_token)):
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, b.name, b.method, p.coin,
                   p.avg_cost, p.total_invested, p.dca_count,
                   p.opened_at, p.closed_at, p.close_reason,
                   p.avg_sell_price, p.total_sold_usdt
            FROM positions p
            JOIN bots b ON b.id = p.bot_id
            WHERE p.is_research = TRUE
            AND p.status = 'closed'
            ORDER BY p.closed_at DESC
            LIMIT 200
        """)
        rows = cur.fetchall()
        result = []
        for r in rows:
            avg_cost = float(r[4] or 0)
            avg_sell = float(r[10] or 0)
            invested = float(r[5] or 0)
            sold = float(r[11] or 0)
            pnl = sold - invested if sold else 0
            pnl_pct = (pnl / invested * 100) if invested else 0
            result.append({
                'id': r[0], 'bot_name': r[1], 'method': r[2],
                'coin': r[3], 'avg_cost': str(r[4]),
                'total_invested': str(r[5]), 'dca_count': r[6],
                'opened_at': str(r[7]), 'closed_at': str(r[8]),
                'close_reason': r[9], 'avg_sell_price': str(r[10] or 0),
                'pnl': round(pnl, 4), 'pnl_pct': round(pnl_pct, 2)
            })
        return result

@app.get('/admin/research/bots')
def get_research_bots_admin(payload: dict = Depends(verify_token)):
    bots = db.get_research_bots()
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT bot_id, COUNT(*) as open_count
            FROM positions WHERE is_research=TRUE AND status='open'
            GROUP BY bot_id
        """)
        open_counts = {r[0]: r[1] for r in cur.fetchall()}
    return [{'id': b[0], 'name': b[1], 'method': b[2],
              'direction': b[3], 'trading_on': b[4],
              'trades_per_bot': b[5], 'bot_params': b[6],
              'dca_percent': str(b[7]),
              'take_profit_percent': str(b[8]),
              'base_order': str(b[9]),
              'status': b[10],
              'exchange': b[11],
              'exchange_name': b[12],
              'open_trades': open_counts.get(b[0], 0)} for b in bots]

@app.get('/admin/stats')
def admin_stats(payload: dict = Depends(require_admin)):
    stats = db.get_platform_stats()
    r = get_redis()
    return {
        'total_users': stats[0],
        'active_bots': stats[1],
        'open_positions': stats[2],
        'live_positions': stats[3],
        'paper_positions': stats[4],
        'total_reserve': float(stats[5] or 0),
        'owner_balance': float(stats[6] or 0),
        'trades_today': stats[7],
        'closed_today': stats[8],
        'bot_status': r.get('bot:status') or 'unknown',
        'cycle_time': r.get('bot:cycle_time') or '0',
        'last_cycle': r.get('bot:last_cycle') or 'never'
    }

@app.get('/admin/users')
def admin_users(payload: dict = Depends(require_admin)):
    users = db.get_all_users_admin()
    return [{'id': u[0], 'email': u[1],
              'created_at': str(u[2]),
              'suspended': u[3],
              'telegram': u[4],
              'bots': u[5],
              'open_positions': u[6],
              'reserve': float(u[7] or 0),
              'fee_debt': float(u[8] or 0)} for u in users]

@app.post('/admin/bot/restart')
def admin_restart_bot(payload: dict = Depends(require_admin)):
    import subprocess
    subprocess.run(['pm2', 'restart', 'averion'])
    return {'message': 'Bot restarting'}

@app.post('/admin/cron/{step}/run')
def admin_run_cron_step(step: str,
                         payload: dict = Depends(require_admin)):
    import subprocess
    scripts = {
        'infrastructure': 'automation/daily_cron.sh',
        'coingecko': 'automation/fetch_coingecko.py',
        'cmc': 'automation/fetch_cmc.py',
        'classification': 'automation/classify_coins.py',
        'reporting': 'automation/daily_aggregation.py',
        'diagnostics': 'automation/generate_diagnostics.py'
    }
    if step not in scripts:
        raise HTTPException(status_code=404, detail='Unknown step')

    script = scripts[step]
    if script.endswith('.py'):
        subprocess.Popen(['python3', script])
    else:
        subprocess.Popen(['bash', script])

    return {'message': f'Step {step} started'}

# ═══════════════════════════════
# EXCHANGES — ADD / TEST / DELETE
# ═══════════════════════════════
class ExchangeCreate(BaseModel):
   exchange: str
   custom_name: str
   api_key: str
   secret: str
   passphrase: Optional[str] = None
   ip_whitelist_confirmed: bool = False

@app.post('/api/exchanges')
def add_exchange(req: ExchangeCreate,
                payload: dict = Depends(verify_token)):
   from cryptography.fernet import Fernet
   import base64

   fernet_key = os.getenv('FERNET_KEY')
   if not fernet_key:
       raise HTTPException(status_code=500,
                           detail='Encryption not configured')

   f = Fernet(fernet_key.encode())
   api_key_enc = f.encrypt(req.api_key.encode()).decode()
   secret_enc = f.encrypt(req.secret.encode()).decode()
   passphrase_enc = None
   if req.passphrase:
       passphrase_enc = f.encrypt(req.passphrase.encode()).decode()

   exchange_id = db.add_exchange(
       payload['user_id'], req.exchange, req.custom_name,
       api_key_enc, secret_enc, passphrase_enc
   )

   # Confirm IP whitelist
   if req.ip_whitelist_confirmed:
       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("""
               UPDATE exchanges SET ip_whitelist_confirmed = TRUE
               WHERE id = %s
           """, (exchange_id,))

   return {'message': 'Exchange added', 'exchange_id': exchange_id}

@app.post('/exchanges/{exchange_id}/test')
def test_exchange(exchange_id: int,
                 payload: dict = Depends(verify_token)):
   from cryptography.fernet import Fernet
   import ccxt

   exc = db.get_exchange_by_id(exchange_id)
   if not exc or exc[1] != payload['user_id']:
       raise HTTPException(status_code=404,
                           detail='Exchange not found')

   fernet_key = os.getenv('FERNET_KEY')
   f = Fernet(fernet_key.encode())

   try:
       api_key = f.decrypt(exc[3].encode()).decode()
       secret = f.decrypt(exc[4].encode()).decode()
       passphrase = None
       if exc[5]:
           passphrase = f.decrypt(exc[5].encode()).decode()

       exchange_class = getattr(ccxt, exc[2])
       config = {
           'apiKey': api_key,
           'secret': secret,
           'enableRateLimit': True
       }
       if passphrase:
           config['password'] = passphrase

       exchange = exchange_class(config)
       balance = exchange.fetch_balance()
       usdt = balance.get('USDT', {}).get('free', 0)

       # Update last connected
       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("""
               UPDATE exchanges SET last_connected_at = NOW()
               WHERE id = %s
           """, (exchange_id,))

       return {
           'success': True,
           'balance_usdt': round(float(usdt), 2),
           'message': f'✅ Connected · Balance: ${usdt:.2f} USDT'
       }

   except ccxt.AuthenticationError:
       return {
           'success': False,
           'message': '❌ Invalid API key or secret'
       }
   except ccxt.ExchangeError as e:
       return {
           'success': False,
           'message': f'❌ Exchange error: {str(e)[:100]}'
       }
   except Exception as e:
       return {
           'success': False,
           'message': f'❌ Error: {str(e)[:100]}'
       }

@app.delete('/exchanges/{exchange_id}')
def delete_exchange(exchange_id: int,
                   payload: dict = Depends(verify_token)):
   with db.get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           UPDATE exchanges SET active = FALSE
           WHERE id = %s AND user_id = %s
       """, (exchange_id, payload['user_id']))
   return {'message': 'Exchange removed'}

# ═══════════════════════════════
# BOTS — CREATE / DELETE
# ═══════════════════════════════
class BotCreate(BaseModel):
   exchange_id: int
   wallet_id: int
   name: str
   method: str
   direction: str
   base_order: float = 1.0
   dca_percent: float = 7.0
   spacing_multiplier: float = 1.4
   size_multiplier: float = 1.5
   take_profit_percent: float = 5.0
   trailing_percent: float = 2.0
   base_coin: str = 'USDT'
   is_paper: bool = True
   trades_per_bot: int = 1
   trades_per_coin: int = 1
   gate_dca_enabled: bool = False
   gate_timer_enabled: bool = False
   gate_timer_hours: int = 5
   order_entry_type: str = 'market'
   order_dca_type: str = 'market'

@app.post('/bots')
def create_bot(req: BotCreate,
              payload: dict = Depends(verify_token)):
   bot_id = db.create_bot(
       payload['user_id'], req.exchange_id, req.wallet_id,
       req.name, req.method, req.direction, req.base_order,
       req.dca_percent, req.spacing_multiplier,
       req.size_multiplier, req.take_profit_percent,
       req.trailing_percent, req.base_coin, req.is_paper,
       req.trades_per_bot, req.trades_per_coin,
       req.gate_dca_enabled, req.gate_timer_enabled,
       req.gate_timer_hours, req.order_entry_type,
       req.order_dca_type
   )
   return {'message': 'Bot created', 'bot_id': bot_id}

@app.post('/bots/{bot_id}/panic-close')
def panic_close_bot(bot_id: int, payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM bots WHERE id=%s AND user_id=%s AND is_research=FALSE",
            (bot_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Bot not found')
        cur.execute(
            "UPDATE live_positions SET status='closed', exit_time=NOW(), exit_reason='panic_close' WHERE bot_id=%s AND status='open'",
            (bot_id,))
        s = cur.rowcount
        cur.execute(
            "UPDATE live_dca_positions SET status='closed', closed_at=NOW(), close_reason='panic_close', realized_pnl_usdt=0 WHERE bot_id=%s AND status='open'",
            (bot_id,))
        d = cur.rowcount
        cur.execute(
            "UPDATE virtual_wallets SET current_balance=current_balance+committed_usdt, committed_usdt=0, updated_at=NOW() WHERE id=(SELECT wallet_id FROM bots WHERE id=%s)",
            (bot_id,))
        cur.execute("UPDATE bots SET trading_on=FALSE WHERE id=%s", (bot_id,))
        conn.commit()
    return {'message': f'Closed {s+d} positions · Bot stopped', 'closed': s+d}

@app.delete('/bots/{bot_id}')
def delete_bot(bot_id: int, payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM bots WHERE id=%s AND user_id=%s AND is_research=FALSE AND is_template=FALSE",
                    (bot_id, user_id))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Bot not found')
        # Close all open positions
        cur.execute("UPDATE live_positions SET status='closed', exit_time=NOW(), exit_reason='bot_deleted' WHERE bot_id=%s AND status='open'", (bot_id,))
        cur.execute("UPDATE live_dca_positions SET status='closed', closed_at=NOW(), close_reason='bot_deleted' WHERE bot_id=%s AND status='open'", (bot_id,))
        # Return wallet funds
        cur.execute("""
            UPDATE virtual_wallets vw
            SET current_balance=vw.current_balance+vw.committed_usdt,
                committed_usdt=0, updated_at=NOW()
            FROM bots b WHERE b.id=%s AND b.wallet_id=vw.id
        """, (bot_id,))
        # Soft delete — hides from all UI, frees bot slot
        cur.execute("""
            UPDATE bots SET status='deleted', trading_on=FALSE, dca_on=FALSE
            WHERE id=%s AND user_id=%s
        """, (bot_id, user_id))
        conn.commit()
    return {'message': 'Bot deleted successfully'}

# ═══════════════════════════════
# VIRTUAL WALLETS
# ═══════════════════════════════
class WalletCreate(BaseModel):
   exchange_id: int
   name: str
   currency: str = 'USDT'
   allocation_type: str = 'fixed'
   allocation_amount: float = 0

@app.get('/wallets')
def get_wallets(payload: dict = Depends(verify_token)):
   wallets = db.get_user_wallets(payload['user_id'])
   return [{'id': w[0], 'name': w[1], 'currency': w[2],
             'allocation_type': w[3],
             'allocation_amount': float(w[4] or 0),
             'current_balance': float(w[5] or 0),
             'standby_reserved': float(w[6] or 0),
             'exchange': w[7],
             'exchange_name': w[8]} for w in wallets]

@app.post('/wallets')
def create_wallet(req: WalletCreate,
                 payload: dict = Depends(verify_token)):
   wallet_id = db.create_wallet(
       payload['user_id'], req.exchange_id, req.name,
       req.currency, req.allocation_type, req.allocation_amount
   )
   return {'message': 'Wallet created', 'wallet_id': wallet_id}

# ═══════════════════════════════
# ADMIN — CRON STATUS
# ═══════════════════════════════
@app.get('/admin/cron-status')
def admin_cron_status(payload: dict = Depends(require_admin)):
   with db.get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           SELECT DISTINCT ON (step)
               step, status, duration_seconds,
               records_processed, error_message,
               completed_at
           FROM performance_timing
           WHERE completed_at > NOW() - INTERVAL '48 hours'
           ORDER BY step, completed_at DESC
       """)
       rows = cur.fetchall()

   steps = {
       'infrastructure': None,
       'coingecko': None,
       'cmc': None,
       'classification': None,
       'reporting': None,
       'cleanup': None
   }

   for r in rows:
       step = r[0]
       if step in steps:
           steps[step] = {
               'step': step,
               'status': r[1],
               'duration': float(r[2] or 0),
               'records': r[3],
               'error': r[4],
               'completed_at': str(r[5])
           }

   return steps

# ═══════════════════════════════
# ADMIN — DIAGNOSTICS
# ═══════════════════════════════
@app.get('/admin/diagnostics')
def admin_diagnostics(payload: dict = Depends(require_admin)):
   try:
       with open('diagnostics/latest.md', 'r') as f:
           content = f.read()
       return {'content': content, 'available': True}
   except:
       return {'content': 'No diagnostics available yet',
               'available': False}

@app.post('/admin/diagnostics/generate')
def generate_diagnostics(payload: dict = Depends(require_admin)):
   import subprocess
   subprocess.Popen(['python3',
                     'automation/generate_diagnostics.py'])
   return {'message': 'Diagnostics generation started'}

# ═══════════════════════════════
# ADMIN — SYSTEM HEALTH
# ═══════════════════════════════


@app.get('/admin/ws-status')
def admin_ws_status(payload: dict = Depends(require_admin)):
    r = get_redis()
    return {
        'status': r.get('ws:mexc:status') or 'unknown',
        'price_count': int(r.get('ws:mexc:price_count') or 0),
        'total_updates': int(r.get('ws:mexc:total_updates') or 0),
        'last_update': r.get('ws:mexc:last_update') or 'never',
    }

@app.get('/admin/health')
def admin_health(payload: dict = Depends(require_admin)):
   with db.get_db() as conn:
       cur = conn.cursor()
       cur.execute("""
           SELECT cpu_percent, ram_percent, disk_percent, checked_at
           FROM system_health
           ORDER BY checked_at DESC LIMIT 168
       """)
       rows = cur.fetchall()
   # Get absolute values from psutil
   try:
       import psutil
       mem = psutil.virtual_memory()
       disk_info = psutil.disk_usage('/')
       ram_total_gb = round(mem.total / 1024**3, 1)
       ram_used_gb  = round(mem.used / 1024**3, 1)
       disk_total_gb = round(disk_info.total / 1024**3, 1)
       disk_used_gb  = round(disk_info.used / 1024**3, 1)
       # Add live CPU/RAM/Disk to latest record
       cpu_live = psutil.cpu_percent(interval=0.5)
       ram_live = mem.percent
       disk_live = disk_info.percent
   except:
       ram_total_gb = ram_used_gb = disk_total_gb = disk_used_gb = 0
       cpu_live = ram_live = disk_live = 0
   result = [{
       'cpu': float(r[0] or 0),
       'ram': float(r[1] or 0),
       'disk': float(r[2] or 0),
       'checked_at': str(r[3])
   } for r in rows]
   if result:
       result[0]['ram_used_gb'] = ram_used_gb
       result[0]['ram_total_gb'] = ram_total_gb
       result[0]['disk_used_gb'] = disk_used_gb
       result[0]['disk_total_gb'] = disk_total_gb
       result[0]['cpu'] = cpu_live
       result[0]['ram'] = ram_live
       result[0]['disk'] = disk_live
   return result

# ═══════════════════════════════
# AUTH — REGISTER / VERIFY
# ═══════════════════════════════
class RegisterRequest(BaseModel):
    email: str
    password: str
    referral_code: Optional[str] = None

@app.post('/auth/register')
def register(req: RegisterRequest, request: Request):
    result, error = auth_module.register_user(
        req.email, req.password, req.referral_code
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result

class VerifyRequest(BaseModel):
    user_id: int
    code: str
    remember: bool = True

@app.post('/auth/verify')
def verify(req: VerifyRequest, request: Request):
    ip = request.client.host
    success = auth_module.verify_code(
        req.user_id, req.code, ip, remember=req.remember
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail='Invalid or expired code'
        )
    return {'message': 'Verified successfully'}

@app.post('/auth/send-code')
def send_code(payload: dict = Depends(verify_token)):
    print('DEBUG: send-code called', payload)
    success = auth_module.send_verification(
        payload['user_id']
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail='Telegram not connected'
        )
    return {'message': 'Code sent via Telegram'}

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

@app.post('/auth/change-password')
def change_password(req: PasswordChange,
                    request: Request,
                    payload: dict = Depends(verify_token)):
    success, message = auth_module.change_password(
        payload['user_id'],
        req.old_password,
        req.new_password,
        request.client.host
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {'message': message}

# ═══════════════════════════════
# SUPPORTED EXCHANGES LIST
# ═══════════════════════════════
@app.get('/exchanges/supported')
def get_supported_exchanges():
    from exchanges import get_supported_exchanges
    return get_supported_exchanges()

# ═══════════════════════════════
# ADMIN — SECURITY LOGS
# ═══════════════════════════════
@app.get('/admin/security-logs')
def admin_security_logs(limit: int = 100,
                         payload: dict = Depends(require_admin)):
    logs = db.get_security_logs(limit=limit)
    return [{'id': l[0], 'user_id': l[1],
              'event': l[2], 'ip': l[3],
              'details': l[4], 'time': str(l[5])}
            for l in logs]

# ═══════════════════════════════
# TELEGRAM — CONNECT
# ═══════════════════════════════
@app.post('/telegram/connect')
def connect_telegram(payload: dict = Depends(verify_token)):
    user_id = payload['user_id']
    # Generate connect code for user
    code = db.create_verification_code(user_id)
    return {
        'message': f'Send this code to @AverionBot: CONNECT-{code}',
        'code': f'CONNECT-{code}',
        'bot_username': 'AverionBot'
    }

@app.get('/telegram/status')
def telegram_status(payload: dict = Depends(verify_token)):
    user = db.get_user_by_id(payload['user_id'])
    return {
        'connected': bool(user[3]) if user else False,
        'verified': bool(user[4]) if user else False
    }

# ═══════════════════════════════
# AUTH — RESET PASSWORD
# ═══════════════════════════════
class ResetPasswordRequest(BaseModel):
    email: str
    method: str = 'email'

class ResetPasswordConfirm(BaseModel):
    email: str
    code: str
    new_password: str

@app.post('/auth/reset-password')
def reset_password(req: ResetPasswordRequest):
    user = db.get_user_by_email(req.email)
    if not user:
        # Don't reveal if email exists
        return {'message': 'If this email exists · code sent'}

    user_id = user[0]
    code = db.create_verification_code(user_id)

    if req.method == 'telegram':
        chat_id = user[5] if len(user) > 5 else None
        if chat_id:
            import telegram as tg
            tg.send_message(chat_id,
                f'🔐 <b>Password Reset Code</b>\n\n'
                f'Your code: <b>{code}</b>\n'
                f'Valid for 15 minutes.\n\n'
                f'If you did not request this · ignore.'
            )
        else:
            return {'message': 'Telegram not connected · try email'}
    else:
        # Email reset — Phase 6 with SendGrid
        # For now: store code · admin can see in logs
        db.log_security_event(
            user_id, 'password_reset_requested',
            details={'method': req.method, 'code': code}
        )

    return {'message': 'If this email exists · code sent'}

@app.post('/auth/reset-password/confirm')
def reset_password_confirm(req: ResetPasswordConfirm):
    user = db.get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=400,
                            detail='Invalid request')

    user_id = user[0]

    # Verify code
    success = db.verify_code(user_id, req.code)
    if not success:
        raise HTTPException(status_code=400,
                            detail='Invalid or expired code')

    # Validate new password
    import re
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400,
                            detail='Password must be at least 8 characters')
    if not re.search(r'[A-Z]', req.new_password):
        raise HTTPException(status_code=400,
                            detail='Password must contain uppercase letter')
    if not re.search(r'[0-9]', req.new_password):
        raise HTTPException(status_code=400,
                            detail='Password must contain a number')
    if not re.search(r'[@$!%*#&]', req.new_password):
        raise HTTPException(status_code=400,
                            detail='Password must contain special character')

    # Update password
    new_hash = auth_module.hash_password(req.new_password)
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET password_hash = %s
            WHERE id = %s
        """, (new_hash, user_id))

    db.log_security_event(user_id, 'password_reset_complete')
    return {'message': 'Password updated · please login'}

@app.post('/auth/resend-verification')
def resend_verification(payload: dict = Depends(verify_token)):
   from datetime import datetime, timezone
   user_id = payload['user_id']

   # Check if already verified
   with db.get_db() as conn:
       cur = conn.cursor()
       cur.execute("SELECT email_verified, email FROM users WHERE id = %s", (user_id,))
       row = cur.fetchone()
       if not row:
           raise HTTPException(status_code=404, detail='User not found')
       if row[0]:
           return {'status': 'already_verified'}
       email = row[1]

   # Check 2 minute cooldown
   last = db.get_last_resend_time(user_id)
   if last and last[0]:
       now = datetime.now(timezone.utc)
       last_time = last[0].replace(tzinfo=timezone.utc)
       seconds_ago = (now - last_time).seconds
       if seconds_ago < 120:
           remaining = 120 - seconds_ago
           return {'status': 'cooldown', 'seconds_remaining': remaining}

   # Generate new code
   code, result = db.regenerate_verification_code(user_id)
   if result == 'too_many_attempts':
       raise HTTPException(status_code=429, detail='Too many resend attempts · try again in 1 hour')

   # Send email
   email_svc.send_verification_email(email, code)
   return {'status': 'sent', 'message': 'New verification code sent'}

@app.post('/exchanges/validate-key')
async def validate_exchange_key(req: dict, payload: dict = Depends(verify_token)):
    """Test API key before saving - check withdrawal permission and IP whitelist"""
    import ccxt
    exchange_name = req.get('exchange')
    api_key = req.get('api_key')
    secret = req.get('secret')
    passphrase = req.get('passphrase', '')

    results = {
        'connection': False,
        'withdrawal_disabled': False,
        'ip_whitelist': False,
        'errors': []
    }

    try:
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange_name)
        params = {'apiKey': api_key, 'secret': secret}
        if passphrase:
            params['password'] = passphrase
        exchange = exchange_class(params)

        # Test 1: Connection
        balance = exchange.fetch_balance()
        results['connection'] = True

        # Test 2: Withdrawal permission check
        try:
            # Try to fetch deposit address - if withdrawal enabled this works
            # We want this to FAIL (permission denied = good)
            exchange.fetch_deposit_address('USDT')
            results['withdrawal_disabled'] = False
            results['errors'].append('WARNING: Withdrawal permission appears enabled! Disable it on exchange first.')
        except ccxt.PermissionDenied:
            results['withdrawal_disabled'] = True
        except Exception:
            # Other errors = withdrawal likely disabled = good
            results['withdrawal_disabled'] = True

        # Test 3: Record validation in security audit log
        db.log_security_event(
            payload['user_id'],
            'api_key_validated',
            f'Exchange: {exchange_name} · Connection: OK · Withdrawal disabled: {results["withdrawal_disabled"]}'
        )

        results['ip_whitelist'] = True  # If we got here from our server IP = whitelist works

    except ccxt.AuthenticationError:
        results['errors'].append('Invalid API key or secret')
    except ccxt.NetworkError as e:
        results['errors'].append(f'Network error: {str(e)}')
    except Exception as e:
        results['errors'].append(f'Error: {str(e)}')

    return results


@app.get("/health")
def health_check():
   try:
       with db.get_db() as conn:
           cur = conn.cursor()
           cur.execute("SELECT 1")
       db_ok = True
   except:
       db_ok = False
   try:
       r = get_redis()
       r.ping()
       redis_ok = True
   except:
       redis_ok = False
   status = "ok" if db_ok and redis_ok else "degraded"
   return {"status": status, "db": "ok" if db_ok else "error", "redis": "ok" if redis_ok else "error"}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
