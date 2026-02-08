"""Feature selection request and response schemas."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class FeatureSelectionMethod(str, Enum):
    """Available automatic feature selection methods."""

    TREE_IMPORTANCE = "tree_importance"
    LASSO = "lasso"
    WOE_IV = "woe_iv"
    BORUTA = "boruta"


# --- Per-method parameter models ---


class TreeImportanceParams(BaseModel):
    """Parameters for tree-based importance feature selection.

    Attributes:
        model_type: Which tree model to use for importance calculation.
        top_k: Number of top features to select. None = use threshold instead.
        threshold: Importance threshold (0-1). Features above this are selected.
    """

    model_type: Literal["random_forest", "xgboost"] = Field(
        default="random_forest", description="Tree model type"
    )
    top_k: int | None = Field(
        default=None, ge=1, le=26, description="Select top K features"
    )
    threshold: float | None = Field(
        default=None, ge=0, le=1, description="Importance threshold"
    )


class LassoParams(BaseModel):
    """Parameters for LASSO (L1) feature selection.

    Attributes:
        C: Inverse regularization strength (lower = fewer features).
        max_iter: Maximum solver iterations.
    """

    C: float = Field(
        default=1.0, gt=0, le=10, description="Inverse regularization strength"
    )
    max_iter: int = Field(default=1000, ge=100, le=5000, description="Max iterations")


class WoeIvParams(BaseModel):
    """Parameters for Weight of Evidence / Information Value selection.

    Attributes:
        n_bins: Number of bins for continuous variable discretization.
        iv_threshold: Minimum IV score to select a feature.
    """

    n_bins: int = Field(
        default=10, ge=5, le=20, description="Number of bins for continuous features"
    )
    iv_threshold: float = Field(
        default=0.1, ge=0, le=1, description="Minimum IV threshold"
    )


class BorutaParams(BaseModel):
    """Parameters for Boruta all-relevant feature selection.

    Attributes:
        n_iterations: Number of Boruta iterations.
        confidence_level: Statistical confidence level for the binomial test.
        include_tentative: Whether to include tentative features in selection.
    """

    n_iterations: int = Field(
        default=100, ge=20, le=500, description="Number of iterations"
    )
    confidence_level: float = Field(
        default=0.95, ge=0.8, le=0.99, description="Confidence level"
    )
    include_tentative: bool = Field(
        default=False, description="Include tentative features"
    )


# --- Request ---


class FeatureSelectionRequest(BaseModel):
    """Request for automatic feature selection.

    Attributes:
        method: Feature selection method to use.
        random_state: Random seed for reproducibility.
        tree_params: Parameters when method is tree_importance.
        lasso_params: Parameters when method is lasso.
        woe_iv_params: Parameters when method is woe_iv.
        boruta_params: Parameters when method is boruta.
    """

    method: FeatureSelectionMethod = Field(description="Selection method")
    random_state: int = Field(default=42, description="Random seed")
    tree_params: TreeImportanceParams | None = Field(default=None)
    lasso_params: LassoParams | None = Field(default=None)
    woe_iv_params: WoeIvParams | None = Field(default=None)
    boruta_params: BorutaParams | None = Field(default=None)


# --- Response ---


class FeatureScore(BaseModel):
    """Score and selection status for a single feature.

    Attributes:
        feature_name: Encoded column name.
        score: Importance / relevance score (method-dependent).
        selected: Whether this feature is selected by the method.
        rank: Rank among all features (1 = highest score).
        metadata: Method-specific metadata (e.g., IV category, Boruta status).
    """

    feature_name: str = Field(description="Encoded column name")
    score: float = Field(description="Importance score")
    selected: bool = Field(description="Whether feature is selected")
    rank: int = Field(ge=1, description="Rank (1 = highest)")
    metadata: dict[str, str | float | int] | None = Field(
        default=None, description="Method-specific metadata"
    )


class FeatureSelectionResult(BaseModel):
    """Standardized result from any feature selection method.

    Attributes:
        method: Method that produced this result.
        selected_features: Encoded column names of selected features.
        feature_scores: Detailed scores for all evaluated features.
        n_selected: Number of features selected.
        n_total: Total number of features evaluated.
        method_metadata: Method-specific summary information.
    """

    method: FeatureSelectionMethod = Field(description="Method used")
    selected_features: list[str] = Field(description="Selected feature names")
    feature_scores: list[FeatureScore] = Field(description="All feature scores")
    n_selected: int = Field(ge=0, description="Number selected")
    n_total: int = Field(ge=1, description="Total features evaluated")
    method_metadata: dict[str, str | float | int | bool] | None = Field(
        default=None, description="Method-specific summary"
    )
