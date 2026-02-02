# RFC-006: Authentication & Production Polish

| Field | Value |
|-------|-------|
| Status | Accepted |
| Author(s) | pkiage |
| Updated | 2026-02-02 |
| Depends On | RFC-001, RFC-002, RFC-004, RFC-005 |

## Objective

Add authentication, production hardening, and polish across all layers to make the platform production-ready.

**Goals:**
- API key authentication for API access
- Session-based auth for web UI (optional)
- CORS restrictions for production
- Rate limiting
- Model persistence to filesystem/S3
- Audit trail completeness
- Error handling polish
- Documentation completion

**Non-goals:**
- OAuth/SSO (can be added later)
- Multi-tenancy
- Role-based access control (RBAC)
- Payment/billing integration

## Motivation

With all layers built (shared, API, notebooks, Gradio, Next.js), we need production hardening:
- Prevent unauthorized API access
- Protect against abuse (rate limiting)
- Persist models beyond session
- Complete audit trail for compliance
- Production-ready error handling

## User Benefit

**Release notes:** "Secure your credit risk API with authentication. Persist trained models. Production-ready deployment."

## Design Proposal

### Authentication Strategy

#### API Authentication (apps/api/)

**Approach:** API Key in header

```
Authorization: Bearer <api_key>
```

**Implementation:**

```python
# apps/api/auth.py
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    # Strip "Bearer " prefix
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]
    
    # Validate against stored keys
    if not is_valid_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key
```

**Key Storage Options:**

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| Environment variable | Simple | Single key only | Dev/demo |
| Config file | Multiple keys | Not secure for prod | Staging |
| Database | Scalable, revocable | More complex | Production |
| Secrets manager | Most secure | External dependency | Enterprise |

**Phase 6 approach:** Environment variable for simplicity, document upgrade path.

#### Web UI Authentication (apps/web/)

**Approach:** Simple session with API key stored in httpOnly cookie

```typescript
// Middleware to check auth
export function middleware(request: NextRequest) {
  const apiKey = request.cookies.get('api_key');
  
  if (!apiKey && !request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}
```

**Login flow:**
1. User enters API key on /login page
2. Key validated against API /health or /auth/verify
3. Key stored in httpOnly cookie
4. Subsequent requests include key in API calls

#### Gradio Authentication

**Approach:** Gradio built-in auth or API key input

```python
# Option 1: Gradio built-in (username/password)
app.launch(auth=("admin", os.getenv("GRADIO_PASSWORD")))

# Option 2: API key input field
api_key_input = gr.Textbox(label="API Key", type="password")
```

### CORS Configuration

```python
# apps/api/main.py
from fastapi.middleware.cors import CORSMiddleware

# Development
CORS_ORIGINS_DEV = ["*"]

# Production
CORS_ORIGINS_PROD = [
    "https://your-domain.com",
    "https://www.your-domain.com",
    "https://your-app.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting

```python
# apps/api/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to routes
@router.post("/train")
@limiter.limit("10/hour")  # Training is expensive
async def train(...):
    ...

@router.post("/predict")
@limiter.limit("100/minute")  # Predictions are cheap
async def predict(...):
    ...
```

### Model Persistence

#### Current State (In-Memory)

```python
_model_store: dict[str, Any] = {}  # Lost on restart
```

#### Target State (Filesystem + Optional S3)

```python
# apps/api/services/model_store.py
import joblib
from pathlib import Path

