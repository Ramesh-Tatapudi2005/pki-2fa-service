import requests
import json
import os

# ==========================================
# ⚠️ CONFIGURATION - EDITED FOR YOU ⚠️
# ==========================================

STUDENT_ID = "24A95A0508"

# MUST MATCH the GitHub repo you are submitting
GITHUB_REPO_URL = "https://github.com/Ramesh-Tatapudi2005/pki-2fa-service"

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"


def request_seed():
    print(f"Reading public key from: {os.path.abspath('student_public.pem')}")

    # 1. Read your student public key
    try:
        with open("student_public.pem", "r") as f:
            public_key_content = f.read()
    except FileNotFoundError:
        print("❌ ERROR: student_public.pem not found!")
        return

    # 2. Prepare Payload
    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": GITHUB_REPO_URL,
        "public_key": public_key_content
    }

    print("\nConnecting to Instructor API...")
    print(f"Student ID: {STUDENT_ID}")
    print(f"Repository: {GITHUB_REPO_URL}")

    try:
        # 3. Send API Request
        response = requests.post(API_URL, json=payload, timeout=15)

        if response.status_code != 200:
            print(f"\n❌ API Error {response.status_code}: {response.text}")
            return

        data = response.json()

        # 4. Save encrypted seed
        if "encrypted_seed" in data:
            with open("encrypted_seed.txt", "w") as f:
                f.write(data["encrypted_seed"])

            print("\n✅ SUCCESS! Encrypted seed saved to encrypted_seed.txt")
            print("⚠️ Do NOT commit encrypted_seed.txt to GitHub.")
        else:
            print("\n❌ 'encrypted_seed' missing in API response.")
            print(f"Response: {data}")

    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")


if __name__ == "__main__":
    request_seed()
