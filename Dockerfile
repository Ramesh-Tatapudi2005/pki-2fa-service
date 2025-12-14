FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim
WORKDIR /app

# Timezone UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY app /app
COPY scripts /app/scripts
COPY cron /app/cron
COPY student_private.pem /app/student_private.pem

RUN chmod +x /app/scripts/log_2fa_cron.py
RUN sed -i 's/\r$//' /app/cron/2fa-cron && chmod 0644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080
