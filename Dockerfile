# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install Python deps into the image
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the full source code
COPY . .

# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim

WORKDIR /app

# Install cron + timezone data
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set timezone to UTC
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

# Create directories for volumes
RUN mkdir -p /data && mkdir -p /cron

# Copy installed Python packages and app code from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Install cron job (config file lives in /app/cron/2fa-cron)
RUN chmod 0644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

# Expose FastAPI port
EXPOSE 8080

# Start cron and the API server
CMD cron && uvicorn app.main:app --host 0.0.0.0 --port 8080
