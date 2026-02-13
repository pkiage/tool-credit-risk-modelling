# App Feature Comparison

> Side-by-side comparison of the three frontend surfaces in the Credit Risk Platform.

## Architecture Overview

| | Marimo | Gradio | Next.js |
|---|---|---|---|
| **Role** | Explore | Validate | Ship |
| **Audience** | Data scientists, developers | Stakeholders, business users | End users, production |
| **Framework** | Marimo (Python notebooks) | Gradio 6.5 (Python) | Next.js 16 (TypeScript) |
| **Rendering** | Server-side (ASGI) | Server-side (Gradio server) | Client-side (React SPA) |
| **Backend** | Standalone (no API needed) | FastAPI via HTTP | FastAPI via HTTP |
| **Deployment** | HF Spaces (Docker) | HF Spaces (Gradio SDK) | Google Cloud Run (Docker) |
| **Live URL** | [credit-risk-notebooks](https://huggingface.co/spaces/pkiage/credit-risk-notebooks) | [credit_risk_modeling_demo](https://huggingface.co/spaces/pkiage/credit_risk_modeling_demo) | [Cloud Run](https://credit-risk-web-p24vtxpm5q-uc.a.run.app) |

## Feature Matrix

### Data Exploration

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Dataset overview (rows, cols, dtypes) | Yes | — | — |
| Missing value detection | Yes | — | — |
| Target distribution chart | Yes | — | — |
| Numeric feature histograms | Yes | — | — |
| Categorical feature distributions | Yes | — | — |
| Correlation heatmap | Yes | — | — |
| Feature-target box plots | Yes | — | — |
| Custom CSV upload | Yes | — | — |

> Marimo is the only surface with EDA capabilities — by design, exploration stays in notebooks.

### Model Training

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Train Logistic Regression | Yes | Yes | Yes |
| Train XGBoost | Yes | Yes | Yes |
| Train Random Forest | Yes | Yes | Yes |
| Test size configuration | Yes | Yes | Yes |
| Random state configuration | Yes | — | — |
| CV folds configuration | — | — | Yes |
| Undersample majority class | Yes | — | Yes |
| Auto feature selection (4 methods) | — | Yes | — |
| Manual feature selection | — | Yes | — |
| Training time display | — | Yes | Yes |
| Model ID tracking | — | Yes | Yes |

### Feature Selection Methods

| Method | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Tree Importance (RF/XGB) | — | Yes | — |
| LASSO (L1 regularization) | — | Yes | — |
| WoE/IV (Information Value) | — | Yes | — |
| Boruta (all-relevant) | — | Yes | — |
| Feature score visualization | — | Yes | — |
| Apply selection to training | — | Yes | — |

> Feature selection is exposed only through Gradio (stakeholder-facing workflow).

### Model Evaluation Metrics

| Metric / Visualization | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Accuracy | Yes | Yes | Yes |
| Precision | Yes | Yes | Yes |
| Recall | Yes | Yes | Yes |
| F1 Score | Yes | Yes | Yes |
| ROC AUC | Yes | Yes | Yes |
| Optimal threshold (Youden's J) | Yes | Yes | Yes |
| ROC curve | Yes | Yes | Yes |
| Confusion matrix | Yes | — | Yes |
| Feature importance chart | Yes | Yes | Yes |
| Precision-recall curve | Yes | — | — |
| Calibration curve | Yes | — | Yes |
| Brier score | Yes | — | — |

### Threshold Optimization

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Interactive threshold slider | Yes | — | — |
| Threshold vs metrics comparison | Yes | — | Yes |
| Sensitivity / specificity display | Yes | — | Yes |
| Youden's J visualization | Yes | — | — |
| Business impact cost calculator | Yes | — | — |
| Cost-optimal threshold | Yes | — | — |

> Deep threshold analysis lives in Marimo for data science exploration.

### Probability Calibration

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Calibration curve (reliability diagram) | Yes | — | — |
| Configurable bin count | Yes | — | — |
| Platt scaling (sigmoid) | Yes | — | — |
| Isotonic regression | Yes | — | — |
| Before/after comparison | Yes | — | — |
| Brier score comparison | Yes | — | — |
| Probability distribution histograms | Yes | — | — |

> Calibration analysis is a notebook-only capability.

### Prediction

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Single loan application form | — | Yes | Yes |
| Model selection dropdown | — | Yes | Yes |
| Binary prediction (Default / No Default) | — | Yes | Yes |
| Default probability | — | Yes | Yes |
| Confidence score | — | — | Yes |
| Threshold display | — | Yes | Yes |
| Visual probability bar | — | — | Yes |
| Auto-calc loan % of income | — | Yes | — |
| Client-side form validation | — | — | Yes |
| Field-level error messages | — | — | Yes |
| Refresh models list | — | Yes | Yes |

### Model Comparison

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Multi-model selection | Yes | Yes | Yes |
| ROC curve overlay | Yes | Yes | Yes |
| Metrics comparison table | Yes | Yes | Yes |
| Metrics grouped bar chart | — | Yes | Yes |
| Precision-recall overlay | Yes | — | — |
| Re-train comparison mode | — | — | Yes |
| Stored results comparison | — | Yes | Yes |
| Session-cached results | — | Yes | — |

### UI / UX

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Dark mode | — | — | Yes |
| Theme toggle (light/dark/system) | — | — | Yes |
| WCAG AAA color contrast | — | — | Yes |
| Keyboard navigation (focus rings) | — | — | Yes |
| Responsive design (mobile) | — | — | Yes |
| Loading spinners | — | Yes | Yes |
| Error alerts | — | Yes | Yes |
| Tabbed navigation | Yes (notebook routes) | Yes | Yes (pages) |
| Dashboard home page | Yes (landing page) | — | Yes |
| API health indicator | — | Yes | Yes |

### Charting Library

| | Marimo | Gradio | Next.js |
|---|---|---|---|
| **Library** | Plotly | Plotly | Recharts |
| **Interactivity** | Hover, zoom, pan | Hover, zoom, pan | Hover, tooltips |
| **Color scheme** | `shared/constants` | `shared/constants` | CSS variables |

### Security & Production

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| Security headers (XSS, CSP, etc.) | — | — | Yes |
| HTTPS enforcement | — | Yes (warning) | Yes |
| Client-side validation | — | — | Yes |
| API timeout handling | — | Yes (60s/300s) | Yes (30s/120s) |
| Structured error handling | — | Yes | Yes |
| Standalone Docker build | Yes | — | Yes |

### Deployment & CI/CD

| Feature | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| GitHub Actions workflow | Yes | Yes | Yes |
| Auto-deploy on push to main | Yes | Yes | Yes |
| Platform | HF Spaces (Docker) | HF Spaces (Gradio SDK) | Google Cloud Run |
| Container format | Dockerfile | SDK-managed | Dockerfile (standalone) |
| Environment variables | — | `CREDIT_RISK_API_URL` | `NEXT_PUBLIC_API_URL` |

## Shared Layer Usage

All three apps import from `shared/` to maintain a single source of truth:

| Import | Marimo | Gradio | Next.js |
|---|:---:|:---:|:---:|
| `shared/constants` (features, colors, params) | Yes | Yes | — (TS types mirror schemas) |
| `shared/logic/evaluation` | Yes | — (via API) | — (via API) |
| `shared/logic/threshold` | Yes | — (via API) | — (via API) |
| `shared/logic/preprocessing` | Yes | — (via API) | — (via API) |
| `shared/schemas/training` | Yes | — (via API) | — (TS interfaces) |
| `shared/schemas/metrics` | Yes | — (via API) | — (TS interfaces) |

- **Marimo**: Direct Python imports from `shared/` — runs logic locally.
- **Gradio**: Imports constants only; delegates ML logic to FastAPI.
- **Next.js**: No Python imports; mirrors Pydantic schemas as TypeScript interfaces.

## Summary: When to Use Which

| Goal | Use |
|---|---|
| Explore a dataset, prototype models, deep-dive analysis | **Marimo** |
| Demo to stakeholders, quick model training with feature selection | **Gradio** |
| Production-grade UI, end-user predictions, polished experience | **Next.js** |
| Threshold tuning, calibration analysis, cost-benefit modeling | **Marimo** |
| Compare models with stored results across sessions | **Gradio** or **Next.js** |
| Accessible, responsive, dark-mode interface | **Next.js** |

## Progression Path

```
Marimo (explore) → Gradio (validate) → Next.js (ship)
```

Each app serves a distinct phase in the ML workflow. Features intentionally differ — not every capability needs to exist in every surface. Marimo goes deep on analysis, Gradio bridges the gap to non-technical users, and Next.js delivers the production experience.
