#!/usr/bin/env python3
import sys
import datetime

from app.crypto_utils import generate_totp_code
from app.config import SEED_PATH


def main():
    try:
        # Seed must exist
        if not SEED_PATH.exists():
            print("Seed file not found", file=sys.stderr)
            return

        # Read seed
        hex_seed = SEED_PATH.read_text().strip()

        # Generate TOTP code
        code = generate_totp_code(hex_seed)

        # UTC timestamp
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Output format required by assignment
        print(f"{now} - 2FA Code: {code}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