class ModelStore:
    def __init__(self, base_path: str = "artifacts/models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, model_id: str, model: Any, metadata: dict) -> str:
        model_path = self.base_path / f"{model_id}.joblib"
        meta_path = self.base_path / f"{model_id}.json"
        
        joblib.dump(model, model_path)
        meta_path.write_text(json.dumps(metadata))
        
        return str(model_path)
    
    def load(self, model_id: str) -> tuple[Any, dict]:
        model_path = self.base_path / f"{model_id}.joblib"
        meta_path = self.base_path / f"{model_id}.json"
        
        model = joblib.load(model_path)
        metadata = json.loads(meta_path.read_text())
        
        return model, metadata
    
    def list(self) -> list[str]:
        return [p.stem for p in self.base_path.glob("*.joblib")]
```

#### S3 Extension (Optional)

```python
# apps/api/services/model_store_s3.py
import boto3

class S3ModelStore(ModelStore):
    def __init__(self, bucket: str, prefix: str = "models/"):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
        self.prefix = prefix
    
    def save(self, model_id: str, model: Any, metadata: dict) -> str:
        # Save locally first, then upload
        local_path = super().save(model_id, model, metadata)
        
        s3_key = f"{self.prefix}{model_id}.joblib"
        self.s3.upload_file(local_path, self.bucket, s3_key)
        
        return f"s3://{self.bucket}/{s3_key}"
```

### Audit Trail Completeness

#### Events to Log

| Event | Trigger | Required Fields |
|-------|---------|-----------------|
| `auth_success` | Valid API key used | api_key_hash, ip |
| `auth_failure` | Invalid API key | ip, attempted_key_prefix |
| `training_started` | POST /train | config, dataset_hash, user |
| `training_completed` | Training finishes | model_id, metrics, duration |
| `training_failed` | Training error | error, config |
| `prediction_made` | POST /predict | model_id, n_samples, user |
| `model_persisted` | Model saved | model_id, path |
| `model_loaded` | Model loaded | model_id |

#### Structured Logging

```python
# apps/api/services/audit.py
import structlog

logger = structlog.get_logger()

def log_event(event_type: str, **kwargs):
    logger.info(
        event_type,
        timestamp=datetime.utcnow().isoformat(),
        **kwargs
    )

# Usage
log_event("training_completed", model_id="abc123", roc_auc=0.85, duration_seconds=12.5)
```

### Error Handling Polish

#### API Error Responses

```python
# apps/api/exceptions.py
from fastapi import HTTPException

class CreditRiskException(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

class ModelNotFoundError(CreditRiskException):
    def __init__(self, model_id: str):
        super().__init__(f"Model not found: {model_id}", "MODEL_NOT_FOUND")

class TrainingError(CreditRiskException):
    def __init__(self, reason: str):
        super().__init__(f"Training failed: {reason}", "TRAINING_FAILED")

class ValidationError(CreditRiskException):
    def __init__(self, field: str, reason: str):
        super().__init__(f"Validation error on {field}: {reason}", "VALIDATION_ERROR")
```

#### Global Exception Handler

```python
# apps/api/main.py
@app.exception_handler(CreditRiskException)
async def credit_risk_exception_handler(request: Request, exc: CreditRiskException):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Documentation Completion

#### API Documentation

- OpenAPI spec auto-generated (already done)
- Add descriptions to all endpoints
- Add example requests/responses
- Add error response documentation

#### README Updates

- Installation instructions
- Configuration guide
- Deployment guide (Vercel, HF Spaces, Docker)
- API usage examples
- Contributing guidelines

#### ADRs to Write

| ADR | Topic |
|-----|-------|
| ADR-002 | Choosing Pydantic as contract layer |
| ADR-003 | Choosing Marimo over Jupyter |
| ADR-004 | API key authentication approach |
| ADR-005 | Model persistence strategy |

### Configuration Management

```python
# apps/api/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_name: str = "Credit Risk API"
    debug: bool = False
    
    # Auth
    api_keys: list[str] = []  # Comma-separated in env
    require_auth: bool = True
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    train_rate_limit: str = "10/hour"
    predict_rate_limit: str = "100/minute"
    
    # Storage
    model_storage_type: str = "filesystem"  # or "s3"
    model_storage_path: str = "artifacts/models"
    s3_bucket: str | None = None
    
    # Logging
    log_level: str = "INFO"
    audit_log_path: str = "logs/audit.jsonl"
    
    class Config:
        env_prefix = "CREDIT_RISK_"
        env_file = ".env"
```

### Security Checklist

- [ ] API keys not logged in plain text
- [ ] CORS restricted in production
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] No secrets in code or git
- [ ] HTTPS enforced in production
- [ ] Error messages don't leak internals
- [ ] Audit trail for compliance

## Alternatives Considered

### Alternative 1: OAuth2 / JWT

**Pros:** Industry standard, refresh tokens

**Cons:** Complex for demo app, requires token management

**Why not chosen:** API keys simpler; OAuth can be added later

### Alternative 2: No Auth (Public API)

**Pros:** Simplest

**Cons:** Abuse risk, no audit trail per user

**Why not chosen:** Need basic protection and user tracking

### Alternative 3: Supabase/Auth0

**Pros:** Managed auth, many features

**Cons:** External dependency, cost

**Why not chosen:** Overkill for current scope; document as upgrade path

## Dependencies

**New dependencies:**
- `slowapi` — Rate limiting
- `structlog` — Structured logging
- `python-jose` — JWT (if needed later)
- `boto3` — S3 (optional)

## Engineering Impact

**Maintenance:** Security-sensitive; needs regular review

**Testing:**
- Auth middleware tests
- Rate limiting tests
- Model persistence tests
- Audit log verification

**Build impact:**
- Environment variables for secrets
- Log rotation setup
- S3 bucket provisioning (if used)

## Platforms and Environments

| Environment | Auth | CORS | Rate Limit | Storage |
|-------------|------|------|------------|---------|
| Local dev | Optional | `*` | Disabled | Filesystem |
| Staging | Required | Staging URLs | Enabled | Filesystem |
| Production | Required | Prod URLs | Enabled | S3 |

## Questions and Discussion Topics

1. **API key generation** — Manual or self-service via UI?
2. **Key rotation** — Support multiple active keys?
3. **Rate limit storage** — In-memory or Redis?
4. **Log retention** — How long to keep audit logs?
5. **S3 vs filesystem** — Which for initial production?

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-01-31 | — | Initial draft |
