# ADR-011: Automatic Feature Selection Methods

| Field  | Value               |
|--------|---------------------|
| Status | Accepted            |
| Author | Paul / Claude       |
| Date   | 2026-02-07          |

## Context

ADR-010 delivered manual feature selection: users toggle checkboxes in the Gradio UI and the API trains on the chosen subset. While manual selection leverages domain expertise, users also need automated methods to:

1. Discover which features are most predictive before committing to a model
2. Reduce overfitting by dropping irrelevant columns
3. Compare filter, embedded, wrapper, and XAI approaches side-by-side
4. Get a recommended starting set that they can then refine manually

## Decision

Implement 5 automatic feature selection methods behind a new `POST /feature-selection/` API endpoint, with a Gradio UI accordion that feeds results into the existing manual checkboxes.

### Architecture

```text
Gradio Training Tab
  └─ Auto Feature Selection accordion
       ↓  HTTP POST
FastAPI  POST /feature-selection/
  └─ feature_selection_service.py  (dispatcher)
       ↓
shared/logic/feature_selection.py  (pure numpy/sklearn)
```

All methods return a standardized `FeatureSelectionResult` schema (see `shared/schemas/feature_selection.py`).

### Methods

| #   | Method          | Type             | Key Parameter          | New Deps |
|-----|-----------------|------------------|------------------------|----------|
| 1   | Tree Importance | Embedded filter  | `top_k` or `threshold` | None     |
| 2   | LASSO (L1)      | Embedded         | `C` (regularization)   | None     |
| 3   | WoE / IV        | Statistical filter | `iv_threshold`       | None     |
| 4   | Boruta          | Wrapper          | `include_tentative`    | None     |

> **SHAP (deferred)**: Removed due to [shap#4184](https://github.com/shap/shap/issues/4184) — XGBoost 3.x returns `base_score` as an array string that SHAP cannot parse. The fix ([PR #4187](https://github.com/shap/shap/pull/4187)) has not been released. Re-add when a compatible shap version ships.

#### 1. Tree Importance

Train a Random Forest or XGBoost model, rank features by `feature_importances_`, select the top K or those above a threshold.

#### 2. LASSO (L1 Regularization)

Train `LogisticRegression(penalty='l1', solver='saga', C=...)`. Features with non-zero coefficients survive. Lower `C` = stronger regularization = fewer features.

#### 3. WoE / IV (Weight of Evidence / Information Value)

Custom implementation. Bin continuous features via quantile-based equal-frequency binning, compute Weight of Evidence per bin, sum to Information Value per feature. IV categories:

- <0.02 useless
- 0.02-0.1 weak
- 0.1-0.3 medium
- 0.3-0.5 strong
- \>0.5 suspicious (overfitting risk)

#### 4. Boruta (simplified, custom)

Custom implementation to avoid adding the `BorutaPy` package. Algorithm:

1. Shuffle each feature column to create "shadow" features
2. Train Random Forest on real + shadow features
3. Record which real features beat the max shadow importance
4. Repeat N iterations
5. Apply `scipy.stats.binom.ppf` to classify each feature as Confirmed, Tentative, or Rejected

**Performance note**: Each iteration trains a RandomForest(100 trees, max_depth=10) on a doubled feature matrix (real + shadow columns). With the full 26-feature dataset (7500 rows × 52 columns), this is the most compute-heavy method. Mitigations:

- `n_jobs=-1` on the per-iteration RandomForest (parallel tree training)
- Gradio client uses a 300-second timeout for the feature-selection endpoint (vs 60s default)
- The API endpoint uses a synchronous `def` (not `async def`) so FastAPI runs it in a threadpool, avoiding event-loop blocking
- The Gradio UI shows a specific timeout message ("try fewer iterations") rather than a generic failure

### Standardized Output

```json
{
  "method": "tree_importance",
  "selected_features": ["loan_int_rate", "person_income", "..."],
  "feature_scores": [
    {"feature_name": "loan_int_rate", "score": 0.25, "selected": true, "rank": 1, "metadata": null}
  ],
  "n_selected": 10,
  "n_total": 26,
  "method_metadata": {"selection_mode": "top_k", "k": 10}
}
```

### Gradio UI Flow

1. Open "Auto Feature Selection" accordion in the Training tab
2. Pick a method and configure its parameters
3. Click "Run Feature Selection" → API returns scored feature list + chart
4. Click "Apply to Training" → updates the manual feature checkboxes below
5. Train the model using the pre-selected feature set

## Files Created / Modified

| File | Change |
|------|--------|
| `shared/constants.py` | IV threshold bands, Boruta/SHAP defaults |
| `shared/schemas/feature_selection.py` | Request, response, and per-method param schemas |
| `shared/logic/feature_selection.py` | 5 pure selection functions |
| `apps/api/services/feature_selection_service.py` | Service dispatcher |
| `apps/api/routers/feature_selection.py` | `POST /feature-selection/` endpoint |
| `apps/api/main.py` | Register new router |
| `apps/gradio/api_client.py` | `feature_selection()` method |
| `apps/gradio/components/training_tab.py` | Auto Feature Selection accordion + handlers |
| `pyproject.toml` | Add `shap>=0.46` |
| `apps/gradio/requirements.txt` | Add `shap>=0.46` |
| `tests/shared/test_feature_selection.py` | Logic layer tests |
| `tests/api/test_feature_selection.py` | Endpoint tests |

## Alternatives Considered

- **BorutaPy package** — avoided to prevent adding a dependency for a ~50-line algorithm
- **Mutual Information (sklearn)** — conceptually similar to WoE/IV but less interpretable in credit risk
- **RFE (Recursive Feature Elimination)** — very slow for marginal benefit over Tree Importance + Boruta
- **Embed selection into TrainingConfig** — feature selection is exploratory and separate from training; a dedicated endpoint keeps concerns separated

## Consequences

### Positive

- Users get 5 complementary methods spanning different selection philosophies
- One-click "Apply to Training" bridges auto-selection and manual control
- All logic in `shared/logic/` is reusable across Marimo notebooks and Next.js
- Custom Boruta avoids adding a package dependency

### Negative

- Adds `shap` dependency (~50 MB installed)
- Boruta with high iteration count is compute-heavy (rate limited to 20/hour, mitigated with `n_jobs=-1` and extended client timeout)
- WoE/IV binning may not be optimal for all feature distributions

### Future Enhancements

- Multi-method consensus (intersection of top features across methods)
- Coefficient path visualization for LASSO across varying C values
- Marimo notebook demonstrating each method interactively
- Next.js UI replication of the auto-selection workflow
