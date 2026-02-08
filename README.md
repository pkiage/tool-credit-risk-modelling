# Credit Risk Modelling Platform

A production-grade credit risk modelling platform with interactive exploration, stakeholder demos, and a production UI.

## Architecture

```text
apps/web/     → Next.js 16 (App Router, TypeScript strict) — Production UI
apps/api/     → FastAPI (Python 3.12+, async-first) — Model serving
apps/gradio/  → Gradio (stakeholder demos, HF Spaces)
shared/       → Pydantic schemas + business logic (single source of truth)
notebooks/    → Marimo (.py files only) — Developer exploration
docs/         → RFCs, ADRs, deployment guide
```

**UI progression:** Marimo (explore) → Gradio (validate) → Next.js (ship)

## Quick Start

```bash
# Install dependencies
uv sync --extra api --extra dev

# Start API (no auth)
uv run uvicorn apps.api.main:app --reload

# Start API (with auth)
CREDIT_RISK_REQUIRE_AUTH=true CREDIT_RISK_API_KEYS=my-key uv run uvicorn apps.api.main:app --reload

# Start Next.js UI
cd apps/web && npm install && npm run dev

# Start Gradio demo
uv run python -m apps.gradio.app
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/auth/verify` | Yes | Verify API key |
| POST | `/train` | Yes | Train a model |
| POST | `/predict` | Yes | Make predictions |
| GET | `/models` | No | List models |
| GET | `/models/{id}` | No | Get model metadata |
| GET | `/models/{id}/results` | No | Get training results |
| POST | `/models/{id}/persist` | Yes | Persist model to disk |

## Documentation

| Document | Description |
|----------|-------------|
| [RFCs](docs/0-RFCs/RFC-README.md) | Architecture proposals and design specs |
| [ADRs](docs/1-ADRs/ADR-README.md) | Architecture decision records |
| [Deployment Guide](docs/DEPLOYMENT.md) | Cloud Run deployment instructions |
| [Environment Variables](docs/ENV_VARS.md) | Configuration reference |

## Contributing

1. Create a feature branch: `git checkout -b feature/description`
2. Use conventional commits: `feat(scope): description`
3. Run tests: `uv run pytest && npm test`
4. Run linting: `uv run ruff check . && npm run lint`
5. Push and create a PR

## References

- [Credit Risk Modeling in Python (Datacamp)](https://www.datacamp.com/courses/credit-risk-modeling-in-python) — Methodology and data
- [Threshold-Moving for Imbalanced Classification](https://machinelearningmastery.com/threshold-moving-for-imbalanced-classification/) — Youden's J statistic

## License

OpenRAIL
