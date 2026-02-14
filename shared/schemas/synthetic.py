"""Synthetic data generation schemas."""

from pydantic import BaseModel, Field


class SyntheticDistribution(BaseModel):
    """Per-feature distribution override for synthetic data generation.

    Attributes:
        feature: Feature name (must be in NUMERIC_FEATURES or CATEGORICAL_FEATURES).
        mean_shift: Additive shift to feature mean (numeric only).
        std_scale: Std deviation scale factor (numeric only).
        category_weights: Override category probability weights (categorical only).
    """

    feature: str = Field(
        description="Feature name (must be in NUMERIC_FEATURES or CATEGORICAL_FEATURES)"
    )
    mean_shift: float = Field(
        default=0.0, description="Additive shift to feature mean (numeric only)"
    )
    std_scale: float = Field(
        default=1.0, gt=0.0, description="Std deviation scale factor (numeric only)"
    )
    category_weights: dict[str, float] | None = Field(
        default=None,
        description="Override category probability weights (categorical only)",
    )


class SyntheticConfig(BaseModel):
    """Configuration for synthetic dataset generation.

    Attributes:
        n_samples: Number of samples to generate.
        default_rate: Target default rate for the generated dataset.
        distributions: Per-feature distribution overrides.
        random_seed: Random seed for reproducibility (None for random).
    """

    n_samples: int = Field(
        default=5000, ge=100, le=50000, description="Number of samples"
    )
    default_rate: float = Field(
        default=0.22, ge=0.01, le=0.99, description="Target default rate"
    )
    distributions: list[SyntheticDistribution] = Field(
        default_factory=list, description="Per-feature distribution overrides"
    )
    random_seed: int | None = Field(
        default=42, description="Random seed (None for random)"
    )


class SyntheticDataset(BaseModel):
    """Metadata for a generated synthetic dataset.

    Attributes:
        n_samples: Number of samples in the dataset.
        n_features: Number of features in the dataset.
        default_rate_actual: Actual default rate in the generated dataset.
        feature_names: Ordered list of feature column names.
        summary_stats: Per-feature summary statistics (mean, std, min, max).
    """

    n_samples: int = Field(ge=1)
    n_features: int = Field(ge=1)
    default_rate_actual: float = Field(ge=0.0, le=1.0)
    feature_names: list[str]
    summary_stats: dict[str, dict[str, float]] = Field(
        description="feature_name -> {mean, std, min, max}"
    )


class SyntheticGenerateResponse(BaseModel):
    """API response from synthetic data generation.

    Attributes:
        dataset_id: Unique identifier for the generated dataset.
        metadata: Metadata about the generated dataset.
    """

    dataset_id: str = Field(description="Unique identifier for the generated dataset")
    metadata: SyntheticDataset
