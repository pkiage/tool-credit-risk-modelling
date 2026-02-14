"""Synthetic credit risk data generator.

Generates datasets in the same format as ``load_dataset_from_csv()`` using
multivariate normal sampling for numeric features (preserving real-dataset
correlations) and multinomial sampling for categorical features.
"""

import numpy as np
from numpy.typing import NDArray

from shared.constants import (
    ALL_FEATURES,
    CATEGORICAL_FEATURE_DEFAULTS,
    CATEGORICAL_FEATURES,
    FEATURE_GROUPS,
    NUMERIC_CORRELATION_MATRIX,
    NUMERIC_FEATURE_DEFAULTS,
    NUMERIC_FEATURES,
)
from shared.schemas.synthetic import SyntheticConfig, SyntheticDataset


def generate_synthetic_dataset(
    config: SyntheticConfig,
) -> tuple[NDArray[np.float64], NDArray[np.int_], list[str], SyntheticDataset]:
    """Generate a synthetic credit risk dataset.

    Uses multivariate normal sampling for numeric features (preserving
    correlations from the real dataset) and multinomial sampling for
    categorical features.

    Args:
        config: Generation configuration.

    Returns:
        Tuple of (X, y, feature_names, metadata).

    Raises:
        ValueError: If a distribution override references an unknown feature.
    """
    _validate_overrides(config)

    rng = np.random.default_rng(config.random_seed)

    # --- Target labels ---
    n_defaults = round(config.n_samples * config.default_rate)
    y = np.zeros(config.n_samples, dtype=np.int_)
    y[:n_defaults] = 1
    rng.shuffle(y)

    # --- Build override lookup ---
    overrides = {d.feature: d for d in config.distributions}

    # --- Numeric features (correlated multivariate normal) ---
    means = np.array(
        [NUMERIC_FEATURE_DEFAULTS[f]["mean"] for f in NUMERIC_FEATURES],
        dtype=np.float64,
    )
    stds = np.array(
        [NUMERIC_FEATURE_DEFAULTS[f]["std"] for f in NUMERIC_FEATURES],
        dtype=np.float64,
    )

    # Apply overrides to means and stds
    for i, feat in enumerate(NUMERIC_FEATURES):
        if feat in overrides:
            means[i] += overrides[feat].mean_shift
            stds[i] *= overrides[feat].std_scale

    # Build covariance matrix: cov[i,j] = corr[i,j] * std_i * std_j
    corr = np.array(NUMERIC_CORRELATION_MATRIX, dtype=np.float64)
    cov = corr * np.outer(stds, stds)

    # Sample and clip to valid bounds
    numeric_data = rng.multivariate_normal(means, cov, config.n_samples)
    for i, feat in enumerate(NUMERIC_FEATURES):
        bounds = NUMERIC_FEATURE_DEFAULTS[feat]
        numeric_data[:, i] = np.clip(numeric_data[:, i], bounds["min"], bounds["max"])

    # --- Categorical features (one-hot encoded via multinomial sampling) ---
    categorical_columns: dict[str, NDArray[np.float64]] = {}

    for cat_feat in CATEGORICAL_FEATURES:
        encoded_cols = FEATURE_GROUPS[cat_feat]
        defaults = CATEGORICAL_FEATURE_DEFAULTS[cat_feat]

        # Category names are the suffix after the last underscore grouping
        # e.g. "person_home_ownership_RENT" -> "RENT"
        prefix = cat_feat + "_"
        categories = [col[len(prefix) :] for col in encoded_cols]

        # Get weights (apply override if present)
        override = overrides.get(cat_feat)
        if override is not None and override.category_weights is not None:
            ow = override.category_weights
            weights = np.array(
                [ow.get(c, defaults.get(c, 0.0)) for c in categories],
                dtype=np.float64,
            )
        else:
            weights = np.array([defaults[c] for c in categories], dtype=np.float64)

        # Normalize weights to sum to 1.0
        weights = weights / weights.sum()

        # Sample categories
        chosen = rng.choice(len(categories), size=config.n_samples, p=weights)

        # One-hot encode
        one_hot = np.zeros((config.n_samples, len(categories)), dtype=np.float64)
        one_hot[np.arange(config.n_samples), chosen] = 1.0

        for j, col_name in enumerate(encoded_cols):
            categorical_columns[col_name] = one_hot[:, j]

    # --- Assemble into (n_samples, 26) matrix in ALL_FEATURES order ---
    X = np.empty((config.n_samples, len(ALL_FEATURES)), dtype=np.float64)  # noqa: N806
    for col_idx, feat_name in enumerate(ALL_FEATURES):
        if feat_name in NUMERIC_FEATURES:
            num_idx = NUMERIC_FEATURES.index(feat_name)
            X[:, col_idx] = numeric_data[:, num_idx]
        else:
            X[:, col_idx] = categorical_columns[feat_name]

    # --- Compute metadata ---
    summary_stats: dict[str, dict[str, float]] = {}
    for col_idx, feat_name in enumerate(ALL_FEATURES):
        col = X[:, col_idx]
        summary_stats[feat_name] = {
            "mean": float(np.mean(col)),
            "std": float(np.std(col)),
            "min": float(np.min(col)),
            "max": float(np.max(col)),
        }

    actual_default_rate = float(np.mean(y))
    metadata = SyntheticDataset(
        n_samples=config.n_samples,
        n_features=len(ALL_FEATURES),
        default_rate_actual=round(actual_default_rate, 4),
        feature_names=list(ALL_FEATURES),
        summary_stats=summary_stats,
    )

    return X, y, list(ALL_FEATURES), metadata


def _validate_overrides(config: SyntheticConfig) -> None:
    """Validate that all distribution override feature names are known.

    Args:
        config: Generation configuration to validate.

    Raises:
        ValueError: If an override references an unknown feature name.
    """
    valid_names = set(NUMERIC_FEATURES) | set(CATEGORICAL_FEATURES)
    for dist in config.distributions:
        if dist.feature not in valid_names:
            raise ValueError(
                f"Unknown feature in distribution override: '{dist.feature}'. "
                f"Valid features: {sorted(valid_names)}"
            )
