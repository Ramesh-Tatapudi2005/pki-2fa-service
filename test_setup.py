import requests
import json

# 1. Read the encrypted seed file
try:
    with open("encrypted_seed.txt", "r") as f:
        encrypted_data = f.read().strip()
    
    print(f"Found seed file. Length: {len(encrypted_data)}")

    # 2. Send it to your local API
    url = "http://localhost:8080/decrypt-seed"
    print("Sending encrypted seed to API...")
    
    response = requests.post(url, json={"encrypted_seed": encrypted_data})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

except FileNotFoundError:
    print("ERROR: 'encrypted_seed.txt' not found! Make sure it is in this folder.")
except Exception as e:
    print(f"ERROR: {e}")
    