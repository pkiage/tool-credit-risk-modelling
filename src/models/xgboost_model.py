from src.features.build_features import SplitDataset

from src.models.xgboost_train_model import xgboost_train_model
from src.models.xgboost_predict_model import xgboost_predit_model
from src.models.xgboost_test_model import xgboost_test_model

from src.models.util_model_class import ModelClass


def xgboost_class(split_dataset: SplitDataset, currency: str):

    # Train Model
    clf_xgbt_model = xgboost_train_model(split_dataset)

    # Predit using Trained Model
    clf_xgbt_predictions = xgboost_predit_model(
        clf_xgbt_model, split_dataset)

    # Test and Evaluate Model
    df_trueStatus_probabilityDefault_threshStatus_loanAmount_xgbt = xgboost_test_model(
        clf_xgbt_model,
        split_dataset,
        currency,
        clf_xgbt_predictions.probability_threshold_selected,
        clf_xgbt_predictions.predicted_default_status)

    return ModelClass(
        model=clf_xgbt_model,
        trueStatus_probabilityDefault_threshStatus_loanAmount_df=df_trueStatus_probabilityDefault_threshStatus_loanAmount_xgbt,
        probability_threshold_selected=clf_xgbt_predictions.probability_threshold_selected,
        predicted_default_status=clf_xgbt_predictions.predicted_default_status,
        prediction_probability_df=clf_xgbt_predictions.prediction_probability_df,
    )
