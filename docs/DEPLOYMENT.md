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

The API uses a multi-stage Dockerfile at the repository root:

```bash
# Build API image
docker build -t credit-risk-api .

# Run API container
docker run -p 8080:8080 \
  -e CREDIT_RISK_REQUIRE_AUTH=true \
  -e CREDIT_RISK_API_KEYS=your-api-key \
  credit-risk-api
```

See `Dockerfile` in the repository root for the full build configuration.

### Web (Next.js)

The web app uses a multi-stage Dockerfile in `apps/web/`:

```bash
# Build web image
cd apps/web
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8080 \
  -t credit-risk-web .

# Run web container
docker run -p 3000:3000 credit-risk-web
```

See `apps/web/Dockerfile` for the full build configuration.

### Docker Compose

Example `docker-compose.yml` for running both services:

```yaml
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - CREDIT_RISK_REQUIRE_AUTH=false
      - CREDIT_RISK_CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./data:/app/data
      - ./artifacts:/app/artifacts

  web:
    build:
      context: ./apps/web
      args:
        NEXT_PUBLIC_API_URL: http://localhost:8080
    ports:
      - "3000:3000"
    depends_on:
      - api
```

**Note:** `NEXT_PUBLIC_API_URL` must be accessible from the browser (use `http://localhost:8080`, not `http://api:8080`).

## Cloud Run Deployment

Both the FastAPI backend and Next.js frontend are deployed to Google Cloud Run with automated CI/CD via GitHub Actions.

### Prerequisites

- GCP project with Cloud Run and Artifact Registry enabled
- Service account with necessary permissions
- GitHub repository secrets configured:
  - `GCP_SA_KEY` - Service account JSON key
  - `GCP_PROJECT_ID` - GCP project ID
  - `GCP_REGION` - Deployment region (e.g., `us-central1`)
  - `CREDIT_RISK_API_URL` - Production API URL for web app
  - (Optional) `CREDIT_RISK_API_KEYS` - API keys for authentication

### API Deployment

Automatically deploys when changes are pushed to `main` branch affecting:

- `apps/api/**`
- `shared/**`
- `Dockerfile`
- `pyproject.toml`
- `uv.lock`

Workflow: `.github/workflows/deploy-api-cloudrun.yml`

**Service Configuration:**

- Memory: 1 GiB
- CPU: 1
- Timeout: 300s
- Port: 8080
- Min instances: 0 (scales to zero)

**Production URL:** Available via Cloud Run service URL

### Web Deployment (Next.js)

Automatically deploys when changes are pushed to `main` branch affecting `apps/web/**`.

Workflow: `.github/workflows/deploy-web-cloudrun.yml`

**Service Configuration:**

- Memory: 512 MiB
- CPU: 1
- Timeout: 60s
- Port: 3000
- Min instances: 0 (scales to zero)
- Max instances: 2

**Production URL:** [https://credit-risk-web-p24vtxpm5q-uc.a.run.app](https://credit-risk-web-p24vtxpm5q-uc.a.run.app)

See [ADR-011](../docs/1-ADRs/ADR-011-nextjs-cloud-run.md) for deployment architecture details.

### Manual Cloud Run Deployment

```bash
# Build and deploy API
gcloud builds submit --tag gcr.io/PROJECT_ID/credit-risk-api
gcloud run deploy credit-risk-api \
  --image gcr.io/PROJECT_ID/credit-risk-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Build and deploy Web
cd apps/web
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://your-api-url.run.app \
  -t gcr.io/PROJECT_ID/credit-risk-web .
docker push gcr.io/PROJECT_ID/credit-risk-web

gcloud run deploy credit-risk-web \
  --image gcr.io/PROJECT_ID/credit-risk-web \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --port 3000
```

## HF Spaces Deployment (Gradio)

The Gradio demo app is deployed to Hugging Face Spaces with automated sync via GitHub Actions.

**Live demo:** [huggingface.co/spaces/pkiage/credit_risk_modeling_demo](https://huggingface.co/spaces/pkiage/credit_risk_modeling_demo)

### Automated Deployment

Workflow: `.github/workflows/sync_to_hf_hub.yml`

Automatically syncs when changes are pushed to `main` branch affecting:

- `apps/gradio/**`
- `shared/**`

Requires GitHub secret `HF_TOKEN` with write access to the Space.

### Manual HF Spaces Setup

1. Create a new Space on Hugging Face
2. Set SDK to Gradio (Python 3.12)
3. Add environment variable: `CREDIT_RISK_API_URL` = your API URL
4. Push `apps/gradio/` contents to the Space repo:

```bash
cd apps/gradio
git remote add hf https://huggingface.co/spaces/USERNAME/SPACE_NAME
git push hf main
```

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
