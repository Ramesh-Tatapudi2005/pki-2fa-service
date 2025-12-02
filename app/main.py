import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.crypto_utils import (
    load_private_key,
    decrypt_seed,
    generate_totp_code,
    verify_totp_code,
)
from app.config import SEED_PATH, PRIVATE_KEY_PATH

app = FastAPI()


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str | None = None


@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    try:
        private_key = load_private_key(str(PRIVATE_KEY_PATH))
        hex_seed = decrypt_seed(body.encrypted_seed, private_key)

        SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
        SEED_PATH.write_text(hex_seed)

        return {"status": "ok"}
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Decryption failed"},
        )


@app.get("/generate-2fa")
def generate_2fa():
    if not SEED_PATH.exists():
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = SEED_PATH.read_text().strip()
        code = generate_totp_code(hex_seed)

        now = int(time.time())
        valid_for = 30 - (now % 30)

        if valid_for == 0:
            valid_for = 30

        return {"code": code, "valid_for": valid_for}
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Generation failed"},
        )


@app.post("/verify-2fa")
def verify_2fa(body: VerifyRequest):
    if body.code is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing code"},
        )

    if not SEED_PATH.exists():
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        hex_seed = SEED_PATH.read_text().strip()
        is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)
        return {"valid": bool(is_valid)}
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Verification failed"},
        )


@app.get("/health")
def health():
    return {"status": "ok"}
