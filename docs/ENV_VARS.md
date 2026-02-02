# Environment Variables

| Variable | Layer | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `CREDIT_RISK_APP_NAME` | api | No | `Credit Risk API` | Application name |
| `CREDIT_RISK_DEBUG` | api | No | `false` | Enable debug mode |
| `CREDIT_RISK_DEFAULT_DATASET_PATH` | api | No | `data/processed/cr_loan_w2.csv` | Path to default training dataset |
| `CREDIT_RISK_MODEL_ARTIFACTS_PATH` | api | No | `artifacts/` | Directory for persisted model artifacts |
| `CREDIT_RISK_LOG_LEVEL` | api | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CREDIT_RISK_CORS_ORIGINS` | api | No | `*` | Comma-separated allowed CORS origins |
| `CREDIT_RISK_REQUIRE_AUTH` | api | No | `false` | Enable API key authentication |
| `CREDIT_RISK_API_KEYS` | api | If auth enabled | — | Comma-separated API keys |
| `CREDIT_RISK_API_URL` | gradio | No | `http://localhost:8000` | API base URL for Gradio app |
| `NEXT_PUBLIC_API_URL` | web | No | `http://localhost:8000` | API URL for browser requests |
