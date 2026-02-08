# Environment Variables

## Application Variables

| Variable | Layer | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `CREDIT_RISK_APP_NAME` | api | No | `Credit Risk API` | Application name |
| `CREDIT_RISK_DEBUG` | api | No | `false` | Enable debug mode (set to `false` in production) |
| `CREDIT_RISK_DEFAULT_DATASET_PATH` | api | No | `data/processed/cr_loan_w2.csv` | Path to default training dataset |
| `CREDIT_RISK_MODEL_ARTIFACTS_PATH` | api | No | `artifacts/` | Directory for persisted model artifacts |
| `CREDIT_RISK_LOG_LEVEL` | api | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CREDIT_RISK_CORS_ORIGINS` | api | No | `*` | Comma-separated allowed CORS origins (restrict in production) |
| `CREDIT_RISK_REQUIRE_AUTH` | api | No | `false` | Enable API key authentication (set to `true` in production) |
| `CREDIT_RISK_API_KEYS` | api | If auth enabled | — | Comma-separated API keys (required if auth enabled) |
| `CREDIT_RISK_API_URL` | gradio | No | `http://localhost:8000` | API base URL for Gradio app |
| `NEXT_PUBLIC_API_URL` | web | No | `http://localhost:8000` | API URL for browser requests (baked into client bundle at build time) |

## Deployment-Specific Notes

### Google Cloud Run (API & Web)

**API Service:**

- All `CREDIT_RISK_*` variables are set as Cloud Run environment variables
- Production uses Cloud Run's built-in HTTPS (no separate reverse proxy needed)
- Default port is 8080 (automatically set by Cloud Run)

**Web Service:**

- `NEXT_PUBLIC_API_URL` is passed as a Docker build arg during GitHub Actions workflow
- The value is inlined into the client bundle at build time
- Changing this value requires rebuilding and redeploying the web image

### Hugging Face Spaces (Gradio)

- Only requires `CREDIT_RISK_API_URL` to point to the deployed API
- Set via Space settings or `.env` file in the Space repo
- HF Spaces automatically provides HTTPS endpoints

## Production Recommendations

| Variable | Production Value |
|----------|------------------|
| `CREDIT_RISK_DEBUG` | `false` |
| `CREDIT_RISK_REQUIRE_AUTH` | `true` |
| `CREDIT_RISK_API_KEYS` | Strong random keys (e.g., `openssl rand -hex 32`) |
| `CREDIT_RISK_CORS_ORIGINS` | Specific domains only (e.g., `https://your-app.run.app`) |
| `NEXT_PUBLIC_API_URL` | Your Cloud Run API URL (e.g., `https://credit-risk-api-xxx.run.app`) |
