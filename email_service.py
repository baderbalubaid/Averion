import os
import requests
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv('RESEND_API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'noreply@averionbot.com')
SENDER_NAME = 'Averion'

# ═══════════════════════════════
# CORE SEND FUNCTION
# ═══════════════════════════════
def send_email(to: str, subject: str, html: str) -> bool:
    if not RESEND_API_KEY:
        print(f'Email not configured · subject: {subject}')
        return False
    try:
        res = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'from': f'{SENDER_NAME} <{SENDER_EMAIL}>',
                'to': [to],
                'subject': subject,
                'html': html
            },
            timeout=10
        )
        if res.status_code == 200:
            print(f'✅ Email sent to {to}: {subject}')
            return True
        else:
            print(f'❌ Email failed: {res.status_code} {res.text}')
            return False
    except Exception as e:
        print(f'❌ Email error: {e}')
        return False

# ═══════════════════════════════
# EMAIL TEMPLATES
# ═══════════════════════════════
def _base_template(content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', sans-serif;
                   background: #0E0E1C; color: #F0F0FF;
                   margin: 0; padding: 0; }}
            .container {{ max-width: 560px; margin: 40px auto;
                         background: #16162A;
                         border: 1px solid #2A2A45;
                         border-radius: 16px;
                         padding: 40px; }}
            .logo {{ font-size: 24px; font-weight: 800;
                    color: #10D98A; letter-spacing: 2px;
                    margin-bottom: 32px; }}
            .content {{ color: #CCCCDD; line-height: 1.7; }}
            .code {{ background: #0E0E1C; border: 1px solid #2A2A45;
                    border-radius: 10px; padding: 20px;
                    text-align: center; font-size: 32px;
                    font-weight: 800; color: #10D98A;
                    letter-spacing: 8px; margin: 24px 0; }}
            .btn {{ display: inline-block; background: #10D98A;
                   color: #0E0E1C; padding: 14px 32px;
                   border-radius: 10px; text-decoration: none;
                   font-weight: 700; margin: 24px 0; }}
            .footer {{ margin-top: 32px; font-size: 12px;
                      color: #555566; text-align: center; }}
            .warning {{ background: rgba(244,100,95,0.1);
                       border: 1px solid rgba(244,100,95,0.3);
                       border-radius: 8px; padding: 12px;
                       color: #F4645F; font-size: 13px;
                       margin-top: 16px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">AVERION</div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                © 2026 Averion · averionbot.com<br>
                Intelligent DCA Trading Platform
            </div>
        </div>
    </body>
    </html>
    """

# ═══════════════════════════════
# VERIFICATION EMAIL
# ═══════════════════════════════
def send_verification_email(to: str, code: str) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">Verify your email</h2>
        <p>Enter this code in Averion to verify your account:</p>
        <div class="code">{code}</div>
        <p style="color:#888;font-size:13px">
            Valid for 15 minutes.<br>
            If you did not create an Averion account, ignore this email.
        </p>
    """)
    return send_email(to, 'Verify your Averion account', html)

# ═══════════════════════════════
# PASSWORD RESET EMAIL
# ═══════════════════════════════
def send_password_reset_email(to: str, code: str) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">Reset your password</h2>
        <p>Enter this code to reset your Averion password:</p>
        <div class="code">{code}</div>
        <p style="color:#888;font-size:13px">
            Valid for 15 minutes.
        </p>
        <div class="warning">
            ⚠️ If you did not request this, your account may be
            at risk. Change your password immediately.
        </div>
    """)
    return send_email(to, 'Reset your Averion password', html)

# ═══════════════════════════════
# WELCOME EMAIL
# ═══════════════════════════════
def send_welcome_email(to: str) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">Welcome to Averion! 🚀</h2>
        <p>Your account is ready. Here is how to get started:</p>
        <ol style="color:#CCCCDD;line-height:2">
            <li>Connect your exchange (MEXC or KuCoin)</li>
            <li>Create your first bot</li>
            <li>Start with paper trading</li>
            <li>Go live when ready</li>
        </ol>
        <p>We only charge <strong style="color:#10D98A">20%
        of your profits</strong>. Loss months cost you nothing.</p>
        <a href="https://averionbot.com/dashboard" class="btn">
            Open Dashboard →
        </a>
        <p style="color:#888;font-size:13px">
            Questions? Reply to this email or contact
            support@averionbot.com
        </p>
    """)
    return send_email(to, 'Welcome to Averion!', html)

# ═══════════════════════════════
# RESERVE WALLET LOW
# ═══════════════════════════════
def send_reserve_low_email(to: str, balance: float) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">⚠️ Reserve Wallet Low</h2>
        <p>Your reserve wallet balance is low:</p>
        <div class="code" style="color:#F59E0B;font-size:24px">
            ${balance:.2f} USDT
        </div>
        <p>Performance fees may not be collected.
           Please top up to keep your bots running.</p>
        <a href="https://averionbot.com/settings" class="btn">
            Top Up Now →
        </a>
    """)
    return send_email(to, '⚠️ Averion Reserve Wallet Low', html)

# ═══════════════════════════════
# API KEY EXPIRING
# ═══════════════════════════════
def send_api_key_expiring_email(to: str, exchange: str,
                                 days_left: int) -> bool:
    html = _base_template(f"""
        <h2 style="margin-bottom:8px">⚠️ API Key Expiring</h2>
        <p>Your <strong>{exchange}</strong> API key expires
           in <strong style="color:#F4645F">{days_left} days</strong>.
        </p>
        <p>Update your API key before it expires to avoid
           trading interruptions.</p>
        <a href="https://averionbot.com/settings" class="btn">
            Update API Key →
        </a>
    """)
    return send_email(
        to,
        f'⚠️ {exchange} API Key Expiring in {days_left} Days',
        html
    )

# ═══════════════════════════════
# UPDATE auth.py TO USE EMAIL SERVICE
# ═══════════════════════════════
# In auth.py register_user() → call:
#   email_service.send_verification_email(email, code)
# In auth.py reset password → call:
#   email_service.send_password_reset_email(email, code)
# In auth.py after registration → call:
#   email_service.send_welcome_email(email)

if __name__ == '__main__':
    print('✅ Email service ready')
    print(f'Provider: Resend')
    print(f'Sender: {SENDER_EMAIL}')
    if RESEND_API_KEY:
        print('✅ API key configured')
    else:
        print('⚠️ RESEND_API_KEY not set · emails will not send')
