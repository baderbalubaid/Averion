#!/usr/bin/env python3
"""
Split Fernet Key - run once on Day 2
Part A goes to .env · Part B goes to Hetzner Secrets
"""
import os, sys, requests
from dotenv import load_dotenv, set_key
load_dotenv()

def split_fernet_key():
    full_key = os.getenv('FERNET_KEY')
    if not full_key:
        print('❌ FERNET_KEY not found in .env')
        sys.exit(1)

    hetzner_token = os.getenv('HETZNER_API_TOKEN')
    secret_id = os.getenv('HETZNER_SECRET_ID')
    if not hetzner_token or not secret_id:
        print('❌ HETZNER_API_TOKEN or HETZNER_SECRET_ID missing from .env')
        sys.exit(1)

    mid = len(full_key) // 2
    part_a = full_key[:mid]
    part_b = full_key[mid:]

    env_path = '/home/averion/Averion/.env'
    set_key(env_path, 'FERNET_KEY_PART_A', part_a)
    print('✅ Part A saved to .env')

    res = requests.put(
        f'https://api.hetzner.cloud/v1/secrets/{secret_id}',
        headers={'Authorization': f'Bearer {hetzner_token}', 'Content-Type': 'application/json'},
        json={'value': part_b}
    )
    if res.status_code in [200, 201]:
        print('✅ Part B saved to Hetzner Secrets')
    else:
        print(f'❌ Hetzner error: {res.status_code} · {res.text}')
        sys.exit(1)

    set_key(env_path, 'FERNET_KEY', '')
    print('✅ FERNET_KEY cleared from .env')
    print('🔐 Split key complete · both parts needed to decrypt')

if __name__ == '__main__':
    split_fernet_key()
