from typing import Union, cast
from sklearn.linear_model import LogisticRegression


import pandas as pd

from dataclasses import dataclass

from xgboost import XGBClassifier
from  features.util_build_features import SplitDataset

from  models.util_predict_model_threshold import (
    user_defined_probability_threshold,
    J_statistic_driven_probability_threshold,
    tradeoff_threshold,
    acceptance_rate_driven_threshold,
    select_probability_threshold,
    model_probability_values_df)

import streamlit as st


def probability_threshold_explainer(model_name):
    st.write(
        f"""
            The {model_name} model (obtained using training data) is applied on testing data to predict the loans probabilities of defaulting.\n
            Probabilities of defaulting of the loans are compared to a probability threshold.\n
            A loan is predicted to default if its predicted probability of defaulting is greater than the probability threshold.
            """
    )


@dataclass(frozen=True)
class Threshold:
    probability_threshold_selected: float
    predicted_default_status: pd.Series
    prediction_probability_df: pd.DataFrame


def make_prediction_view(
    model_name_short: str,
    model_name: str,
):
    def view(
        clf_xgbt_model: Union[XGBClassifier, LogisticRegression],
        split_dataset: SplitDataset,
    ) -> Threshold:

        probability_threshold_explainer(model_name)

        clf_prediction_prob_df_gbt = model_probability_values_df(
            clf_xgbt_model,
            split_dataset.X_test,
        )

        (clf_thresh_predicted_default_status_user_gbt,
         user_threshold
         ) = user_defined_probability_threshold(
            model_name_short, clf_xgbt_model, split_dataset)

        (clf_thresh_predicted_default_status_Jstatistic_gbt,
         J_statistic_best_threshold) = J_statistic_driven_probability_threshold(
            clf_prediction_prob_df_gbt, clf_xgbt_model, split_dataset)

        tradeoff_threshold(clf_prediction_prob_df_gbt, split_dataset)

        (acc_rate_thresh_gbt,
         clf_thresh_predicted_default_status_acceptance_gbt) = acceptance_rate_driven_threshold(model_name_short, clf_prediction_prob_df_gbt)

        (prob_thresh_selected_gbt,
         predicted_default_status_gbt) = select_probability_threshold(model_name_short,
                                                                      user_threshold,
                                                                      clf_thresh_predicted_default_status_user_gbt,
                                                                      J_statistic_best_threshold,
                                                                      clf_thresh_predicted_default_status_Jstatistic_gbt,
                                                                      acc_rate_thresh_gbt,
                                                                      clf_thresh_predicted_default_status_acceptance_gbt)

        return Threshold(
            probability_threshold_selected=cast(
                float, prob_thresh_selected_gbt
            ),
            predicted_default_status=predicted_default_status_gbt,
            prediction_probability_df=clf_prediction_prob_df_gbt,
        )

    return view
