# Stage 1: Builder - Installs Python dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Minimal base image for execution
FROM python:3.11-slim

# Set Timezone to UTC (CRITICAL for correct TOTP generation)
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies (cron and timezone data)
RUN apt-get update \
    && apt-get install -y cron tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code and keys
# (Note: We do NOT copy start.sh because we deleted it)
COPY src src
COPY scripts scripts
COPY cron cron
COPY *.pem .  

# Setup cron job
# 1. sed removes Windows 'CR' characters automatically
# 2. chmod sets correct permissions
# 3. crontab loads the file
RUN sed -i 's/\r$//' cron/2fa-cron \
    && chmod 0644 cron/2fa-cron \
    && crontab cron/2fa-cron

# Create volume mount points for persistence
RUN mkdir -p /data /cron \
    && chmod 755 /data /cron

# Make python logging script executable
RUN chmod +x scripts/log_2fa_cron.py

# Expose the API port
EXPOSE 8080

# --- 🟢 THE NO-SCRIPT FIX 🟢 ---
# This runs cron and the API server directly.
# It completely bypasses the need for a 'start.sh' file.
CMD ["sh", "-c", "cron && uvicorn src.main:app --host 0.0.0.0 --port 8080"]