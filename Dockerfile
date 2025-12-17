# -------------------------
# STAGE 1: BUILDER
# -------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# -------------------------
# STAGE 2: RUNTIME
# -------------------------
FROM python:3.11-slim

# Install cron + timezone
RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy application source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY cron/ ./cron/
COPY student_private.pem instructor_public.pem student_public.pem ./

# Convert CRLF → LF and register cron
RUN sed -i 's/\r$//' cron/2fa-cron && chmod 0644 cron/2fa-cron && crontab cron/2fa-cron

# Create persistence folder
RUN mkdir -p /data && chmod 755 /data

# Ensure cron script is executable
RUN chmod +x scripts/log_2fa_cron.py

EXPOSE 8080

# -------------------------
# START BOTH CRON + FASTAPI
# -------------------------
CMD ["sh", "-c", "cron && uvicorn src.main:app --host 0.0.0.0 --port 8080"]
