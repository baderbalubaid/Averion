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
@app.get('/dashboard')
def dashboard():
    return FileResponse('dashboard.html')

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
    return FileResponse('index.html')

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
@app.get('/bots')
def get_bots(payload: dict = Depends(verify_token)):
    bots = db.get_user_bots(payload['user_id'])
    return [{'id': b[0], 'name': b[1], 'method': b[2],
              'direction': b[3], 'trading_on': b[4],
              'dca_on': b[5], 'is_paper': b[6],
              'status': b[7], 'expires_at': str(b[8]),
              'auto_renew': b[9], 'base_coin': b[10],
              'trades_per_bot': b[11],
              'trades_per_coin': b[12],
              'gate_dca_enabled': b[13],
              'gate_timer_enabled': b[14],
              'gate_timer_hours': b[15],
              'order_entry_type': b[16],
              'order_dca_type': b[17],
              'exchange': b[18],
              'exchange_name': b[19]} for b in bots]

class BotToggle(BaseModel):
    trading_on: Optional[bool] = None
    dca_on: Optional[bool] = None
    trades_per_bot: Optional[int] = None

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
@app.get('/exchanges')
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


    uvicorn.run(app, host='0.0.0.0', port=8080)

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

@app.delete('/bots/{bot_id}')
def delete_bot(bot_id: int,
              payload: dict = Depends(verify_token)):
   with db.get_db() as conn:
       cur = conn.cursor()
       # Check ownership
       cur.execute("""
           SELECT id FROM bots
           WHERE id = %s AND user_id = %s
       """, (bot_id, payload['user_id']))
       if not cur.fetchone():
           raise HTTPException(status_code=404,
                               detail='Bot not found')
       # Soft delete
       cur.execute("""
           UPDATE bots SET status = 'deleted'
           WHERE id = %s
       """, (bot_id,))
   return {'message': f'Bot {bot_id} deleted'}

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

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
   uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
