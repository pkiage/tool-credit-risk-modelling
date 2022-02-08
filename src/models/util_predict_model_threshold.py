import streamlit as st

from sklearn.metrics import classification_report, roc_curve

import numpy as np

import plotly.express as px

import pandas as pd

from numpy import argmax

from src.visualization.metrics import streamlit_2columns_metrics_df, streamlit_2columns_metrics_pct_df

from src.visualization.graphs_threshold import acceptance_rate_driven_threshold_graph


def model_probability_values_df(model, X):
    return pd.DataFrame(model.predict_proba(X)[:, 1], columns=["PROB_DEFAULT"])


def find_best_threshold_J_statistic(y, clf_prediction_prob_df):
    fpr, tpr, thresholds = roc_curve(y, clf_prediction_prob_df)
    # get the best threshold
    # Youden’s J statistic tpr-fpr
    # Argmax to get the index in
    # thresholds
    return thresholds[argmax(tpr - fpr)]

# Function that makes dataframe with probability of default, predicted default status based on threshold
# and actual default status


def classification_report_per_threshold(
    threshold_list, threshold_default_status_list, y_test
):
    target_names = ["Non-Default", "Default"]
    classification_report_list = []
    for threshold_default_status in threshold_default_status_list:
        thresh_classification_report = classification_report(
            y_test,
            threshold_default_status,
            target_names=target_names,
            output_dict=True,
            zero_division=0,
        )
        classification_report_list.append(thresh_classification_report)
    # Return threshold classification report dict
    return dict(zip(threshold_list, classification_report_list))


def thresh_classification_report_recall_accuracy(
    thresh_classification_report_dict,
):
    thresh_def_recalls_list = []
    thresh_nondef_recalls_list = []
    thresh_accs_list = []
    for x in [*thresh_classification_report_dict]:
        thresh_def_recall = thresh_classification_report_dict[x]["Default"][
            "recall"
        ]
        thresh_def_recalls_list.append(thresh_def_recall)
        thresh_nondef_recall = thresh_classification_report_dict[x][
            "Non-Default"
        ]["recall"]
        thresh_nondef_recalls_list.append(thresh_nondef_recall)
        thresh_accs = thresh_classification_report_dict[x]["accuracy"]
        thresh_accs_list.append(thresh_accs)
    return [
        thresh_def_recalls_list,
        thresh_nondef_recalls_list,
        thresh_accs_list,
    ]


def apply_threshold_to_probability_values(probability_values, threshold):
    return (
        probability_values["PROB_DEFAULT"]
        .apply(lambda x: 1 if x > threshold else 0)
        .rename("PREDICT_DEFAULT_STATUS")
    )


@st.cache(suppress_st_warning=True)
def find_best_threshold_J_statistic(y, clf_prediction_prob_df):
    fpr, tpr, thresholds = roc_curve(y, clf_prediction_prob_df)
    # get the best threshold
    J = tpr - fpr  # Youden’s J statistic
    ix = argmax(J)
    return thresholds[ix]


def default_status_per_threshold(threshold_list, prob_default):
    threshold_default_status_list = []
    for threshold in threshold_list:
        threshold_default_status = prob_default.apply(
            lambda x: 1 if x > threshold else 0
        )
        threshold_default_status_list.append(threshold_default_status)
    return threshold_default_status_list


def threshold_and_predictions(clf_xgbt_model, split_dataset, threshold):

    clf_prediction_prob_df_gbt = model_probability_values_df(
        clf_xgbt_model,
        split_dataset.X_test,
    )
    clf_thresh_predicted_default_status = (
        apply_threshold_to_probability_values(
            clf_prediction_prob_df_gbt,
            threshold,
        )
    )

    streamlit_2columns_metrics_df(
        "# of Predicted Defaults",
        "# of Predicted Non-Default",
        clf_thresh_predicted_default_status,
    )

    streamlit_2columns_metrics_pct_df(
        "% of Loans Predicted to Default",
        "% of Loans Predicted not to Default",
        clf_thresh_predicted_default_status,
    )

    return clf_thresh_predicted_default_status


def user_defined_probability_threshold(model_name_short, clf_xgbt_model, split_dataset):
    st.subheader("Classification Probability Threshold - User Defined")

    user_defined_threshold = st.slider(
        label="Default Probability Threshold:",
        min_value=0.0,
        max_value=1.0,
        value=0.8,
        key=f"threshold_{model_name_short}_default",
    )

    clf_thresh_predicted_default_status = threshold_and_predictions(
        clf_xgbt_model, split_dataset, user_defined_threshold)

    return clf_thresh_predicted_default_status, user_defined_threshold


def J_statistic_driven_probability_threshold(clf_prediction_prob_df_gbt, clf_xgbt_model, split_dataset):
    st.subheader("J Statistic Driven Classification Probability Threshold")

    J_statistic_best_threshold = find_best_threshold_J_statistic(
        split_dataset.y_test, clf_prediction_prob_df_gbt
    )
    st.metric(
        label="Youden's J statistic calculated best threshold",
        value=J_statistic_best_threshold,
    )

    clf_thresh_predicted_default_status = threshold_and_predictions(
        clf_xgbt_model, split_dataset, J_statistic_best_threshold)

    return clf_thresh_predicted_default_status, J_statistic_best_threshold


def create_tradeoff_graph(df):
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


def tradeoff_threshold(clf_prediction_prob_df_gbt, split_dataset):
    st.subheader(
        "Recall and Accuracy Tradeoff with given Probability Threshold"
    )

    threshold_list = np.arange(
        0, 1, 0.025).round(decimals=3).tolist()

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

    create_tradeoff_graph(df)


def select_probability_threshold(model_name_short,
                                 user_defined_threshold,
                                 clf_thresh_predicted_default_status_user_gbt,
                                 J_statistic_best_threshold,
                                 clf_thresh_predicted_default_status_Jstatistic_gbt,
                                 acc_rate_thresh_gbt,
                                 clf_thresh_predicted_default_status_acceptance_gbt):
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
        prob_thresh_selected_gbt = user_defined_threshold
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

    return prob_thresh_selected_gbt, predicted_default_status_gbt


def acceptance_rate_driven_threshold(model_name_short, clf_prediction_prob_df_gbt):
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

    acceptance_rate_driven_threshold_graph(
        clf_prediction_prob_df_gbt, acc_rate_thresh_gbt)

    clf_thresh_predicted_default_status_acceptance_gbt = apply_threshold_to_probability_values(
        clf_prediction_prob_df_gbt,
        acc_rate_thresh_gbt,
    )

    return acc_rate_thresh_gbt, clf_thresh_predicted_default_status_acceptance_gbt
