# RFC-001: Credit Risk Modeling Platform Architecture

| Field | Value |
|-------|-------|
| Status | Draft |
| Author(s) | Claude |
| Updated | 2025-01-30 |
| GitHub Issue | — |
| Obsoletes | — |

## Objective

Migrate the existing Streamlit-based credit risk modeling demo to a production-grade monorepo with clear separation between API (FastAPI), UI layers (Marimo → Gradio → Next.js), and shared business logic.

**Goals:**

- Single source of truth for schemas and ML logic in `shared/`
- Interactive learning via Marimo notebooks deployable to Molab
- Stakeholder demos via Gradio on HF Spaces
- Production UI via Next.js with typed API integration
- Audit trail for model training and predictions

**Non-goals:**

- Distributed model serving (single-instance API is sufficient)
- Real-time streaming predictions
- Multi-tenant authentication (demo-level auth only)

## Motivation

The current implementation scored 3.2/10 in technical assessment due to:

- Zero test coverage — bugs discovered only in production
- No error handling — crashes on malformed input
- Hard-coded paths — Windows-specific, non-portable
- Deprecated APIs — `@st.cache` instead of `@st.cache_data`
- No separation of concerns — ML logic entangled with UI

**Who is affected:**

- Developers cannot safely refactor without tests
- Stakeholders see crashes during demos
- Users cannot run locally without Windows + Graphviz path hacks

**Current pain points:**

- Adding a new model requires touching UI code
- Threshold optimization logic duplicated across views
- No way to persist or serve trained models

## User Benefit

**Release notes headline:** "Credit risk models now trainable via API, comparable in interactive notebooks, and deployable to production."

Concrete benefits:

- Train and compare models without writing code (Gradio/Next.js UI)
- Explore threshold optimization interactively (Marimo notebooks)
- Integrate predictions into external systems (FastAPI endpoints)
- Audit model decisions for compliance review

## Design Proposal

### Overview

Three-tier architecture with progressive UI fidelity:

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                             │
│  Marimo (explore) → Gradio (validate) → Next.js (ship)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       API Layer                             │
│              FastAPI (apps/api/)                            │
│         /train  /predict  /models  /health                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Shared Layer                            │
│    Pydantic Schemas + Business Logic (shared/)              │
│    LoanApplication, TrainingConfig, Youden's J, etc.        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
│         cr_loan_w2.csv | User Uploads | Artifacts           │
└─────────────────────────────────────────────────────────────┘
```

### System Architecture (Mermaid)

```mermaid
flowchart TB
    subgraph "Client Layer"
        WEB["Next.js 16<br/>(apps/web)"]
        MOLAB["Marimo on Molab<br/>(notebooks/)"]
        GRADIO["Gradio<br/>(apps/gradio)"]
    end

    subgraph "API Layer"
        API["FastAPI<br/>(apps/api)"]
        API --> TRAIN["/train"]
        API --> PREDICT["/predict"]
        API --> MODELS["/models"]
    end

    subgraph "Shared Layer"
        SCHEMAS["Pydantic Schemas"]
        LOGIC["Business Logic"]
    end

    subgraph "Data Layer"
        CSV["cr_loan_w2.csv"]
        UPLOAD["User Uploads"]
        ARTIFACTS["Model Artifacts"]
    end

    WEB --> API
    GRADIO --> API
    MOLAB --> SCHEMAS
    MOLAB --> LOGIC
    API --> SCHEMAS
    API --> LOGIC
    TRAIN --> CSV
    TRAIN --> UPLOAD
    PREDICT --> ARTIFACTS
```

### UI Layer Progression

```mermaid
flowchart LR
    M["Marimo<br/>notebooks/"] --> DEV["Developer<br/>exploration"]
    G["Gradio<br/>apps/gradio/"] --> STAKE["Stakeholder<br/>validation"]
    N["Next.js<br/>apps/web/"] --> PROD["End user<br/>production"]

    M -.->|"validate UX"| G
    G -.->|"inform design"| N
```

### API / Interface Changes

#### Endpoints

| Method | Path | Request | Response |
|--------|------|---------|----------|
| `POST` | `/train` | `TrainingConfig` + file | `TrainingResult` |
| `POST` | `/predict` | `PredictionRequest` | `PredictionResponse` |
| `GET` | `/models` | — | `list[ModelSummary]` |
| `POST` | `/models/{id}/persist` | — | `{path, instructions}` |
| `GET` | `/health` | — | `{status: "ok"}` |

#### Core Schemas

```python
# shared/schemas/loan.py
class LoanApplication(BaseModel):
    person_age: int = Field(ge=18, le=120)
    person_income: float = Field(gt=0)
    person_emp_length: float = Field(ge=0)
    loan_amnt: float = Field(gt=0)
    loan_int_rate: float = Field(gt=0, le=100)
    loan_percent_income: float = Field(ge=0, le=1)
    cb_person_cred_hist_length: int = Field(ge=0)
    person_home_ownership: Literal["RENT", "OWN", "MORTGAGE", "OTHER"]
    loan_intent: Literal["EDUCATION", "MEDICAL", "VENTURE", "PERSONAL", "DEBTCONSOLIDATION", "HOMEIMPROVEMENT"]
    loan_grade: Literal["A", "B", "C", "D", "E", "F", "G"]
    cb_person_default_on_file: Literal["Y", "N"]

