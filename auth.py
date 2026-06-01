import os
import hashlib
import secrets
import jwt
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import database as db
import telegram as tg

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
TOKEN_DAYS = 30

# ═══════════════════════════════
# PASSWORD HASHING
# ═══════════════════════════════
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(
        f'{salt}{password}'.encode()
    ).hexdigest()
    return f'{salt}:{hashed}'

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split(':')
        return hashlib.sha256(
            f'{salt}{password}'.encode()
        ).hexdigest() == hashed
    except:
        return False

# ═══════════════════════════════
# JWT TOKENS
# ═══════════════════════════════
def create_token(user_id: int, is_admin: bool) -> str:
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=TOKEN_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise Exception('Token expired · please login again')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def is_token_expiring_soon(token: str, days=7) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        exp = datetime.utcfromtimestamp(payload['exp'])
        remaining = (exp - datetime.utcnow()).days
        return remaining <= days
    except:
        return True

# ═══════════════════════════════
# LOGIN
# ═══════════════════════════════
def login(email: str, password: str,
          ip: str = None, user_agent: str = None):
    user = db.get_user_by_email(email)

    if not user:
        db.log_security_event(
            None, 'login_failed', ip, user_agent,
            {'email': email, 'reason': 'user_not_found'}
        )
        return None, 'Invalid email or password'

    user_id = user[0]
    password_hash = user[2]
    is_admin = user[3]
    is_suspended = user[6] if len(user) > 6 else False

    if is_suspended:
        db.log_security_event(
            user_id, 'login_blocked', ip, user_agent,
            {'reason': 'account_suspended'}
        )
        return None, 'Account suspended'

    if not verify_password(password, password_hash):
        db.log_security_event(
            user_id, 'login_failed', ip, user_agent,
            {'reason': 'wrong_password'}
        )
        return None, 'Invalid email or password'

    # Check if needs verification (new device or 30 days)
    needs_verification = check_needs_verification(user_id, ip)

    token = create_token(user_id, is_admin)

    db.log_security_event(
        user_id, 'login_success', ip, user_agent,
        {'needs_verification': needs_verification}
    )

    return {
        'token': token,
        'user_id': user_id,
        'email': email,
        'is_admin': is_admin,
        'needs_verification': needs_verification
    }, None

# ═══════════════════════════════
# DEVICE / SESSION VERIFICATION
# ═══════════════════════════════
def check_needs_verification(user_id: int, ip: str) -> bool:
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )

    # Check if this IP is trusted
    trusted_key = f'trusted_ip:{user_id}:{ip}'
    if r.get(trusted_key):
        return False  # Known device · no verification needed

    # New device · needs verification
    return True

def trust_device(user_id: int, ip: str, days=30):
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    trusted_key = f'trusted_ip:{user_id}:{ip}'
    r.setex(trusted_key, days * 86400, '1')

# ═══════════════════════════════
# VERIFICATION CODE
# ═══════════════════════════════
def send_verification(user_id: int) -> bool:
    user = db.get_user_by_id(user_id)
    if not user:
        return False

    telegram_chat_id = user[3]  # telegram_chat_id
    if not telegram_chat_id:
        return False

    return tg.send_verification_code(user_id, telegram_chat_id)

def verify_code(user_id: int, code: str,
                ip: str = None) -> bool:
    success = db.verify_code(user_id, code)

    if success:
        trust_device(user_id, ip, days=30)
        db.log_security_event(
            user_id, 'verification_success', ip,
            details={'code_verified': True}
        )

    else:
        db.log_security_event(
            user_id, 'verification_failed', ip,
            details={'reason': 'wrong_or_expired_code'}
        )

    return success

# ═══════════════════════════════
# BRUTE FORCE PROTECTION
# ═══════════════════════════════
def check_brute_force(ip: str) -> bool:
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    key = f'login_fails:{ip}'
    fails = r.get(key)
    return int(fails) >= 5 if fails else False

def record_login_fail(ip: str):
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    key = f'login_fails:{ip}'
    count = r.incr(key)
    r.expire(key, 1800)  # 30 minutes

    if count >= 5:
        tg.send_admin(
            f'🔴 <b>Brute Force Detected</b>\n'
            f'IP: {ip}\n'
            f'Failed attempts: {count}\n'
            f'Locked for 30 minutes'
        )

def clear_login_fails(ip: str):
    import redis as redis_lib
    r = redis_lib.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    r.delete(f'login_fails:{ip}')

# ═══════════════════════════════
# USER REGISTRATION
# ═══════════════════════════════
def register_user(email: str, password: str,
                   referral_code: str = None) -> tuple:
    # Check if email exists
    existing = db.get_user_by_email(email)
    if existing:
        return None, 'Email already registered'

    # Validate password strength
    if len(password) < 8:
        return None, 'Password must be at least 8 characters'

    # Hash password
    password_hash = hash_password(password)

    # Generate referral code
    user_referral = secrets.token_hex(4).upper()

    # Create user
    user_id = db.create_user(email, password_hash, user_referral)

    # Create reserve wallet
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO reserve_wallets (user_id)
            VALUES (%s)
        """, (user_id,))

    # Handle referral
    if referral_code:
        with db.get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id FROM users
                WHERE referral_code = %s
            """, (referral_code,))
            referrer = cur.fetchone()
            if referrer:
                cur.execute("""
                    INSERT INTO referrals
                    (referrer_user_id, referred_user_id)
                    VALUES (%s, %s)
                """, (referrer[0], user_id))

    db.log_security_event(
        user_id, 'registration',
        details={'email': email, 'referral': referral_code}
    )

    token = create_token(user_id, False)
    return {'token': token, 'user_id': user_id}, None

# ═══════════════════════════════
# PASSWORD CHANGE
# ═══════════════════════════════
def change_password(user_id: int, old_password: str,
                     new_password: str, ip: str = None) -> tuple:
    user = db.get_user_by_email_by_id(user_id)
    if not user:
        return False, 'User not found'

    if not verify_password(old_password, user[2]):
        db.log_security_event(
            user_id, 'password_change_failed', ip,
            details={'reason': 'wrong_old_password'}
        )
        return False, 'Current password incorrect'

    if len(new_password) < 8:
        return False, 'Password must be at least 8 characters'

    new_hash = hash_password(new_password)
    with db.get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users SET password_hash = %s
            WHERE id = %s
        """, (new_hash, user_id))

    db.log_security_event(
        user_id, 'password_changed', ip
    )
    tg.send_admin(f'🔐 Password changed · User #{user_id}')
    return True, 'Password changed successfully'

if __name__ == '__main__':
    print('✅ Auth module ready')
    test_hash = hash_password('testpassword123')
    print(f'✅ Password hashing works: {verify_password("testpassword123", test_hash)}')
