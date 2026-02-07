# ADR-004: API Key Authentication

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author | Paul / Claude |
| Date | 2026-02-02 |
| RFC | [RFC-006](../0-RFCs/RFC-006-auth-polish.md) |

## Context

The API needs basic access control to prevent unauthorized usage, enable audit trails per user, and support rate limiting. We needed an authentication approach that balances security with simplicity.

## Decision

Use API key authentication via the `Authorization: Bearer <key>` header.

**Implementation:**
- Keys stored as comma-separated environment variable (`CREDIT_RISK_API_KEYS`)
- Auth can be disabled for development (`CREDIT_RISK_REQUIRE_AUTH=false`)
- Protected endpoints: `POST /train`, `POST /predict`, `POST /models/{id}/persist`
- Public endpoints: `GET /health`, `GET /models`
- Web UI stores key in cookie, includes in API requests
- Gradio app has key input field

## Alternatives Considered

- **OAuth2 / JWT** — Industry standard but complex for a demo platform; can be added later
- **No auth (public API)** — No protection against abuse, no per-user audit trail
- **Supabase / Auth0** — External dependency, cost, overkill for current scope

## Consequences

- API keys must be provisioned manually (no self-service UI)
- Keys are not hashed in memory (acceptable for env-var-based approach)
- Upgrade path to OAuth2/JWT documented in RFC-006
- All protected endpoints return 401 without valid key
- Rate limiting keys off IP address, not API key (SlowAPI limitation)
