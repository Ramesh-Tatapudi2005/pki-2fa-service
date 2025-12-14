import base64
import time
import struct
import hmac
import hashlib
import re

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def load_private_key(path):
    try:
        with open(path, "rb") as key_file:
            return serialization.load_pem_private_key(key_file.read(), password=None)
    except Exception as e:
        print("Private key load error:", e)
        return None


def decrypt_seed(encrypted_b64, private_key):
    encrypted_bytes = base64.b64decode(encrypted_b64)

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted.decode()


def generate_totp_code(secret_hex, step=30):
    key = bytes.fromhex(secret_hex)
    counter = int(time.time() // step)

    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7fffffff
    code = binary % 1000000

    return f"{code:06d}"


def verify_totp_code(secret_hex, code, window=1):
    current_time = int(time.time() // 30)

    key = bytes.fromhex(secret_hex)

    for offset in range(-window, window + 1):
        counter = current_time + offset
        msg = struct.pack(">Q", counter)

        digest = hmac.new(key, msg, hashlib.sha1).digest()
        off = digest[-1] & 0x0F
        binary = struct.unpack(">I", digest[off:off + 4])[0] & 0x7fffffff
        generated = f"{binary % 1000000:06d}"

        if hmac.compare_digest(generated, code):
            return True

    return False
