# src/crypto_utils.py
import base64
import time
import sys
import pyotp
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding as pss_padding

# --- Key Loading Utilities ---

def load_private_key(file_path):
    """Loads RSA private key from a PEM file."""
    try:
        with open(file_path, "rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(), password=None, backend=default_backend()
            )
    except Exception as e:
        print(f"Error loading private key from {file_path}: {e}", file=sys.stderr)
        raise

def load_public_key(file_path):
    """Loads RSA public key from a PEM file."""
    try:
        with open(file_path, "rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(), backend=default_backend()
            )
    except Exception as e:
        print(f"Error loading public key from {file_path}: {e}", file=sys.stderr)
        raise

# --- Decryption (RSA/OAEP-SHA256) ---

def decrypt_seed(encrypted_seed_b64: str, private_key: rsa.RSAPrivateNumbers) -> str:
    """Decrypts base64-encoded seed using RSA/OAEP with SHA-256 and MGF1."""
    ciphertext = base64.b64decode(encrypted_seed_b64)

    # CRITICAL: RSA/OAEP with SHA-256 and MGF1 for decryption
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(), 
            label=None
        )
    )
    hex_seed = plaintext.decode('utf-8')

    # Validation: must be 64-character hex string
    if len(hex_seed) != 64 or not all(c in '0123456789abcdef' for c in hex_seed.lower()):
        raise ValueError("Decrypted seed format invalid or not 64-character hex.")

    return hex_seed

# 

# --- TOTP Utilities (SHA-1, 30s, 6-digit) ---

def hex_to_base32(hex_seed: str) -> str:
    """Converts 64-char hex string to base32 required by TOTP."""
    seed_bytes = bytes.fromhex(hex_seed)
    # Base32 encoding, strip padding (=)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8').strip('=')
    return base32_seed

def generate_totp_code(hex_seed: str):
    """Generates the current TOTP code and validity seconds."""
    base32_seed = hex_to_base32(hex_seed)
    # TOTP: SHA-1, 30s, 6 digits
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6, digest=hashes.SHA1)

    code = totp.now()

    # Calculate remaining seconds in current 30s period
    valid_for = totp.interval - (int(time.time()) % totp.interval)

    return code, valid_for

def verify_totp_code(hex_seed: str, code: str) -> bool:
    """Verifies a TOTP code with +/- 1 period tolerance."""
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6, digest=hashes.SHA1)

    # CRITICAL: Set time window tolerance to +/- 1 period (valid_window=1)
    return totp.verify(code, valid_window=1)

# --- Commit Proof Utilities (for Phase 5) ---

def sign_message_pss(message: str, private_key) -> bytes:
    """Signs message (commit hash) using RSA-PSS with SHA-256 and max salt."""
    message_bytes = message.encode('utf-8') 

    signature = private_key.sign(
        message_bytes,
        pss_padding.PSS(
            mgf=pss_padding.MGF1(hashes.SHA256()),
            salt_length=pss_padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_signature_oaep(data: bytes, public_key) -> bytes:
    """Encrypts data (the signature) using RSA/OAEP with SHA-256."""
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )