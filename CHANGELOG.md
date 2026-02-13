# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- [web] Number input step validation rejecting valid income, employment length, and loan amount values
- [web] Compare page ROC curve X-axis showing array indices instead of false positive rate
- [web] Model ID text overflow on home page and training summary on mobile viewports

## [0.1.0] - 2026-02-11

Initial release — migrated from a Streamlit prototype to a production-grade monorepo
with four integrated application layers.

### Added

#### Shared Layer (`shared/`)

- [shared] Pydantic v2 schemas for loan applications, training results, predictions, and audit logs (#12)
- [shared] Preprocessing and evaluation logic using sklearn (#12)
- [shared] Threshold optimization using Youden's J statistic (#12)
- [shared] Automatic feature selection: Boruta, Lasso, Tree Importance, WOE-IV (#38)

#### API Layer (`apps/api/`)

- [api] FastAPI service with health, train, predict, and model endpoints (#12)
- [api] API key authentication with configurable enforcement (#19)
- [api] Rate limiting and audit logging (#19)
- [api] Model persistence with in-memory cache and filesystem storage (#12)
- [api] Feature selection endpoint supporting four methods (#38)

#### Gradio App (`apps/gradio/`)

- [gradio] Training tab with model configuration and feature selection (#12, #31)
- [gradio] Prediction tab with probability display (#12)
- [gradio] Model comparison tab (#12)
- [gradio] Deployed to Hugging Face Spaces (#26)

#### Next.js UI (`apps/web/`)

- [web] Next.js 16 scaffold with App Router, TypeScript strict, and Recharts dashboard (#17)
- [web] Training page with ROC curve, calibration plot, and confusion matrix (#17)
- [web] Prediction page with input form and probability visualizations (#17)
- [web] Model comparison page with side-by-side metrics (#17)
- [web] Dark mode toggle with system preference detection (#46)
- [web] Deployed to Cloud Run (#37)

#### Notebooks (`notebooks/`)

- [marimo] Interactive exploration notebooks stored as `.py` files (#14)
- [marimo] Deployed to Hugging Face Spaces via Docker (#36)
- [marimo] Landing page with HF Spaces link (#41)

#### Infrastructure

- [ci] Monorepo setup with uv, Ruff, pyproject.toml (#12)
- [ci] Pytest + npm test coverage reporting (#24)
- [ci] deptry dependency checking and security scanning (#24, #25)
- [ci] Dockerfile and Cloud Run deployment workflow for API (#30)
- [ci] Monorepo-aware Gradio deploy to HF Spaces (#26, #28)
- [ci] Cloud Run deployment for Next.js app (#37)

#### Documentation

- [docs] RFC-001: Platform Architecture
- [docs] RFC-002: API Layer
- [docs] RFC-006: Auth & Security
- [docs] ADR-001 through ADR-014 covering all architectural decisions (#40)
- [docs] Deployment guide for Cloud Run and HF Spaces (#43)
- [docs] Environment variables reference
- [docs] Parallel development and worktree guidance (#35)

### Changed

- [gradio] Upgraded Gradio from 4.0.0 to 6.5.1 (#29)
- [marimo] Added tabulate dependency for pandas `to_markdown` (#42)
- [web] Removed authentication layer — internal tool, unnecessary friction (#44)
- [gradio] Removed authentication layer (#45)

### Fixed

- [shared/api] Phase 1-2 code review fixes (#13)
- [notebooks] Phase 3 review fixes (#15)
- [gradio] Phase 4 review fixes — session state, error handling, loading states (#16)
- [web] Phase 5 review fixes — validation, compare toggle, RFC decisions (#18)
- [api] Security hardening from Phase 6 review (#20)
- [ci] deptry monorepo configuration (#25)
- [ci] HF Spaces deploy git init and python_version (#27, #28)
- [ci] Copy shared/constants.py to HF Spaces deployment (#32)
- [gradio] Compare tab not showing trained models (#33)
- [gradio] Boruta feature selection timeout (#39)
- [web] Trailing slashes on API endpoint paths (#47)
- [web] Dark mode WCAG AAA color contrast (#48)

### Security

- [api] CORS configuration with configurable origins
- [web] Security headers in Next.js (CSP, X-Frame-Options, etc.)
- [api] Input validation via Pydantic schemas
- [api] Path traversal protection in model store
- [api] Security hardening audit (#20)

### Pre-monorepo

- Initial Streamlit prototype with credit risk model (#1, #7, #11)
