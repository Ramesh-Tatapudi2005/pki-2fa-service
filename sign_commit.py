import base64
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import serialization

from app.crypto_utils import sign_message, encrypt_with_public_key


def load_private_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_private_key(data, password=None)


def load_public_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_public_key(data)


def get_latest_commit_hash() -> str:
    # gets the latest commit hash from git
    out = subprocess.check_output(
        ["git", "log", "-1", "--format=%H"],
        text=True,
    )
    return out.strip()


def main():
    repo_root = Path(__file__).resolve().parent

    # 1. Get commit hash
    commit_hash = get_latest_commit_hash()
    print(f"Commit Hash: {commit_hash}")

    # 2. Load keys
    student_private_path = repo_root / "student_private.pem"
    instructor_public_path = repo_root / "instructor_public.pem"

    student_private_key = load_private_key(student_private_path)
    instructor_public_key = load_public_key(instructor_public_path)

    # 3. Sign commit hash (RSA-PSS-SHA256)
    signature = sign_message(commit_hash, student_private_key)

    # 4. Encrypt signature with instructor public key (RSA-OAEP-SHA256)
    encrypted_signature = encrypt_with_public_key(signature, instructor_public_key)

    # 5. Base64 encode for submission
    encrypted_b64 = base64.b64encode(encrypted_signature).decode("utf-8")

    print("\nEncrypted Commit Signature (Base64, single line):")
    print(encrypted_b64)


if __name__ == "__main__":
    main()
