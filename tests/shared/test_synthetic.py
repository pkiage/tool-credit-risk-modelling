"""Tests for synthetic data generator."""

import numpy as np
import pytest

from shared.constants import ALL_FEATURES, NUMERIC_FEATURE_DEFAULTS, NUMERIC_FEATURES
from shared.logic.synthetic import generate_synthetic_dataset
from shared.schemas.synthetic import SyntheticConfig, SyntheticDistribution


class TestGenerateSyntheticDataset:
    """Tests for the generate_synthetic_dataset function."""

    def test_output_shapes(self) -> None:
        config = SyntheticConfig(n_samples=1000, random_seed=42)
        X, y, feature_names, metadata = generate_synthetic_dataset(config)
        assert X.shape == (1000, 26)
        assert y.shape == (1000,)

    def test_feature_names_match_all_features(self) -> None:
        config = SyntheticConfig(n_samples=500, random_seed=42)
        _, _, feature_names, _ = generate_synthetic_dataset(config)
        assert feature_names == ALL_FEATURES

    def test_default_rate_approximately_correct(self) -> None:
        config = SyntheticConfig(n_samples=5000, default_rate=0.30, random_seed=42)
        _, y, _, metadata = generate_synthetic_dataset(config)
        actual_rate = float(np.mean(y))
        assert abs(actual_rate - 0.30) < 0.05

    def test_deterministic_with_same_seed(self) -> None:
        config = SyntheticConfig(n_samples=500, random_seed=123)
        X1, y1, _, _ = generate_synthetic_dataset(config)
        X2, y2, _, _ = generate_synthetic_dataset(config)
        np.testing.assert_array_equal(X1, X2)
        np.testing.assert_array_equal(y1, y2)

    def test_different_output_with_no_seed(self) -> None:
        config = SyntheticConfig(n_samples=500, random_seed=None)
        X1, _, _, _ = generate_synthetic_dataset(config)
        X2, _, _, _ = generate_synthetic_dataset(config)
        # Extremely unlikely to be identical with random seeds
        assert not np.array_equal(X1, X2)

    def test_numeric_features_within_bounds(self) -> None:
        config = SyntheticConfig(n_samples=2000, random_seed=42)
        X, _, feature_names, _ = generate_synthetic_dataset(config)
        for feat in NUMERIC_FEATURES:
            col_idx = feature_names.index(feat)
            col = X[:, col_idx]
            bounds = NUMERIC_FEATURE_DEFAULTS[feat]
            assert float(np.min(col)) >= bounds["min"], f"{feat} below min"
            assert float(np.max(col)) <= bounds["max"], f"{feat} above max"

    def test_categorical_valid_one_hot(self) -> None:
        """Each categorical group must have exactly one 1.0 per row, rest 0.0."""
        config = SyntheticConfig(n_samples=1000, random_seed=42)
        X, _, feature_names, _ = generate_synthetic_dataset(config)

        from shared.constants import CATEGORICAL_FEATURES, FEATURE_GROUPS

        for cat_feat in CATEGORICAL_FEATURES:
            encoded_cols = FEATURE_GROUPS[cat_feat]
            col_indices = [feature_names.index(c) for c in encoded_cols]
            group_data = X[:, col_indices]

            # Each row should sum to exactly 1.0
            row_sums = group_data.sum(axis=1)
            np.testing.assert_array_almost_equal(row_sums, 1.0)

            # Each value should be 0.0 or 1.0
            unique_vals = np.unique(group_data)
            assert set(unique_vals) == {0.0, 1.0}

    def test_mean_shift_changes_mean(self) -> None:
        base_config = SyntheticConfig(n_samples=5000, random_seed=42)
        shifted_config = SyntheticConfig(
            n_samples=5000,
            random_seed=42,
            distributions=[
                SyntheticDistribution(feature="person_age", mean_shift=10.0),
            ],
        )
        X_base, _, names, _ = generate_synthetic_dataset(base_config)
        X_shifted, _, _, _ = generate_synthetic_dataset(shifted_config)

        age_idx = names.index("person_age")
        base_mean = float(np.mean(X_base[:, age_idx]))
        shifted_mean = float(np.mean(X_shifted[:, age_idx]))
        # Shifted mean should be higher (allowing for clipping effects)
        assert shifted_mean > base_mean

    def test_std_scale_changes_variance(self) -> None:
        base_config = SyntheticConfig(n_samples=5000, random_seed=42)
        scaled_config = SyntheticConfig(
            n_samples=5000,
            random_seed=42,
            distributions=[
                SyntheticDistribution(feature="loan_int_rate", std_scale=2.0),
            ],
        )
        X_base, _, names, _ = generate_synthetic_dataset(base_config)
        X_scaled, _, _, _ = generate_synthetic_dataset(scaled_config)

        idx = names.index("loan_int_rate")
        base_var = float(np.var(X_base[:, idx]))
        scaled_var = float(np.var(X_scaled[:, idx]))
        # Variance should increase (roughly 4x, but clipping reduces it)
        assert scaled_var > base_var * 1.5

    def test_category_weights_override(self) -> None:
        config = SyntheticConfig(
            n_samples=5000,
            random_seed=42,
            distributions=[
                SyntheticDistribution(
                    feature="cb_person_default_on_file",
                    category_weights={"N": 0.1, "Y": 0.9},
                ),
            ],
        )
        X, _, names, _ = generate_synthetic_dataset(config)
        y_idx = names.index("cb_person_default_on_file_Y")
        proportion_y = float(np.mean(X[:, y_idx]))
        # Should be close to 0.9
        assert proportion_y > 0.85

    def test_edge_case_min_samples(self) -> None:
        config = SyntheticConfig(n_samples=100, random_seed=42)
        X, y, _, metadata = generate_synthetic_dataset(config)
        assert X.shape[0] == 100
        assert y.shape[0] == 100
        assert metadata.n_samples == 100

    def test_edge_case_low_default_rate(self) -> None:
        config = SyntheticConfig(n_samples=1000, default_rate=0.01, random_seed=42)
        _, y, _, _ = generate_synthetic_dataset(config)
        actual_rate = float(np.mean(y))
        assert actual_rate < 0.05

    def test_edge_case_high_default_rate(self) -> None:
        config = SyntheticConfig(n_samples=1000, default_rate=0.99, random_seed=42)
        _, y, _, _ = generate_synthetic_dataset(config)
        actual_rate = float(np.mean(y))
        assert actual_rate > 0.95

    def test_invalid_feature_name_raises_error(self) -> None:
        config = SyntheticConfig(
            distributions=[
                SyntheticDistribution(feature="nonexistent_feature"),
            ]
        )
        with pytest.raises(ValueError, match="Unknown feature"):
            generate_synthetic_dataset(config)

    def test_metadata_summary_stats_all_features(self) -> None:
        config = SyntheticConfig(n_samples=500, random_seed=42)
        _, _, _, metadata = generate_synthetic_dataset(config)
        assert len(metadata.summary_stats) == 26
        for feat_name in ALL_FEATURES:
            assert feat_name in metadata.summary_stats
            stats = metadata.summary_stats[feat_name]
            assert "mean" in stats
            assert "std" in stats
            assert "min" in stats
            assert "max" in stats

    def test_metadata_n_features(self) -> None:
        config = SyntheticConfig(n_samples=500, random_seed=42)
        _, _, _, metadata = generate_synthetic_dataset(config)
        assert metadata.n_features == 26

    def test_y_dtype_is_integer(self) -> None:
        config = SyntheticConfig(n_samples=500, random_seed=42)
        _, y, _, _ = generate_synthetic_dataset(config)
        assert np.issubdtype(y.dtype, np.integer)

    def test_y_values_binary(self) -> None:
        config = SyntheticConfig(n_samples=500, random_seed=42)
        _, y, _, _ = generate_synthetic_dataset(config)
        assert set(np.unique(y)) <= {0, 1}
