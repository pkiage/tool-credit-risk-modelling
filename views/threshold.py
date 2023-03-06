from dataclasses import dataclass
from typing import Union, cast
import numpy as np
import streamlit as st
import plotly.express as px
import pandas as pd
from xgboost.sklearn import XGBClassifier
from sklearn.linear_model import LogisticRegression
from common.data import SplitDataset
from common.util import (
    model_probability_values_df,
    apply_threshold_to_probability_values,
    find_best_threshold_J_statistic,
    default_status_per_threshold,
    classification_report_per_threshold,
    thresh_classification_report_recall_accuracy,
)
from common.views import (
    streamlit_2columns_metrics_df,
    streamlit_2columns_metrics_pct_df,
)


@dataclass(frozen=True)
class Threshold:
    probability_threshold_selected: float
    predicted_default_status: pd.Series
    prediction_probability_df: pd.DataFrame


def make_threshold_view(
    model_name_short: str,
    model_name: str,
):
    def view(
        clf_gbt_model: Union[XGBClassifier, LogisticRegression],
        split_dataset: SplitDataset,
    ) -> Threshold:
        st.subheader("Classification Probability Threshold - User Defined")
        st.write(
            f"""
            The {model_name} model (obtained using training data) is applied on testing data to predict the loans probabilities of defaulting.\n
            Probabilities of defaulting of the loans are compared to a probability threshold.\n
            A loan is predicted to default if its predicted probability of defaulting is greater than the probability threshold.
            """
        )

        threshold_gbt_default = st.slider(
            label="Default Probability Threshold:",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            key=f"threshold_{model_name_short}_default",
        )

        clf_prediction_prob_df_gbt = model_probability_values_df(
            clf_gbt_model,
            split_dataset.X_test,
        )

        clf_thresh_predicted_default_status_user_gbt = (
            apply_threshold_to_probability_values(
                clf_prediction_prob_df_gbt,
                threshold_gbt_default,
            )
        )

        streamlit_2columns_metrics_df(
            "# of Predicted Defaults",
            "# of Predicted Non-Default",
            clf_thresh_predicted_default_status_user_gbt,
        )

        streamlit_2columns_metrics_pct_df(
            "% of Loans Predicted to Default",
            "% of Loans Predicted not to Default",
            clf_thresh_predicted_default_status_user_gbt,
        )

        st.subheader("J Statistic Driven Classification Probability Threshold")

        J_statistic_best_threshold = find_best_threshold_J_statistic(
            split_dataset.y_test, clf_prediction_prob_df_gbt
        )
        st.metric(
            label="Youden's J statistic calculated best threshold",
            value=J_statistic_best_threshold,
        )

        clf_thresh_predicted_default_status_Jstatistic_gbt = (
            apply_threshold_to_probability_values(
                clf_prediction_prob_df_gbt,
                J_statistic_best_threshold,
            )
        )

        streamlit_2columns_metrics_df(
            "# of Predicted Defaults",
            "# of Predicted Non-Default",
            clf_thresh_predicted_default_status_Jstatistic_gbt,
        )

        streamlit_2columns_metrics_pct_df(
            "% of Loans Predicted to Default",
            "% of Loans Predicted not to Default",
            clf_thresh_predicted_default_status_Jstatistic_gbt,
        )

        st.subheader(
            "Recall and Accuracy Tradeoff with given Probability Threshold"
        )
        # Steps
        # Get list of thresholds
        # Get default status per threshold
        # Get classification report per threshold
        # Get recall, nondef recall, and accuracy per threshold

        threshold_list = np.arange(0, 1, 0.025).round(decimals=3).tolist()

        threshold_default_status_list = default_status_per_threshold(
            threshold_list, clf_prediction_prob_df_gbt["PROB_DEFAULT"]
        )
        thresh_classification_report_dict = (
            classification_report_per_threshold(
                threshold_list,
                threshold_default_status_list,
                split_dataset.y_test,
            )
        )

        (
            thresh_def_recalls_list,
            thresh_nondef_recalls_list,
            thresh_accs_list,
        ) = thresh_classification_report_recall_accuracy(
            thresh_classification_report_dict
        )

        namelist = [
            "Default Recall",
            "Non Default Recall",
            "Accuracy",
            "Threshold",
        ]

        df = pd.DataFrame(
            [
                thresh_def_recalls_list,
                thresh_nondef_recalls_list,
                thresh_accs_list,
                threshold_list,
            ],
            index=namelist,
        )

        df = df.T

        fig2 = px.line(
            data_frame=df,
            y=["Default Recall", "Non Default Recall", "Accuracy"],
            x="Threshold",
        )

        fig2.update_layout(
            title="Recall and Accuracy score Trade-off with Probability Threshold",
            xaxis_title="Probability Threshold",
            yaxis_title="Score",
        )
        fig2.update_yaxes(range=[0.0, 1.0])

        st.plotly_chart(fig2)

        st.subheader("Acceptance Rate Driven Probability Threshold")
        # Steps
        # Set acceptance rate
        # Get default status per threshold
        # Get classification report per threshold
        # Get recall, nondef recall, and accuracy per threshold

        acceptance_rate = (
            st.slider(
                label="% of loans accepted (acceptance rate):",
                min_value=0,
                max_value=100,
                value=85,
                key=f"acceptance_rate_{model_name_short}",
                format="%f%%",
            )
            / 100
        )

        acc_rate_thresh_gbt = np.quantile(
            clf_prediction_prob_df_gbt["PROB_DEFAULT"], acceptance_rate
        )

        st.write(
            f"An acceptance rate of {acceptance_rate} results in probability threshold of {acc_rate_thresh_gbt}"
        )

        figa = px.histogram(clf_prediction_prob_df_gbt["PROB_DEFAULT"])

        figa.update_layout(
            title="Acceptance Rate Threshold vs. Loans Accepted",
            xaxis_title="Acceptance Rate Threshold",
            yaxis_title="Loans Accepted",
        )

        figa.update_traces(marker_line_width=1, marker_line_color="white")

        figa.add_vline(
            x=acc_rate_thresh_gbt,
            line_width=3,
            line_dash="solid",
            line_color="red",
        )

        st.plotly_chart(figa)

        clf_thresh_predicted_default_status_acceptance_gbt = (
            apply_threshold_to_probability_values(
                clf_prediction_prob_df_gbt,
                acc_rate_thresh_gbt,
            )
        )

        st.write()
        st.subheader("Selected Probability Threshold")

        options = [
            "User Defined",
            "J Statistic Driven",
            "Acceptance Rate Driven",
        ]
        prob_thresh_option = st.radio(
            label="Selected Probability Threshold",
            options=options,
            key=f"{model_name_short}_radio_thresh",
        )

        if prob_thresh_option == "User Defined":
            prob_thresh_selected_gbt = threshold_gbt_default
            predicted_default_status_gbt = (
                clf_thresh_predicted_default_status_user_gbt
            )
        elif prob_thresh_option == "J Statistic Driven":
            prob_thresh_selected_gbt = J_statistic_best_threshold
            predicted_default_status_gbt = (
                clf_thresh_predicted_default_status_Jstatistic_gbt
            )
        else:
            prob_thresh_selected_gbt = acc_rate_thresh_gbt
            predicted_default_status_gbt = (
                clf_thresh_predicted_default_status_acceptance_gbt
            )

        st.write(
            f"Selected probability threshold is {prob_thresh_selected_gbt}"
        )

        return Threshold(
            probability_threshold_selected=cast(
                float, prob_thresh_selected_gbt
            ),
            predicted_default_status=predicted_default_status_gbt,
            prediction_probability_df=clf_prediction_prob_df_gbt,
        )

    return view


decision_tree_threshold_view = make_threshold_view("gbt", "decision tree")
logistic_threshold_view = make_threshold_view("lg", "logistic")
