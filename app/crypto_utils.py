import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def sign_message(message: str, private_key) -> bytes:
    """
    Sign commit hash using RSA-PSS with SHA-256 and maximum salt length.
    Message must be signed as ASCII bytes (NOT hex-decoded).
    """
    message_bytes = message.encode("utf-8")

    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt signature bytes using RSA/OAEP with SHA-256.
    """
    encrypted = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted
