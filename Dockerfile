# Credit Risk API — multi-stage build for Google Cloud Run
# Build context must be the repo root (needs shared/, apps/api/, data/).

FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install only external dependencies (skip hatchling project build)
RUN uv sync --extra api --no-dev --frozen --no-install-project

# --- Production stage ---
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment with all dependencies
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY shared/ ./shared/
COPY apps/api/ ./apps/api/

# Copy training dataset
COPY data/processed/cr_loan_w2.csv ./data/processed/cr_loan_w2.csv

# Create writable artifacts directory for model persistence
RUN mkdir -p artifacts

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
