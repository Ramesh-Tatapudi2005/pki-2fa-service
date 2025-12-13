# src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys

# Add the source directory to the path for correct import inside the container
sys.path.append(os.path.dirname(__file__)) 
# Import the functions created in Phase 2
from crypto_utils import decrypt_seed, load_private_key, generate_totp_code, verify_totp_code

app = FastAPI()

# --- Constants ---
PRIVATE_KEY_PATH = "student_private.pem" # Loaded from the /app directory in the container
SEED_FILE_PATH = "/data/seed.txt"        # Path to the persistent Docker volume

# --- Request Models (Pydantic) ---

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# --- Helper Function for Persistence ---

def get_hex_seed():
    """Reads the hex seed from persistent storage (/data/seed.txt) or raises HTTP 500."""
    # Check if the seed has been decrypted yet
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    try:
        with open(SEED_FILE_PATH, "r") as f:
            seed = f.read().strip()
            if not seed:
                 raise HTTPException(status_code=500, detail={"error": "Seed file is empty"})
            return seed
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Failed to read seed file"})


# --- API Endpoints ---

@app.post("/decrypt-seed")
def api_decrypt_seed(item: DecryptRequest):
    """Endpoint 1: Decrypts seed and saves it to persistent storage."""
    try:
        # 1. Load the private key
        private_key = load_private_key(PRIVATE_KEY_PATH)

        # 2. Decrypt the seed using the utility function
        hex_seed = decrypt_seed(item.encrypted_seed, private_key)

        # 3. Store persistently in the Docker volume
        with open(SEED_FILE_PATH, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}
    except Exception as e:
        print(f"Decryption/Storage Error: {e}", file=sys.stderr)
        # 500 Internal Server Error for cryptography or I/O failure
        raise HTTPException(status_code=500, detail={"error": "Decryption failed"})

@app.get("/generate-2fa")
def api_generate_2fa():
    """Endpoint 2: Generates the current TOTP code and validity time."""
    try:
        # 1. Retrieve the decrypted seed
        hex_seed = get_hex_seed()
        # 2. Generate the code using the utility function
        code, valid_for = generate_totp_code(hex_seed)

        return {"code": code, "valid_for": valid_for}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "TOTP generation failed"})

@app.post("/verify-2fa")
def api_verify_2fa(item: VerifyRequest):
    """Endpoint 3: Verifies a 6-digit TOTP code with time window tolerance."""
    # Basic validation
    if not item.code or len(item.code) != 6 or not item.code.isdigit():
        raise HTTPException(status_code=400, detail={"error": "Invalid code format"})

    try:
        # 1. Retrieve the decrypted seed
        hex_seed = get_hex_seed()

        # 2. Verify the code (uses +/- 1 period tolerance built into verify_totp_code)
        is_valid = verify_totp_code(hex_seed, item.code)

        return {"valid": is_valid}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "TOTP verification failed due to internal error"})