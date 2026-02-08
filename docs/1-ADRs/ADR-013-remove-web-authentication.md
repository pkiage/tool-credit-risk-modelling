# ADR-013: Remove Web Authentication Layer

| Field | Value |
|-------|-------|
| Status | Proposed |
| Author | Paul / Claude |
| Date | 2026-02-08 |
| PR | _Added before merge_ |

## Context

The Next.js web application was initially built with an API key authentication layer consisting of:

- Login page (`/login`) requiring API key input
- Middleware enforcing authentication on all routes
- Cookie-based session management
- Logout functionality

However, the FastAPI backend has `require_auth: bool = False` by default ([apps/api/config.py:29](../../apps/api/config.py#L29)), meaning the API does not require authentication in development mode. When `require_auth` is disabled, the API's authentication dependency returns `"anonymous"` without validating any credentials.

This created a misalignment where:
- **Web app**: Always enforces authentication (login required to access any page)
- **API**: Does not require or validate authentication by default

Users must "log in" with an API key to access a web UI that communicates with an open API, creating unnecessary friction without providing actual security.

## Decision

**Remove the web authentication layer entirely** from the Next.js application, including:

1. Login page (`apps/web/app/login/page.tsx`)
2. Middleware authentication checks (`apps/web/middleware.ts`)
3. Logout button component (`apps/web/components/logout-button.tsx`)
4. API key cookie management in `api-client.ts`
5. 401 redirect logic in the API client

## Rationale

### Why Remove Authentication?

1. **API is open by default**: The backend does not enforce authentication in development mode, making web-layer auth security theater

2. **Development/demo platform**: This application is:
   - Migrated from Streamlit (which had no authentication)
   - Used for stakeholder demos (Gradio app on HF Spaces is public)
   - Intended for development and exploration

3. **No security requirements**: CLAUDE.md and project documentation do not specify security requirements or sensitive data handling

4. **Better UX**: Removing unnecessary login friction improves the developer and demo experience

5. **Authentication framework preserved**: The API retains its authentication module (`apps/api/auth.py`, `apps/api/routers/auth.py`) for future use when/if authentication is needed

### When to Re-enable Authentication?

If the platform moves to production or handles sensitive data, authentication can be re-enabled by:

1. Setting `CREDIT_RISK_REQUIRE_AUTH=true` in API environment
2. Providing valid API keys via `CREDIT_RISK_API_KEYS="key1,key2"`
3. Re-implementing web authentication (middleware, login page) if needed
4. Using the existing `/auth/verify` endpoint

The API's auth infrastructure remains intact for this purpose.

## Consequences

### Positive

- **Simpler UX**: Users can access the web app immediately without authentication barriers
- **Consistency**: Web app behavior now matches API authentication posture
- **Less code**: Removed ~100 lines of auth-related code
- **Clearer intent**: Application is explicitly positioned as a development/demo tool

### Negative

- **No access control**: Anyone with network access can use the application
  - **Mitigation**: This is already the case with the open API; web auth was not providing security
- **Must rebuild auth for production**: If security is needed later, web authentication must be re-implemented
  - **Mitigation**: API auth framework is preserved; web auth can be quickly restored using git history

### Neutral

- **API authentication unchanged**: The backend's auth module remains available but unused (can be enabled via environment variables)
- **Gradio app unchanged**: The Gradio demo app did not use authentication; remains unaffected

## Alternatives Considered

### 1. Enable API Authentication

Set `require_auth = True` and provide API keys to secure the backend.

**Rejected because**:
- Adds complexity for development/demo use cases
- No clear security requirement or threat model
- Would still require distributing API keys to demo users

### 2. Make Web Auth Optional

Check API's auth status and conditionally show login page.

**Rejected because**:
- Added complexity without clear benefit
- Still requires maintaining auth infrastructure
- Authentication should be all-or-nothing, not configurable per-layer

### 3. Keep Web Auth, Remove API Auth

Rely on web-layer authentication only.

**Rejected because**:
- API endpoints remain directly accessible, bypassing web auth
- Creates false sense of security
- Web auth cannot protect API without backend enforcement

## Related Documents

- [apps/api/config.py](../../apps/api/config.py) - API authentication configuration
- [apps/api/auth.py](../../apps/api/auth.py) - API authentication module (preserved)
- [CLAUDE.md](../../CLAUDE.md) - Project guidelines (no security requirements specified)

## Implementation

Changes made in PR #[TBD]:

**Deleted files:**
- `apps/web/app/login/page.tsx` (87 lines) - Login form component
- `apps/web/middleware.ts` (22 lines) - Route authentication enforcement
- `apps/web/components/logout-button.tsx` (24 lines) - Logout button

**Modified files:**
- `apps/web/components/layout/header.tsx` - Removed `<LogoutButton />` from header
- `apps/web/lib/api-client.ts` - Removed:
  - `getApiKey()` function
  - API key cookie reading
  - Authorization header injection
  - 401 redirect to `/login`

**Preserved (for future use):**
- `apps/api/auth.py` - Authentication dependency
- `apps/api/routers/auth.py` - `/auth/verify` endpoint
- API configuration: `require_auth`, `api_keys` settings

**Testing:**
- Manual verification: Web app loads without login redirect
- API calls succeed without Authorization headers
- All pages (Train, Predict, Compare) accessible directly