# shared/schemas/training.py
class TrainingConfig(BaseModel):
    model_type: Literal["logistic_regression", "xgboost", "random_forest"]
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    random_state: int = 42

class TrainingResult(BaseModel):
    model_id: str
    metrics: ModelMetrics
    optimal_threshold: float
    feature_importance: dict[str, float] | None

# shared/schemas/metrics.py
class ThresholdResult(BaseModel):
    threshold: float
    sensitivity: float  # TPR
    specificity: float  # TNR
    youden_j: float

class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    threshold_analysis: ThresholdResult
    roc_curve: dict
    confusion_matrix: list[list[int]]
```

### Directory Structure

```
/
├── apps/
│   ├── web/                    # Next.js 16 (App Router)
│   ├── api/                    # FastAPI
│   └── gradio/                 # Gradio (HF Spaces)
├── shared/                     # Single Source of Truth
│   ├── schemas/                # Pydantic models
│   └── logic/                  # Business logic (threshold, evaluation)
├── notebooks/                  # Marimo (.py files)
├── data/raw/                   # cr_loan_w2.csv
├── tests/
├── docs/
│   ├── RFCs/
│   └── ADRs/
├── pyproject.toml
├── package.json
└── CLAUDE.md
```

### Usage Examples

**Training via API:**

```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"model_type": "xgboost", "test_size": 0.2}'
```

**Prediction via API:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"applications": [{"person_age": 25, ...}]}'
```

**Interactive exploration (Marimo):**

```bash
marimo run notebooks/02_model_comparison.py
```

## Alternatives Considered

### Alternative 1: Refactor Streamlit in place

**Pros:** Faster initial progress, familiar to current users

**Cons:** Still tied to Streamlit's limitations, no API layer, can't serve models

**Why not chosen:** Doesn't address core architectural issues; tech debt remains

### Alternative 2: Full Next.js + tRPC

**Pros:** Type-safe end-to-end, single language (TypeScript)

**Cons:** Loses Python ML ecosystem, harder to iterate on model logic

**Why not chosen:** Credit risk modeling benefits from Python's ML libraries

### Alternative 3: Jupyter + Voila

**Pros:** Familiar notebook paradigm

**Cons:** Poor git diffs, no typed schemas, limited interactivity

**Why not chosen:** Marimo offers better DX with .py files and reactive cells

## Dependencies

**New dependencies:**

- `uv` — Python package management
- `pydantic>=2.0` — Schema validation
- `fastapi` — API framework
- `marimo` — Interactive notebooks
- `gradio` — Stakeholder demos

**Dependent projects:**

- HF Spaces deployment (Gradio)
- Molab deployment (Marimo)
- Vercel deployment (Next.js)

## Engineering Impact

**Maintenance:** Shared logic owned by ML team; UI layers owned by respective teams

**Testing:**

- `shared/` — 90%+ coverage required
- `apps/api/` — Integration tests for all endpoints
- `apps/web/` — Component tests + E2E

**Build impact:** Monorepo with `uv` workspaces (Python) and `npm` workspaces (Node)

**API surface:** New public API at `/train`, `/predict`, `/models`

## Platforms and Environments

| Platform | Layer | Notes |
|----------|-------|-------|
| Local | All | `uv run`, `npm run dev` |
| Molab | Marimo | Notebook deployment |
| HF Spaces | Gradio | Docker-based |
| Vercel | Next.js | Edge deployment |
| Any cloud | FastAPI | Containerized |

## Best Practices

- All Pydantic schemas in `shared/` — never define models in app layers
- TypeScript interfaces derived from Pydantic (manual sync or codegen)
- Marimo notebooks import from `shared/`, never duplicate logic
- Audit events for all training and prediction operations

## Tutorials and Examples

- `notebooks/01_eda.py` — Dataset exploration
- `notebooks/02_model_comparison.py` — Train and compare models
- `notebooks/03_threshold_optimization.py` — Youden's J walkthrough
- `docs/` — API usage examples

## User Impact

**User-facing changes:**

- New API endpoints for programmatic access
- New Gradio UI for stakeholder demos
- New Next.js UI (replaces Streamlit)

**Migration:**

- Existing Streamlit users redirect to new UI
- No data migration required (stateless)

## Detailed Design

See inline code examples above. Full implementation in:

- `shared/schemas/` — All Pydantic models
- `shared/logic/threshold.py` — Youden's J implementation
- `apps/api/routers/` — FastAPI endpoints

## Questions and Discussion Topics

1. **Model persistence backend** — Local filesystem, S3, or MLflow?
2. **Auth strategy** — None for demo, API key, or OAuth?
3. **Chart library for Next.js** — Recharts, Plotly.js, or Nivo?
4. **TypeScript sync** — Manual or `datamodel-code-generator`?
5. **Gradio placement** — Standalone HF Space or embedded in Next.js?

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-01-30 | Claude | Initial draft |
