from common.data import SplitDataset
import streamlit as st
import pandas as pd
import plotly.express as px
from views.threshold import logistic_threshold_view
from views.evaluation import logistic_evaluation_view
from common.util import (
    test_variables_logistic,
    print_coeff_logistic,
    model_probability_values_df,
    apply_threshold_to_probability_values,
)
from common.views import (
    streamlit_2columns_metrics_df,
    streamlit_2columns_metrics_pct_df,
)
from views.typing import ModelView


def logistic_view(split_dataset: SplitDataset, currency: str) -> ModelView:
    # ### Test and create variables logically

    st.header("Logistic Regression")

    clf_logistic_model = test_variables_logistic(
        split_dataset.X_train, split_dataset.y_train
    )

    st.metric(
        label="# of Coefficients in Logistic Regression",
        value=clf_logistic_model.n_features_in_,
        delta=None,
        delta_color="normal",
    )

    coef_dict = print_coeff_logistic(clf_logistic_model, split_dataset)

    st.subheader("Logistic Regression Coefficient Values")

    coef_dict_sorted = dict(
        sorted(coef_dict.items(), key=lambda item: item[1], reverse=False)
    )

    data_items = coef_dict_sorted.items()
    data_list = list(data_items)

    df = pd.DataFrame(data_list, columns=["Coefficient", "Value"])

    fig1 = px.bar(data_frame=df, x="Value", y="Coefficient", orientation="h")

    fig1.update_layout(
        title="Logistic Regression Coefficients",
        xaxis_title="Value",
        yaxis_title="Coefficient",
    )

    st.plotly_chart(fig1)

    st.subheader("Classification Probability Threshold")

    st.write(
        """
        The logistic regression model (obtained using training data) is applied on testing data to predict the loans probabilities of defaulting.\n
        Probabilities of defaulting of the loans are compared to a probability threshold.\n
        A loan is predicted to default if its predicted probability of defaulting is greater than the probability threshold.
        """
    )

    threshold = st.slider(
        label="Default Probability Threshold:",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        key="key_threshold",
    )

    clf_prediction_prob_df_log = model_probability_values_df(
        clf_logistic_model,
        split_dataset.X_test,
    )

    clf_thresh_predicted_default_status_user = (
        apply_threshold_to_probability_values(
            clf_prediction_prob_df_log,
            threshold,
        )
    )

    streamlit_2columns_metrics_df(
        "# of Predicted Defaults",
        "# of Predicted Non-Default",
        clf_thresh_predicted_default_status_user,
    )

    streamlit_2columns_metrics_pct_df(
        "% of Loans Predicted to Default",
        "% of Loans Predicted not to Default",
        clf_thresh_predicted_default_status_user,
    )

    threshold = logistic_threshold_view(clf_logistic_model, split_dataset)

    df_trueStatus_probabilityDefault_threshStatus_loanAmount = (
        logistic_evaluation_view(
            clf_logistic_model,
            split_dataset,
            currency,
            threshold.probability_threshold_selected,
            threshold.predicted_default_status,
        )
    )

    return ModelView(
        model=clf_logistic_model,
        trueStatus_probabilityDefault_threshStatus_loanAmount_df=df_trueStatus_probabilityDefault_threshStatus_loanAmount,
        probability_threshold_selected=threshold.probability_threshold_selected,
        predicted_default_status=threshold.predicted_default_status,
        prediction_probability_df=threshold.prediction_probability_df,
    )
