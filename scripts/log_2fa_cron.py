#!/usr/bin/env python3
import time
import os
from crypto_utils import generate_totp_code

SEED_FILE = "/data/seed.txt"

try:
    if not os.path.exists(SEED_FILE):
        print("Seed not ready")
        exit()

    with open(SEED_FILE, "r") as f:
        seed = f.read().strip()

    code = generate_totp_code(seed)
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    print(f"{ts} - 2FA Code: {code}")

except Exception as e:
    print(f"CRON ERROR: {e}")
