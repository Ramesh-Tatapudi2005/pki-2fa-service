import base64
import time
import hmac
import hashlib
import struct
import binascii

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes


# -------------------------------
# Load RSA Private Key
# -------------------------------
def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


# -------------------------------
# RSA Decryption for Seed
# -------------------------------
def decrypt_seed(enc_b64, private_key):
    encrypted_bytes = base64.b64decode(enc_b64)

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted.decode()


# -------------------------------
# Generate TOTP Code (RFC 6238)
# -------------------------------
def _generate_totp_at(key: bytes, counter: int) -> str:
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()

    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF

    return str(binary % 1_000_000).zfill(6)


def generate_totp_code(hex_seed):
    key = binascii.unhexlify(hex_seed)
    counter = int(time.time() // 30)

    code = _generate_totp_at(key, counter)
    remaining = 30 - (int(time.time()) % 30)

    return code, remaining


# -------------------------------
# Verify TOTP with ±1 time window
# -------------------------------
def verify_totp_code(hex_seed, user_code):
    key = binascii.unhexlify(hex_seed)
    counter = int(time.time() // 30)

    valid_codes = {
        _generate_totp_at(key, counter - 1),
        _generate_totp_at(key, counter),
        _generate_totp_at(key, counter + 1),
    }

    return user_code in valid_codes
