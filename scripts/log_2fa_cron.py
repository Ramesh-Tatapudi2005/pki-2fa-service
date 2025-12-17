#!/usr/bin/env python3

import sys
sys.path.append("/app")
import time
import os
from datetime import datetime
from src.crypto_utils import generate_totp_code


SEED_FILE = "/data/seed.txt"

def read_seed():
    if not os.path.exists(SEED_FILE):
        return None
    with open(SEED_FILE, "r") as f:
        return f.read().strip()

def main():
    seed = read_seed()
    if not seed:
        print("Seed not found")
        return

    code, _ = generate_totp_code(seed)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
