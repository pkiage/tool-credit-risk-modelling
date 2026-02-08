"""Automatic feature selection methods for credit risk modeling.

Pure functions using numpy/sklearn only (no pandas in the logic layer).
All methods share the same signature pattern and return FeatureSelectionResult.
"""

from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import NDArray
from scipy.stats import binom
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from shared import constants
from shared.schemas.feature_selection import (
    BorutaParams,
    FeatureScore,
    FeatureSelectionMethod,
    FeatureSelectionResult,
    LassoParams,
    ShapParams,
    TreeImportanceParams,
    WoeIvParams,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _rank_and_build_scores(
    feature_names: list[str],
    scores: NDArray[np.float64],
    selected_mask: NDArray[np.bool_],
    metadata_list: list[dict[str, str | float | int]] | None = None,
) -> list[FeatureScore]:
    """Build ranked FeatureScore objects from raw arrays.

    Args:
        feature_names: Ordered list of feature names.
        scores: Importance scores (higher = more important).
        selected_mask: Boolean mask indicating selected features.
        metadata_list: Optional per-feature metadata dicts.

    Returns:
        List of FeatureScore sorted by rank (1 = highest).
    """
    ranks = np.argsort(-scores).argsort() + 1

    feature_scores = []
    for i, name in enumerate(feature_names):
        feature_scores.append(
            FeatureScore(
                feature_name=name,
                score=float(scores[i]),
                selected=bool(selected_mask[i]),
                rank=int(ranks[i]),
                metadata=metadata_list[i] if metadata_list else None,
            )
        )

    feature_scores.sort(key=lambda fs: fs.rank)
    return feature_scores


# ---------------------------------------------------------------------------
# 1. Tree Importance
# ---------------------------------------------------------------------------


def select_features_tree_importance(
    X: NDArray[np.float64],
    y: NDArray[np.int_],
    feature_names: list[str],
    params: TreeImportanceParams,
    random_state: int = 42,
) -> FeatureSelectionResult:
    """Select features by training a tree model and ranking importances.

    Args:
        X: Feature matrix (n_samples, n_features).
        y: Binary target labels.
        feature_names: Encoded column names.
        params: Tree importance parameters (model_type, top_k or threshold).
        random_state: Random seed.

    Returns:
        FeatureSelectionResult with importance-ranked features.
    """
    if params.model_type == "random_forest":
        model = RandomForestClassifier(
            **{**constants.RANDOM_FOREST_PARAMS, "random_state": random_state},  # type: ignore[arg-type]
        )
    else:
        model = XGBClassifier(
            **{**constants.XGBOOST_PARAMS, "random_state": random_state},  # type: ignore[arg-type]
        )

    model.fit(X, y)
    importances = model.feature_importances_.astype(np.float64)

    # Determine selection
    if params.top_k is not None:
        top_indices = np.argsort(importances)[-params.top_k :]
        selected_mask = np.zeros(len(feature_names), dtype=bool)
        selected_mask[top_indices] = True
        meta: dict[str, str | float | int | bool] = {
            "selection_mode": "top_k",
            "k": params.top_k,
        }
    elif params.threshold is not None:
        selected_mask = importances >= params.threshold
        meta = {"selection_mode": "threshold", "threshold": params.threshold}
    else:
        selected_mask = importances > 0
        meta = {"selection_mode": "non_zero"}

    meta["model_type"] = params.model_type

    return FeatureSelectionResult(
        method=FeatureSelectionMethod.TREE_IMPORTANCE,
        selected_features=[n for n, s in zip(feature_names, selected_mask) if s],
        feature_scores=_rank_and_build_scores(
            feature_names, importances, selected_mask
        ),
        n_selected=int(selected_mask.sum()),
        n_total=len(feature_names),
        method_metadata=meta,
    )


# ---------------------------------------------------------------------------
# 2. LASSO (L1)
# ---------------------------------------------------------------------------


def select_features_lasso(
    X: NDArray[np.float64],
    y: NDArray[np.int_],
    feature_names: list[str],
    params: LassoParams,
    random_state: int = 42,
) -> FeatureSelectionResult:
    """Select features using L1-penalized Logistic Regression.

    Features with non-zero coefficients after L1 regularization are selected.

    Args:
        X: Feature matrix (n_samples, n_features).
        y: Binary target labels.
        feature_names: Encoded column names.
        params: LASSO parameters (C, max_iter).
        random_state: Random seed.

    Returns:
        FeatureSelectionResult with coefficient-based selection.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        model = LogisticRegression(
            penalty="l1",
            solver="saga",
            C=params.C,
            max_iter=params.max_iter,
            random_state=random_state,
        )
        model.fit(X, y)

    coefficients = np.abs(model.coef_[0])
    selected_mask = coefficients > 0

    n_iter = model.n_iter_
    n_iter_val = int(n_iter[0]) if hasattr(n_iter, "__iter__") else int(n_iter)

    return FeatureSelectionResult(
        method=FeatureSelectionMethod.LASSO,
        selected_features=[n for n, s in zip(feature_names, selected_mask) if s],
        feature_scores=_rank_and_build_scores(
            feature_names, coefficients, selected_mask
        ),
        n_selected=int(selected_mask.sum()),
        n_total=len(feature_names),
        method_metadata={
            "C": params.C,
            "converged": n_iter_val < params.max_iter,
            "n_iterations": n_iter_val,
        },
    )


# ---------------------------------------------------------------------------
# 3. WoE / IV
# ---------------------------------------------------------------------------


def _calculate_iv_for_feature(
    feature_values: NDArray[np.float64],
    target: NDArray[np.int_],
    n_bins: int = 10,
) -> float:
    """Calculate Information Value for a single feature.

    Args:
        feature_values: Values for one feature column.
        target: Binary target (0/1).
        n_bins: Number of equal-frequency bins for continuous features.

    Returns:
        Information Value score.
    """
    unique_vals = np.unique(feature_values)

    if len(unique_vals) <= 2:
        # Binary / one-hot feature: use raw values as bins
        bin_indices = feature_values.astype(int)
    else:
        # Continuous feature: quantile-based binning
        percentiles = np.linspace(0, 100, n_bins + 1)
        bin_edges = np.percentile(feature_values, percentiles)
        bin_edges = np.unique(bin_edges)  # collapse duplicate edges
        bin_indices = np.digitize(feature_values, bin_edges[1:-1])

    total_good = max((target == 0).sum(), 1)
    total_bad = max((target == 1).sum(), 1)

    iv = 0.0
    for bin_val in np.unique(bin_indices):
        mask = bin_indices == bin_val
        n_good = ((target == 0) & mask).sum()
        n_bad = ((target == 1) & mask).sum()

        if n_good == 0 or n_bad == 0:
            continue

        pct_good = n_good / total_good
        pct_bad = n_bad / total_bad

        woe = np.log(pct_good / pct_bad)
        iv += (pct_good - pct_bad) * woe

    return float(iv)


def _iv_category(iv: float) -> str:
    """Classify an IV value into an interpretive category.

    Args:
        iv: Information Value score.

    Returns:
        Category string: useless, weak, medium, strong, or suspicious.
    """
    if iv < constants.IV_THRESHOLD_USELESS:
        return "useless"
    if iv < constants.IV_THRESHOLD_WEAK:
        return "weak"
    if iv < constants.IV_THRESHOLD_MEDIUM:
        return "medium"
    if iv < constants.IV_THRESHOLD_STRONG:
        return "strong"
    return "suspicious"


def select_features_woe_iv(
    X: NDArray[np.float64],
    y: NDArray[np.int_],
    feature_names: list[str],
    params: WoeIvParams,
    random_state: int = 42,  # noqa: ARG001
) -> FeatureSelectionResult:
    """Select features using Information Value (IV).

    IV interpretation:
    - <0.02 useless, 0.02-0.1 weak, 0.1-0.3 medium, 0.3-0.5 strong, >0.5 suspicious.

    Args:
        X: Feature matrix (n_samples, n_features).
        y: Binary target labels.
        feature_names: Encoded column names.
        params: WoE/IV parameters (n_bins, iv_threshold).
        random_state: Unused, kept for signature consistency.

    Returns:
        FeatureSelectionResult with IV-based selection.
    """
    iv_scores = np.array(
        [
            _calculate_iv_for_feature(X[:, i], y, params.n_bins)
            for i in range(X.shape[1])
        ]
    )
    selected_mask = iv_scores >= params.iv_threshold

    metadata_list = [{"iv_category": _iv_category(iv)} for iv in iv_scores]

    return FeatureSelectionResult(
        method=FeatureSelectionMethod.WOE_IV,
        selected_features=[n for n, s in zip(feature_names, selected_mask) if s],
        feature_scores=_rank_and_build_scores(
            feature_names, iv_scores, selected_mask, metadata_list
        ),
        n_selected=int(selected_mask.sum()),
        n_total=len(feature_names),
        method_metadata={
            "iv_threshold": params.iv_threshold,
            "n_bins": params.n_bins,
            "mean_iv": float(iv_scores.mean()),
            "max_iv": float(iv_scores.max()),
        },
    )


# ---------------------------------------------------------------------------
# 4. Boruta (simplified custom implementation)
# ---------------------------------------------------------------------------


def select_features_boruta(
    X: NDArray[np.float64],
    y: NDArray[np.int_],
    feature_names: list[str],
    params: BorutaParams,
    random_state: int = 42,
) -> FeatureSelectionResult:
    """Select features using a simplified Boruta algorithm.

    Algorithm:
    1. Create shadow features (shuffled copies of each real feature).
    2. Train a Random Forest on real + shadow features.
    3. Count how often each real feature's importance exceeds the max shadow importance.
    4. After N iterations, apply a binomial test to classify features as
       Confirmed, Tentative, or Rejected.

    Args:
        X: Feature matrix (n_samples, n_features).
        y: Binary target labels.
        feature_names: Encoded column names.
        params: Boruta parameters (n_iterations, confidence_level, include_tentative).
        random_state: Random seed.

    Returns:
        FeatureSelectionResult with Boruta classification.
    """
    rng = np.random.RandomState(random_state)
    n_features = X.shape[1]
    hit_counts = np.zeros(n_features, dtype=int)

    for iteration in range(params.n_iterations):
        # Create shadow features by shuffling each column independently
        X_shadow = X.copy()
        for j in range(n_features):
            rng.shuffle(X_shadow[:, j])

        X_combined = np.hstack([X, X_shadow])

        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=random_state + iteration,
        )
        rf.fit(X_combined, y)

        importances = rf.feature_importances_
        real_importances = importances[:n_features]
        shadow_importances = importances[n_features:]
        max_shadow = shadow_importances.max()

        hit_counts += (real_importances > max_shadow).astype(int)

    # Binomial test: threshold for "confirmed"
    alpha = 1 - params.confidence_level
    threshold_hits = binom.ppf(1 - alpha, params.n_iterations, 0.5)

    confirmed = hit_counts >= threshold_hits
    rejected = hit_counts < params.n_iterations * 0.1
    tentative = ~confirmed & ~rejected

    if params.include_tentative:
        selected_mask = confirmed | tentative
    else:
        selected_mask = confirmed

    # Score = hit rate (fraction of iterations feature beat max shadow)
    scores = hit_counts.astype(np.float64) / params.n_iterations

    def _status(i: int) -> str:
        if confirmed[i]:
            return "confirmed"
        if tentative[i]:
            return "tentative"
        return "rejected"

    metadata_list: list[dict[str, str | float | int]] = [
        {"status": _status(i), "hit_rate": float(scores[i])} for i in range(n_features)
    ]

    return FeatureSelectionResult(
        method=FeatureSelectionMethod.BORUTA,
        selected_features=[n for n, s in zip(feature_names, selected_mask) if s],
        feature_scores=_rank_and_build_scores(
            feature_names, scores, selected_mask, metadata_list
        ),
        n_selected=int(selected_mask.sum()),
        n_total=len(feature_names),
        method_metadata={
            "n_iterations": params.n_iterations,
            "confidence_level": params.confidence_level,
            "include_tentative": params.include_tentative,
            "n_confirmed": int(confirmed.sum()),
            "n_tentative": int(tentative.sum()),
            "n_rejected": int(rejected.sum()),
        },
    )


# ---------------------------------------------------------------------------
# 5. SHAP
# ---------------------------------------------------------------------------


def select_features_shap(
    X: NDArray[np.float64],
    y: NDArray[np.int_],
    feature_names: list[str],
    params: ShapParams,
    random_state: int = 42,
) -> FeatureSelectionResult:
    """Select features using mean |SHAP| values.

    Trains a tree model, computes SHAP values via TreeExplainer, and ranks
    features by their mean absolute SHAP contribution.

    Args:
        X: Feature matrix (n_samples, n_features).
        y: Binary target labels.
        feature_names: Encoded column names.
        params: SHAP parameters (model_type, sample_size, top_k or threshold).
        random_state: Random seed.

    Returns:
        FeatureSelectionResult with SHAP-based selection.
    """
    import shap

    if params.model_type == "xgboost":
        model = XGBClassifier(
            **{**constants.XGBOOST_PARAMS, "random_state": random_state},  # type: ignore[arg-type]
        )
    else:
        model = RandomForestClassifier(
            **{**constants.RANDOM_FOREST_PARAMS, "random_state": random_state},  # type: ignore[arg-type]
        )

    model.fit(X, y)

    # Sample for efficiency
    if X.shape[0] > params.sample_size:
        idx = np.random.RandomState(random_state).choice(
            X.shape[0], size=params.sample_size, replace=False
        )
        X_sample = X[idx]
    else:
        X_sample = X

    explainer = shap.TreeExplainer(model)
    explanation = explainer(X_sample)

    # Extract raw numpy values from Explanation object
    shap_vals = np.array(explanation.values)

    # Binary classification may return 3D (n_samples, n_features, 2)
    if shap_vals.ndim == 3:
        shap_vals = shap_vals[:, :, 1]

    mean_abs_shap = np.abs(shap_vals).mean(axis=0).astype(np.float64)

    # Determine selection
    if params.top_k is not None:
        top_indices = np.argsort(mean_abs_shap)[-params.top_k :]
        selected_mask = np.zeros(len(feature_names), dtype=bool)
        selected_mask[top_indices] = True
        meta: dict[str, str | float | int | bool] = {
            "selection_mode": "top_k",
            "k": params.top_k,
        }
    elif params.threshold is not None:
        selected_mask = mean_abs_shap >= params.threshold
        meta = {"selection_mode": "threshold", "threshold": params.threshold}
    else:
        selected_mask = mean_abs_shap > 0
        meta = {"selection_mode": "non_zero"}

    meta["model_type"] = params.model_type
    meta["sample_size"] = min(X.shape[0], params.sample_size)

    return FeatureSelectionResult(
        method=FeatureSelectionMethod.SHAP,
        selected_features=[n for n, s in zip(feature_names, selected_mask) if s],
        feature_scores=_rank_and_build_scores(
            feature_names, mean_abs_shap, selected_mask
        ),
        n_selected=int(selected_mask.sum()),
        n_total=len(feature_names),
        method_metadata=meta,
    )
