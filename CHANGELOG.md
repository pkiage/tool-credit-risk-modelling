# Changelog

## [Unreleased]

### Added
- Credit risk model training API (FastAPI, async)
- Shared Pydantic schemas and business logic layer
- Interactive Marimo notebooks for exploration
- Gradio stakeholder demo app
- Next.js production UI with TypeScript strict mode
- API key authentication
- Model persistence (in-memory + filesystem)
- Rate limiting on API endpoints
- Audit logging for training and prediction events

### Security
- CORS configuration
- Security headers in Next.js
- SameSite/Secure cookie flags
- Input validation via Pydantic schemas
- Path traversal protection in model store

### Documentation
- RFC-001: Platform Architecture
- RFC-002: API Layer
- RFC-006: Auth & Security
- ADR-001 through ADR-008 covering all architectural decisions
- Environment variables reference
- Deployment guide
