import base64
import pyotp

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import padding as asy_padding


def load_private_key(path: str):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_private_key(data, password=None)


def load_public_key(path: str):
    with open(path, "rb") as f:
        data = f.read()
    return serialization.load_pem_public_key(data)


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    ciphertext = base64.b64decode(encrypted_seed_b64)

    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    hex_seed = plaintext.decode("utf-8").strip()

    allowed = set("0123456789abcdef")
    if len(hex_seed) != 64 or any(c not in allowed for c in hex_seed):
        raise ValueError("Invalid hex seed")

    return hex_seed


def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    b32 = base64.b32encode(seed_bytes).decode("utf-8")
    return b32


def generate_totp_code(hex_seed: str) -> str:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30)
    return totp.verify(code, valid_window=valid_window)
