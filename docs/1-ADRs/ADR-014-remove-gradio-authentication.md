# ADR-014: Remove Gradio Authentication Layer

| Field | Value |
|-------|-------|
| Status | Proposed |
| Author | Paul / Claude |
| Date | 2026-02-08 |
| PR | _Added before merge_ |

## Context

The Gradio stakeholder demo application includes an API key authentication UI consisting of:

- API key input field (password type)
- "Verify" button that calls `/auth/verify` endpoint
- Authentication status indicator ("Not authenticated", "Authenticated", "Invalid key")
- `verify_key()` method in `CreditRiskAPI` client
- `set_api_key()` and `api_key` attribute for managing keys
- Authorization header injection in all API requests

However, the FastAPI backend has `require_auth: bool = False` by default ([apps/api/config.py:29](../../apps/api/config.py#L29)), meaning the API does not require authentication in development mode. When `require_auth` is disabled, the API's authentication dependency returns `"anonymous"` without validating any credentials.

This creates the same misalignment observed in the Next.js web app (see [ADR-013](ADR-013-remove-web-authentication.md)):
- **Gradio app**: Prompts for API key verification
- **API**: Does not require or validate authentication by default

Users must "verify" an API key to proceed, but the underlying API accepts requests without any credentials, creating unnecessary friction without providing actual security.

## Decision

**Remove the authentication layer entirely** from the Gradio application, including:

1. API key input field, verify button, and auth status UI (`apps/gradio/app.py`)
2. `verify_key()` method in `CreditRiskAPI` (`apps/gradio/api_client.py`)
3. `set_api_key()` method and `api_key` attribute
4. Authorization header logic in `_headers()` method

## Rationale

### Why Remove Authentication?

1. **API is open by default**: The backend does not enforce authentication in development mode, making Gradio-layer auth security theater

2. **Demo platform**: The Gradio app is:
   - Intended for stakeholder demonstrations
   - Deployed on Hugging Face Spaces as a public demo
   - Used for rapid prototyping and validation
   - Not handling sensitive production data

3. **Consistency with web app**: ADR-013 removed authentication from the Next.js web app for the same reasons; Gradio should follow the same approach

4. **Better UX**: Removing the verification step improves the demo experience—stakeholders can immediately interact with the application

5. **Authentication framework preserved**: The API retains its authentication module (`apps/api/auth.py`, `apps/api/routers/auth.py`) for future use when/if authentication is needed

### When to Re-enable Authentication?

If the platform moves to production or handles sensitive data, authentication can be re-enabled by:

1. Setting `CREDIT_RISK_REQUIRE_AUTH=true` in API environment
2. Providing valid API keys via `CREDIT_RISK_API_KEYS="key1,key2"`
3. Re-implementing Gradio authentication UI if needed
4. Using the existing `/auth/verify` endpoint

The API's auth infrastructure remains intact for this purpose.

## Consequences

### Positive

- **Simpler UX**: Stakeholders can use the demo immediately without authentication barriers
- **Consistency**: Gradio app behavior now matches both the API's authentication posture and the Next.js web app's approach
- **Less code**: Removed ~40 lines of auth-related code
- **Clearer intent**: Application is explicitly positioned as a demo/validation tool

### Negative

- **No access control**: Anyone with network access can use the Hugging Face Spaces deployment
  - **Mitigation**: This is already the case with public HF Spaces deployments; auth was not providing security
- **Must rebuild auth for production**: If security is needed later, Gradio authentication must be re-implemented
  - **Mitigation**: API auth framework is preserved; Gradio auth can be quickly restored using git history

### Neutral

- **API authentication unchanged**: The backend's auth module remains available but unused (can be enabled via environment variables)
- **Next.js app unchanged**: The web app already has authentication removed per ADR-013

## Alternatives Considered

### 1. Enable API Authentication

Set `require_auth = True` and provide API keys to secure the backend.

**Rejected because**:
- Adds complexity for demo use cases
- No clear security requirement or threat model for public HF Spaces demo
- Would require distributing API keys to demo users, defeating the purpose of a public demo

### 2. Make Gradio Auth Optional

Check API's auth status and conditionally show verification UI.

**Rejected because**:
- Added complexity without clear benefit
- Still requires maintaining auth infrastructure
- Authentication should be all-or-nothing, not configurable per-layer

### 3. Keep Gradio Auth, Remove API Auth

Rely on Gradio-layer authentication only.

**Rejected because**:
- API endpoints remain directly accessible, bypassing Gradio auth
- Creates false sense of security
- Gradio auth cannot protect API without backend enforcement

## Related Documents

- [ADR-013: Remove Web Authentication Layer](ADR-013-remove-web-authentication.md) - Parallel decision for Next.js web app
- [ADR-004: API Key Authentication](ADR-004-api-key-authentication.md) - Original API authentication design
- [apps/api/config.py](../../apps/api/config.py) - API authentication configuration
- [apps/api/auth.py](../../apps/api/auth.py) - API authentication module (preserved)
- [CLAUDE.md](../../CLAUDE.md) - Project guidelines (no security requirements specified)

## Implementation

Changes made in PR #[TBD]:

**Modified files:**
- `apps/gradio/app.py` - Removed:
  - API key input field, verify button, auth status UI (~25 lines)
  - `_verify_key()` function (~9 lines)
  - Button click event handler

- `apps/gradio/api_client.py` - Removed:
  - `verify_key()` method (~13 lines)
  - `set_api_key()` method (~6 lines)
  - `api_key` attribute and documentation
  - Authorization header logic from `_headers()` method

**Preserved (for future use):**
- `apps/api/auth.py` - Authentication dependency
- `apps/api/routers/auth.py` - `/auth/verify` endpoint
- API configuration: `require_auth`, `api_keys` settings

**Testing:**
- Manual verification: Gradio app loads without authentication UI
- API calls succeed without Authorization headers
- All tabs (Train, Predict, Compare) functional
