#!/usr/bin/env python3
"""
Fernet Key Rotation — runs 1st of every month
Generates new key · re-encrypts all API keys · deletes old key
"""
import os
import sys
sys.path.insert(0, '/home/averion/Averion')

from cryptography.fernet import Fernet
import database as db
import telegram as tg
from dotenv import load_dotenv, set_key

load_dotenv()

def rotate_fernet_key():
    print("🔐 Starting Fernet key rotation...")
    
    old_key = os.getenv('FERNET_KEY')
    if not old_key:
        print("❌ FERNET_KEY not found in .env")
        return False

    old_fernet = Fernet(old_key.encode())
    new_key = Fernet.generate_key().decode()
    new_fernet = Fernet(new_key.encode())

    try:
        with db.get_db() as conn:
            cur = conn.cursor()

            # Fetch all encrypted keys
            cur.execute("""
                SELECT id, api_key_enc, secret_enc, passphrase_enc
                FROM exchanges
                WHERE api_key_enc IS NOT NULL
            """)
            rows = cur.fetchall()
            print(f"Found {len(rows)} exchange keys to rotate")

            # Re-encrypt each key
            for row in rows:
                exc_id = row[0]
                try:
                    new_api = new_fernet.encrypt(
                        old_fernet.decrypt(row[1].encode())
                    ).decode()
                    new_secret = new_fernet.encrypt(
                        old_fernet.decrypt(row[2].encode())
                    ).decode()
                    new_pass = None
                    if row[3]:
                        new_pass = new_fernet.encrypt(
                            old_fernet.decrypt(row[3].encode())
                        ).decode()

                    cur.execute("""
                        UPDATE exchanges SET
                            api_key_enc = %s,
                            secret_enc = %s,
                            passphrase_enc = %s
                        WHERE id = %s
                    """, (new_api, new_secret, new_pass, exc_id))
                except Exception as e:
                    print(f"❌ Failed exchange {exc_id}: {e}")
                    return False

            conn.commit()

        # Update .env with new key
        env_path = '/home/averion/Averion/.env'
        set_key(env_path, 'FERNET_KEY', new_key)
        print(f"✅ FERNET_KEY rotated · {len(rows)} keys re-encrypted")

        # Alert admin
        tg.send_admin(
            f"🔐 Fernet key rotated successfully\n"
            f"Keys re-encrypted: {len(rows)}\n"
            f"Next rotation: 1st of next month"
        )
        return True

    except Exception as e:
        print(f"❌ Rotation failed: {e}")
        tg.send_admin(f"❌ CRITICAL: Fernet key rotation FAILED\n{e}")
        return False

if __name__ == '__main__':
    success = rotate_fernet_key()
    sys.exit(0 if success else 1)
