from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time

from crypto_utils import (
    decrypt_seed,
    load_private_key,
    generate_totp_code,
    verify_totp_code
)

app = FastAPI()

PRIVATE_KEY_PATH = "/app/student_private.pem"
SEED_FILE_PATH = "/data/seed.txt"   # persistent volume


class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


def get_hex_seed():
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    try:
        with open(SEED_FILE_PATH, "r") as f:
            seed = f.read().strip()
            if not seed:
                raise HTTPException(status_code=500, detail="Seed file empty")
            return seed
    except:
        raise HTTPException(status_code=500, detail="Failed to read seed file")


@app.post("/decrypt-seed")
def api_decrypt_seed(req: DecryptRequest):
    try:
        private_key = load_private_key(PRIVATE_KEY_PATH)
        seed = decrypt_seed(req.encrypted_seed, private_key)

        with open(SEED_FILE_PATH, "w") as f:
            f.write(seed)

        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def api_generate_2fa():
    seed = get_hex_seed()

    code = generate_totp_code(seed)
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
def api_verify_2fa(req: VerifyRequest):
    if not (req.code and req.code.isdigit() and len(req.code) == 6):
        raise HTTPException(status_code=400, detail="Invalid code format")

    seed = get_hex_seed()
    is_valid = verify_totp_code(seed, req.code)

    return {"valid": is_valid}
