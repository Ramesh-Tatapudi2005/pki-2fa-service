#!/usr/bin/env python3
# scripts/log_2fa_cron.py

import os
import datetime
import sys

# Adjust path to enable importing from the src directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from crypto_utils import generate_totp_code 

SEED_FILE_PATH = "/data/seed.txt"

def main():
    try:
        if not os.path.exists(SEED_FILE_PATH):
            # Fail silently if seed not ready (normal during startup)
            print("ERROR: Seed file not found.", file=sys.stderr)
            return

        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        if not hex_seed:
            return

        code, _ = generate_totp_code(hex_seed)

        # Get current UTC timestamp (CRITICAL!)
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Output to stdout (cron appends this to /cron/last_code.txt)
        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print(f"CRON FATAL ERROR: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()