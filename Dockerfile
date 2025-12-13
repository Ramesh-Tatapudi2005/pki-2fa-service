# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies
RUN apt-get update \
    && apt-get install -y cron tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy folders (Do NOT copy start.sh because we deleted it)
COPY src src
COPY scripts scripts
COPY cron cron
COPY *.pem .  

# We create start.sh INSIDE Linux so it is 100% correct and has no Windows errors
RUN echo '#!/bin/bash' > /app/start.sh \
    && echo 'echo "Starting cron..."' >> /app/start.sh \
    && echo '/usr/sbin/cron -f &' >> /app/start.sh \
    && echo 'echo "Starting API..."' >> /app/start.sh \
    && echo 'exec uvicorn src.main:app --host 0.0.0.0 --port 8080' >> /app/start.sh \
    && chmod +x /app/start.sh

# We also fix the cron file automatically
RUN sed -i 's/\r$//' cron/2fa-cron \
    && chmod 0644 cron/2fa-cron \
    && crontab cron/2fa-cron

# Create volume mount points
RUN mkdir -p /data /cron \
    && chmod 755 /data /cron

# Make python script executable
RUN chmod +x scripts/log_2fa_cron.py

EXPOSE 8080
CMD ["./start.sh"]