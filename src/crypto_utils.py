import base64
import time
import hmac
import hashlib
import struct
import binascii

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes


def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def decrypt_seed(enc_b64, private_key):
    data = base64.b64decode(enc_b64)
    decrypted = private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()


def generate_totp_code(hex_seed):
    key = binascii.unhexlify(hex_seed)
    counter = int(time.time() // 30)

    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()

    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset:offset+4])[0] & 0x7FFFFFFF
    code = str(binary % 1000000).zfill(6)

    valid_for = 30 - (int(time.time()) % 30)

    return code, valid_for


def verify_totp_code(hex_seed, code):
    current, _, = generate_totp_code(hex_seed)
    prev, _, = generate_totp_code(hex_seed)
    next_c, _, = generate_totp_code(hex_seed)

    return code in {current, prev, next_c}
