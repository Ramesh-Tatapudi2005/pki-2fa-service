import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# 🔴 PASTE YOUR COMMIT HASH HERE
COMMIT_HASH = "PASTE_YOUR_COMMIT_HASH_HERE"

# Load student private key
with open("student_private.pem", "rb") as f:
    student_private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

# Step 1: Sign commit hash (ASCII, NOT hex bytes)
signature = student_private_key.sign(
    COMMIT_HASH.encode("utf-8"),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Load instructor public key
with open("instructor_public.pem", "rb") as f:
    instructor_public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

# Step 2: Encrypt signature using instructor public key
encrypted_signature = instructor_public_key.encrypt(
    signature,
    padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Step 3: Base64 encode (SINGLE LINE)
encoded_signature = base64.b64encode(encrypted_signature).decode("utf-8")

print("====================")
print(encoded_signature)
print("====================")