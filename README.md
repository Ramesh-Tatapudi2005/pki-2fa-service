# 🔐 PKI-Based TOTP 2FA Authentication Microservice

Enterprise-grade authentication microservice implementing **Public Key Infrastructure (PKI)** and **Time-based One-Time Passwords (TOTP)** using Docker.

---

## 📌 Objective

Build a secure, containerized microservice that:
- Uses **RSA-4096** for secure seed transmission
- Implements **TOTP-based 2FA**
- Runs inside Docker with **cron automation**
- Persists data across container restarts

---

## 🛡️ Cryptography Used

- RSA **4096-bit** key pair (public exponent 65537)
- **RSA-OAEP (SHA-256 + MGF1)** for seed decryption
- **RSA-PSS (SHA-256)** for commit signing
- Encrypted commit proof using instructor public key

---

## 🔐 TOTP Configuration

- Algorithm: **SHA-1**
- Digits: **6**
- Time period: **30 seconds**
- Verification window: **±1 period**
- Seed format: **64-char hex → Base32**

---

## 🚀 API Endpoints

### 🔓 POST `/decrypt-seed`
Decrypts the encrypted seed and stores it persistently.

**Request**
```json
{
  "encrypted_seed": "BASE64_STRING"
}
```

**Response**
```json
{ "status": "ok" }
```

---

### 🔢 GET `/generate-2fa`
Generates the current TOTP code.

**Response**
```json
{
  "code": "123456",
  "valid_for": 30
}
```

---

### ✅ POST `/verify-2fa`
Verifies a submitted TOTP code.

**Request**
```json
{
  "code": "123456"
}
```

**Response**
```json
{
  "valid": true
}
```

---

## ⏱️ Cron Job

- Executes **every minute**
- Reads seed from `/data/seed.txt`
- Generates TOTP code
- Logs to `/cron/last_code.txt`
- Uses **UTC timezone**

---

## 🐳 Docker Implementation

- Multi-stage Dockerfile
- Cron daemon + API server
- Exposes port **8080**
- Uses named volumes for persistence

---

## 📁 Project Structure

```
pki-2fa-service/
├── src/
├── scripts/
├── cron/
│   └── 2fa-cron
├── student_private.pem
├── student_public.pem
├── instructor_public.pem
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitattributes
├── .gitignore
└── README.md
```

---

## 🧪 Local Testing

```bash
docker-compose build
docker-compose up -d
```

---

## ✅ Status


