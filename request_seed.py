import requests

STUDENT_ID = "24A95A0508"  
REPO_URL = "https://github.com/Ramesh-Tatapudi2005/pki-2fa-service"  
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def main():
    # 1. Read your student public key (PEM)
    with open("student_public.pem", "r") as f:
        public_key_pem = f.read()

    # 2. Prepare the payload for the API
    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": REPO_URL,
        "public_key": public_key_pem,
    }

    # 3. Send POST request to the instructor API
    response = requests.post(API_URL, json=payload, timeout=30)
    response.raise_for_status()  # raise error if status != 200

    data = response.json()
    print("API Response:", data)

    # 4. Extract the encrypted seed
    encrypted_seed = data["encrypted_seed"]

    # 5. Save it to a file
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("Encrypted seed saved to encrypted_seed.txt")

if __name__ == "__main__":
    main()
