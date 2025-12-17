from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from src.crypto_utils import (
    decrypt_seed,
    load_private_key,
    generate_totp_code,
    verify_totp_code
)

app = FastAPI()   

PRIVATE_KEY_PATH = "/app/student_private.pem"
SEED_FILE_PATH = "/data/seed.txt"


class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


def get_hex_seed():
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_FILE_PATH, "r") as f:
        seed = f.read().strip()

    if not seed:
        raise HTTPException(status_code=500, detail="Seed file empty")

    return seed


@app.post("/decrypt-seed")
def api_decrypt_seed(body: DecryptRequest):
    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)

        with open(SEED_FILE_PATH, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception as e:
        print("Decryption error:", e)
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def api_generate_2fa():
    try:
        seed = get_hex_seed()
        code, valid_for = generate_totp_code(seed)
        return {"code": code, "valid_for": valid_for}
    except Exception as e:
        print("Generate-2FA error:", e)
        raise HTTPException(status_code=500, detail="TOTP generation failed")


@app.post("/verify-2fa")
def api_verify_2fa(body: VerifyRequest):
    if not (body.code.isdigit() and len(body.code) == 6):
        raise HTTPException(status_code=400, detail="Invalid code format")

    seed = get_hex_seed()
    is_valid = verify_totp_code(seed, body.code)

    return {"valid": is_valid}
