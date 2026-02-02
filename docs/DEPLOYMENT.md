# Deployment Guide

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- uv (Python package manager)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CREDIT_RISK_APP_NAME` | `Credit Risk API` | API display name |
| `CREDIT_RISK_DEBUG` | `false` | Enable debug mode |
| `CREDIT_RISK_REQUIRE_AUTH` | `false` | Require API key auth |
| `CREDIT_RISK_API_KEYS` | `""` | Comma-separated API keys |
| `CREDIT_RISK_CORS_ORIGINS` | `*` | Comma-separated allowed origins |
| `CREDIT_RISK_LOG_LEVEL` | `INFO` | Logging level |
| `CREDIT_RISK_DEFAULT_DATASET_PATH` | `data/processed/cr_loan_w2.csv` | Training dataset path |
| `CREDIT_RISK_MODEL_ARTIFACTS_PATH` | `artifacts/` | Model persistence directory |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | API URL for Next.js |
| `CREDIT_RISK_API_URL` | `http://localhost:8000` | API URL for Gradio |

### Start Services

```bash
# Terminal 1: API
uv run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Next.js
cd apps/web && npm run dev

# Terminal 3: Gradio
uv run python -m apps.gradio.app
```

### Start with Authentication

```bash
CREDIT_RISK_REQUIRE_AUTH=true \
CREDIT_RISK_API_KEYS=dev-key-123,dev-key-456 \
uv run uvicorn apps.api.main:app --reload
```

## Docker Deployment

### API

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install uv && uv sync --extra api

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CREDIT_RISK_REQUIRE_AUTH=true
      - CREDIT_RISK_API_KEYS=${API_KEYS}
      - CREDIT_RISK_CORS_ORIGINS=http://localhost:3000

  web:
    build: ./apps/web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api
```

## Vercel Deployment (Next.js)

1. Connect repo to Vercel
2. Set root directory to `apps/web`
3. Add environment variable: `NEXT_PUBLIC_API_URL` = your API URL
4. Deploy

## HF Spaces Deployment (Gradio)

1. Create a new Space on Hugging Face
2. Set SDK to Gradio
3. Add environment variable: `CREDIT_RISK_API_URL` = your API URL
4. Push `apps/gradio/` to the Space repo

## Production Checklist

- [ ] Set `CREDIT_RISK_REQUIRE_AUTH=true`
- [ ] Generate strong API keys
- [ ] Restrict CORS origins to production domains
- [ ] Enable HTTPS (via reverse proxy / cloud provider)
- [ ] Set `CREDIT_RISK_DEBUG=false`
- [ ] Configure log rotation for `logs/audit.jsonl`
- [ ] Set up monitoring and alerting
- [ ] Review rate limits for expected traffic
- [ ] Back up model artifacts directory
