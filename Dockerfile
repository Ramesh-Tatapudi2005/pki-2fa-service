# ===========================
# Stage 1 - Build Dependencies
# ===========================
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ===========================
# Stage 2 - Runtime Image
# ===========================
FROM python:3.11-slim

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY src src
COPY scripts scripts
COPY cron cron
COPY student_private.pem student_public.pem instructor_public.pem ./

# Fix CRLF → LF for cron
RUN sed -i 's/\r$//' cron/2fa-cron && chmod 0644 cron/2fa-cron && crontab cron/2fa-cron

RUN mkdir -p /data /cron && chmod 755 /data /cron
RUN chmod +x scripts/log_2fa_cron.py

EXPOSE 8080

CMD cron && uvicorn src.main:app --host 0.0.0.0 --port 8080
