"""Feature selection service for the API layer."""

from apps.api.services.training import load_dataset_from_csv
from shared.logic import feature_selection as fs_logic
from shared.schemas.feature_selection import (
    BorutaParams,
    FeatureSelectionMethod,
    FeatureSelectionRequest,
    FeatureSelectionResult,
    LassoParams,
    ShapParams,
    TreeImportanceParams,
    WoeIvParams,
)


def run_feature_selection(
    request: FeatureSelectionRequest, dataset_path: str
) -> FeatureSelectionResult:
    """Run automatic feature selection on the training dataset.

    Args:
        request: Feature selection request with method and parameters.
        dataset_path: Path to the training CSV dataset.

    Returns:
        FeatureSelectionResult with selected features and scores.

    Raises:
        FileNotFoundError: If dataset file doesn't exist.
        ValueError: If configuration is invalid.
    """
    # Always load all features for selection analysis
    X, y, feature_names = load_dataset_from_csv(dataset_path, selected_features=None)

    dispatchers = {
        FeatureSelectionMethod.TREE_IMPORTANCE: (
            fs_logic.select_features_tree_importance,
            request.tree_params or TreeImportanceParams(),
        ),
        FeatureSelectionMethod.LASSO: (
            fs_logic.select_features_lasso,
            request.lasso_params or LassoParams(),
        ),
        FeatureSelectionMethod.WOE_IV: (
            fs_logic.select_features_woe_iv,
            request.woe_iv_params or WoeIvParams(),
        ),
        FeatureSelectionMethod.BORUTA: (
            fs_logic.select_features_boruta,
            request.boruta_params or BorutaParams(),
        ),
        FeatureSelectionMethod.SHAP: (
            fs_logic.select_features_shap,
            request.shap_params or ShapParams(),
        ),
    }

    func, params = dispatchers[request.method]
    return func(X, y, feature_names, params, random_state=request.random_state)
