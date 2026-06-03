# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /app/deps /app/deps
ENV PYTHONPATH="/app/deps:${PYTHONPATH}"

# Copy application code
COPY . .

# Cloud Run sets PORT env var; default to 8000 for local
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE ${PORT}

# Run with uvicorn — Cloud Run sends SIGTERM for graceful shutdown
# Use shell form so $PORT is expanded from environment at runtime
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
