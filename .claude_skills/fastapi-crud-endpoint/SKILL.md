---
name: fastapi-crud-endpoint
description: Create new FastAPI CRUD endpoints following the project's proven router patterns (auth, rate limiting, error handling, Pydantic v2 schemas).
---

# FastAPI CRUD Endpoint Skill

Generate new API endpoints that match the conventions established across the 5 existing routers (`auth`, `predict`, `train`, `models`, `feature_selection`).

## When to Use

- Adding a new router to `apps/api/routers/`
- Adding endpoints to an existing router
- Creating a new service + router pair

## When NOT to Use

- Modifying shared Pydantic schemas only (no endpoint changes)
- Changing middleware or app-level configuration

## Endpoint Patterns

This project uses four endpoint shapes. Pick the one that fits, then follow the template in `references/router-template.py`.

### Pattern 1 — GET List

Return a collection. No auth required (read-only).

```python
@router.get("/", response_model=list[ItemSchema])
async def list_items() -> list[ItemSchema]:
```

### Pattern 2 — GET by ID

Return a single resource. Raise 404 if missing.

```python
@router.get("/{item_id}", response_model=ItemSchema)
async def get_item(item_id: str) -> ItemSchema:
```

### Pattern 3 — POST Create / Action

Accept a Pydantic request body, return a Pydantic response. Requires auth + optional rate limiting.

```python
@router.post("/", response_model=ResponseSchema)
@limiter.limit("100/minute")
async def create_item(
    request: Request,
    payload: RequestSchema,
    settings: Settings = Depends(get_settings),
    _api_key: str = Depends(verify_api_key),
) -> ResponseSchema:
```

### Pattern 4 — POST Sub-action on Resource

Perform an action on an existing resource (e.g., `/models/{id}/persist`).

```python
@router.post("/{item_id}/action", response_model=ResponseSchema)
async def perform_action(
    item_id: str,
    settings: Settings = Depends(get_settings),
    _api_key: str = Depends(verify_api_key),
) -> ResponseSchema:
```

## Creation Steps

1. **Define Pydantic schemas** in `shared/schemas/<domain>.py`
   - Request model (if POST) and Response model
   - Use `Field()` for validation and OpenAPI docs
   - Run `uv run pytest tests/shared/` after changes

2. **Create the service** in `apps/api/services/<domain>.py`
   - Pure business logic, no FastAPI imports
   - Accept typed inputs, return Pydantic models
   - Raise `ValueError` for bad input, `FileNotFoundError` for missing resources

3. **Create the router** in `apps/api/routers/<domain>.py`
   - Follow the template in `references/router-template.py`
   - Module docstring: `"""<Domain> endpoint router."""`
   - Single `router = APIRouter()` at module level

4. **Register the router** in `apps/api/main.py`
   ```python
   from apps.api.routers import new_domain
   app.include_router(
       new_domain.router,
       prefix="/new-domain",
       tags=["new-domain"],
   )
   ```

5. **Add tests** in `tests/api/test_<domain>.py`
   - Use `httpx.AsyncClient` with the app fixture
   - Test happy path, 400, 404, and 500 cases

## Conventions

### Dependency Order (in function signature)

1. Path parameters (`item_id: str`)
2. Request body (`payload: RequestSchema`)
3. `request: Request` (only if rate limiting is used)
4. `settings: Settings = Depends(get_settings)` (if needed)
5. `_api_key: str = Depends(verify_api_key)` (if write endpoint)

### Error Handling

Every POST endpoint uses this hierarchy:

```python
try:
    result = service_function(...)
    return result
except FileNotFoundError:
    logger.exception("Resource not found")
    raise HTTPException(status_code=404, detail="Resource not found")
except ValueError:
    logger.exception("Invalid input")
    raise HTTPException(status_code=400, detail="Invalid configuration")
except Exception:
    logger.exception("Operation failed unexpectedly")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Rate Limiting

- Heavy compute (training, feature selection): `"10/hour"` or `"20/hour"`
- Standard endpoints (predictions): `"100/minute"`
- Read-only endpoints: no rate limit

### Logging

- `logger = logging.getLogger(__name__)` at module level
- Use `logger.exception()` inside except blocks (auto-attaches traceback)

### Docstrings

Every endpoint needs:
- One-line summary
- `Args:` section
- `Returns:` section
- `Raises:` section listing HTTPException codes
- `Example Request:` / `Example Response:` JSON blocks (for POST endpoints)

## Checklist

- [ ] Pydantic schemas defined in `shared/schemas/`
- [ ] Service created in `apps/api/services/`
- [ ] Router created using template pattern
- [ ] Router registered in `apps/api/main.py` with prefix and tags
- [ ] Docstrings with Args/Returns/Raises/Examples
- [ ] Error handling follows the 404/400/500 hierarchy
- [ ] Auth dependency added for write endpoints
- [ ] Rate limiting added for compute-heavy endpoints
- [ ] Tests cover happy path + error cases
- [ ] `uv run pytest` passes
