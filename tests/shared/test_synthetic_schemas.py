"""Tests for synthetic data generation schemas."""

import pytest
from pydantic import ValidationError

from shared.schemas.synthetic import (
    SyntheticConfig,
    SyntheticDataset,
    SyntheticDistribution,
    SyntheticGenerateResponse,
)


class TestSyntheticDistribution:
    """Tests for SyntheticDistribution schema."""

    def test_valid_with_all_fields(self) -> None:
        dist = SyntheticDistribution(
            feature="person_age",
            mean_shift=5.0,
            std_scale=2.0,
            category_weights=None,
        )
        assert dist.feature == "person_age"
        assert dist.mean_shift == 5.0
        assert dist.std_scale == 2.0
        assert dist.category_weights is None

    def test_valid_with_category_weights(self) -> None:
        dist = SyntheticDistribution(
            feature="loan_grade",
            category_weights={"A": 0.5, "B": 0.3, "C": 0.2},
        )
        assert dist.category_weights == {"A": 0.5, "B": 0.3, "C": 0.2}
        assert dist.mean_shift == 0.0
        assert dist.std_scale == 1.0

    def test_std_scale_zero_invalid(self) -> None:
        with pytest.raises(ValidationError):
            SyntheticDistribution(feature="person_age", std_scale=0.0)

    def test_std_scale_negative_invalid(self) -> None:
        with pytest.raises(ValidationError):
            SyntheticDistribution(feature="person_age", std_scale=-1.0)


class TestSyntheticConfig:
    """Tests for SyntheticConfig schema."""

    def test_valid_defaults(self) -> None:
        config = SyntheticConfig()
        assert config.n_samples == 5000
        assert config.default_rate == 0.22
        assert config.distributions == []
        assert config.random_seed == 42

    def test_n_samples_below_minimum(self) -> None:
        with pytest.raises(ValidationError):
            SyntheticConfig(n_samples=99)

    def test_n_samples_above_maximum(self) -> None:
        with pytest.raises(ValidationError):
            SyntheticConfig(n_samples=50001)

    def test_n_samples_at_bounds(self) -> None:
        config_min = SyntheticConfig(n_samples=100)
        assert config_min.n_samples == 100
        config_max = SyntheticConfig(n_samples=50000)
        assert config_max.n_samples == 50000

    def test_default_rate_below_minimum(self) -> None:
        with pytest.raises(ValidationError):
            SyntheticConfig(default_rate=0.001)

    def test_default_rate_above_maximum(self) -> None:
        with pytest.raises(ValidationError):
            SyntheticConfig(default_rate=0.999)

    def test_default_rate_at_bounds(self) -> None:
        config_low = SyntheticConfig(default_rate=0.01)
        assert config_low.default_rate == 0.01
        config_high = SyntheticConfig(default_rate=0.99)
        assert config_high.default_rate == 0.99

    def test_random_seed_none(self) -> None:
        config = SyntheticConfig(random_seed=None)
        assert config.random_seed is None

    def test_with_distributions(self) -> None:
        config = SyntheticConfig(
            distributions=[
                SyntheticDistribution(feature="person_age", mean_shift=5.0),
            ]
        )
        assert len(config.distributions) == 1
        assert config.distributions[0].feature == "person_age"


class TestSyntheticDataset:
    """Tests for SyntheticDataset schema."""

    def test_valid(self) -> None:
        dataset = SyntheticDataset(
            n_samples=1000,
            n_features=26,
            default_rate_actual=0.22,
            feature_names=["f1", "f2"],
            summary_stats={"f1": {"mean": 1.0, "std": 0.5, "min": 0.0, "max": 2.0}},
        )
        assert dataset.n_samples == 1000
        assert dataset.n_features == 26
        assert dataset.default_rate_actual == 0.22


class TestSyntheticGenerateResponse:
    """Tests for SyntheticGenerateResponse schema."""

    def test_valid(self) -> None:
        response = SyntheticGenerateResponse(
            dataset_id="syn_abc123",
            metadata=SyntheticDataset(
                n_samples=1000,
                n_features=26,
                default_rate_actual=0.22,
                feature_names=["f1"],
                summary_stats={"f1": {"mean": 1.0, "std": 0.5, "min": 0.0, "max": 2.0}},
            ),
        )
        assert response.dataset_id == "syn_abc123"
        assert response.metadata.n_samples == 1000
