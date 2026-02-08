"""Tests for automatic feature selection methods."""

import numpy as np
import pytest

from shared.schemas.feature_selection import (
    BorutaParams,
    FeatureSelectionMethod,
    LassoParams,
    ShapParams,
    TreeImportanceParams,
    WoeIvParams,
)


@pytest.fixture
def classification_data() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Synthetic binary classification dataset with 5 informative + 5 noise features."""
    rng = np.random.RandomState(42)
    n = 500
    n_features = 10
    X = rng.randn(n, n_features)
    # Target depends on first 3 features only
    y = (X[:, 0] + 2 * X[:, 1] - X[:, 2] > 0).astype(np.int_)
    names = [f"feat_{i}" for i in range(n_features)]
    return X, y, names


# -------------------------------------------------------------------
# Tree Importance
# -------------------------------------------------------------------


class TestTreeImportance:
    """Tests for select_features_tree_importance."""

    def test_top_k(self, classification_data: tuple) -> None:
        """Top-K selection returns exactly K features."""
        from shared.logic.feature_selection import select_features_tree_importance

        X, y, names = classification_data
        params = TreeImportanceParams(model_type="random_forest", top_k=5)
        result = select_features_tree_importance(X, y, names, params)

        assert result.method == FeatureSelectionMethod.TREE_IMPORTANCE
        assert result.n_selected == 5
        assert result.n_total == 10
        assert len(result.selected_features) == 5
        assert len(result.feature_scores) == 10
        # Scores are ranked 1..10
        assert result.feature_scores[0].rank == 1

    def test_threshold(self, classification_data: tuple) -> None:
        """Threshold selection returns features above the threshold."""
        from shared.logic.feature_selection import select_features_tree_importance

        X, y, names = classification_data
        params = TreeImportanceParams(model_type="xgboost", threshold=0.05)
        result = select_features_tree_importance(X, y, names, params)

        assert result.n_selected >= 1
        for fs in result.feature_scores:
            if fs.selected:
                assert fs.score >= 0.05


# -------------------------------------------------------------------
# LASSO
# -------------------------------------------------------------------


class TestLasso:
    """Tests for select_features_lasso."""

    def test_basic(self, classification_data: tuple) -> None:
        """LASSO selects features with non-zero coefficients."""
        from shared.logic.feature_selection import select_features_lasso

        X, y, names = classification_data
        params = LassoParams(C=1.0)
        result = select_features_lasso(X, y, names, params)

        assert result.method == FeatureSelectionMethod.LASSO
        assert result.n_total == 10
        assert result.n_selected > 0
        assert "converged" in result.method_metadata

    def test_strong_regularization(self, classification_data: tuple) -> None:
        """Strong regularization (low C) selects fewer features."""
        from shared.logic.feature_selection import select_features_lasso

        X, y, names = classification_data
        weak = select_features_lasso(X, y, names, LassoParams(C=10.0))
        strong = select_features_lasso(X, y, names, LassoParams(C=0.01))
        assert strong.n_selected <= weak.n_selected


# -------------------------------------------------------------------
# WoE/IV
# -------------------------------------------------------------------


class TestWoeIv:
    """Tests for select_features_woe_iv."""

    def test_basic(self, classification_data: tuple) -> None:
        """WoE/IV returns IV scores and categories."""
        from shared.logic.feature_selection import select_features_woe_iv

        X, y, names = classification_data
        params = WoeIvParams(n_bins=10, iv_threshold=0.05)
        result = select_features_woe_iv(X, y, names, params)

        assert result.method == FeatureSelectionMethod.WOE_IV
        assert result.n_total == 10
        # Check metadata has iv_category
        for fs in result.feature_scores:
            assert fs.metadata is not None
            assert fs.metadata["iv_category"] in {
                "useless",
                "weak",
                "medium",
                "strong",
                "suspicious",
            }

    def test_high_threshold_selects_fewer(self, classification_data: tuple) -> None:
        """Higher IV threshold selects fewer features."""
        from shared.logic.feature_selection import select_features_woe_iv

        X, y, names = classification_data
        low = select_features_woe_iv(X, y, names, WoeIvParams(iv_threshold=0.02))
        high = select_features_woe_iv(X, y, names, WoeIvParams(iv_threshold=0.3))
        assert high.n_selected <= low.n_selected


# -------------------------------------------------------------------
# Boruta
# -------------------------------------------------------------------


class TestBoruta:
    """Tests for select_features_boruta."""

    def test_basic(self, classification_data: tuple) -> None:
        """Boruta classifies features as confirmed/tentative/rejected."""
        from shared.logic.feature_selection import select_features_boruta

        X, y, names = classification_data
        # Use low iterations for speed in tests
        params = BorutaParams(n_iterations=20, confidence_level=0.95)
        result = select_features_boruta(X, y, names, params)

        assert result.method == FeatureSelectionMethod.BORUTA
        assert result.n_total == 10
        for fs in result.feature_scores:
            assert fs.metadata is not None
            assert fs.metadata["status"] in {"confirmed", "tentative", "rejected"}
        meta = result.method_metadata
        assert meta["n_confirmed"] + meta["n_tentative"] + meta["n_rejected"] == 10

    def test_include_tentative(self, classification_data: tuple) -> None:
        """Including tentative features selects at least as many."""
        from shared.logic.feature_selection import select_features_boruta

        X, y, names = classification_data
        strict = select_features_boruta(
            X, y, names, BorutaParams(n_iterations=20, include_tentative=False)
        )
        relaxed = select_features_boruta(
            X, y, names, BorutaParams(n_iterations=20, include_tentative=True)
        )
        assert relaxed.n_selected >= strict.n_selected


# -------------------------------------------------------------------
# SHAP
# -------------------------------------------------------------------


class TestShap:
    """Tests for select_features_shap."""

    def test_top_k(self, classification_data: tuple) -> None:
        """SHAP top-K returns exactly K features."""
        from shared.logic.feature_selection import select_features_shap

        X, y, names = classification_data
        params = ShapParams(model_type="xgboost", sample_size=50, top_k=5)
        result = select_features_shap(X, y, names, params)

        assert result.method == FeatureSelectionMethod.SHAP
        assert result.n_selected == 5
        assert result.n_total == 10
        assert len(result.selected_features) == 5


# -------------------------------------------------------------------
# Schema validation
# -------------------------------------------------------------------


class TestSchemas:
    """Tests for feature selection Pydantic schemas."""

    def test_result_roundtrip(self) -> None:
        """FeatureSelectionResult serializes and deserializes correctly."""
        from shared.schemas.feature_selection import (
            FeatureScore,
            FeatureSelectionResult,
        )

        result = FeatureSelectionResult(
            method=FeatureSelectionMethod.LASSO,
            selected_features=["a", "b"],
            feature_scores=[
                FeatureScore(feature_name="a", score=1.0, selected=True, rank=1),
                FeatureScore(feature_name="b", score=0.5, selected=True, rank=2),
                FeatureScore(feature_name="c", score=0.0, selected=False, rank=3),
            ],
            n_selected=2,
            n_total=3,
        )
        data = result.model_dump()
        restored = FeatureSelectionResult.model_validate(data)
        assert restored.n_selected == 2
        assert restored.feature_scores[0].feature_name == "a"
