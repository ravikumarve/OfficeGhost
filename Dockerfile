# GhostOffice Dockerfile
# Multi-stage build for optimized production image

# ─────────────────────────────────────────────
# BUILDER STAGE
# ─────────────────────────────────────────────
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ─────────────────────────────────────────────
# PRODUCTION STAGE
# ─────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r ghostoffice && useradd -r -g ghostoffice ghostoffice

# Create data directories
RUN mkdir -p /app/data/logs /app/data/backups /app/data/reports && \
    chown -R ghostoffice:ghostoffice /app

USER ghostoffice

# Environment defaults for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://host.docker.internal:11434

# Health check - verify Ollama is accessible
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:11434/api/tags', timeout=5)" || exit 1

# Expose dashboard port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]