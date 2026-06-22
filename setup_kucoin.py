import sys
sys.path.insert(0, '/home/averion/Averion')
from dotenv import load_dotenv
load_dotenv()
import database as db
from exchanges import encrypt
import getpass

db.init_pool()

print("=== KuCoin Setup ===")
api_key = getpass.getpass("API Key: ")
secret = getpass.getpass("Secret: ")
passphrase = getpass.getpass("Passphrase (KuCoin requires this): ")
user_id = input("User ID (1 for admin): ") or "1"

with db.get_db() as conn:
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO exchanges (user_id, exchange, custom_name, api_key_enc, secret_enc, passphrase_enc, active)
        VALUES (%s, 'kucoin', 'KuCoin Live', %s, %s, %s, TRUE)
        RETURNING id
    """, (user_id, encrypt(api_key), encrypt(secret), encrypt(passphrase)))
    new_id = cur.fetchone()[0]
    conn.commit()

print(f"KuCoin added successfully, exchange id={new_id}")
