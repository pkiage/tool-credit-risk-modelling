from src.features.build_features import SplitDataset

from src.models.logistic_train_model import logistic_train_model
from src.models.logistic_predict_model import logistic_predict_model
from src.models.logistic_test_model import logistic_test_model

from src.models.util_model_class import ModelClass


def logistic_class(split_dataset: SplitDataset, currency: str) -> ModelClass:

    # Train Model
    clf_logistic_model = logistic_train_model(split_dataset)

    # Predict using Trained Model
    clf_logistic_predictions = logistic_predict_model(
        clf_logistic_model, split_dataset)

    # Test and Evaluate Model
    df_trueStatus_probabilityDefault_threshStatus_loanAmount_logistic = logistic_test_model(
        clf_logistic_model,
        split_dataset,
        currency,
        clf_logistic_predictions.probability_threshold_selected,
        clf_logistic_predictions.predicted_default_status)

    return ModelClass(
        model=clf_logistic_model,
        trueStatus_probabilityDefault_threshStatus_loanAmount_df=df_trueStatus_probabilityDefault_threshStatus_loanAmount_logistic,
        probability_threshold_selected=clf_logistic_predictions.probability_threshold_selected,
        predicted_default_status=clf_logistic_predictions.predicted_default_status,
        prediction_probability_df=clf_logistic_predictions.prediction_probability_df,
    )
