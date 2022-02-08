
import plotly.express as px

import streamlit as st

import matplotlib.pyplot as plt

import numpy as np


def acceptance_rate_driven_threshold_graph(clf_prediction_prob_df_gbt, acc_rate_thresh_gbt):
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


def recall_accuracy_threshold_tradeoff_fig(
    widthsize,
    heightsize,
    threshold_list,
    thresh_def_recalls_list,
    thresh_nondef_recalls_list,
    thresh_accs_list,
):
    fig = plt.figure(figsize=(widthsize, heightsize))
    plt.plot(threshold_list, thresh_def_recalls_list, label="Default Recall")
    plt.plot(
        threshold_list, thresh_nondef_recalls_list, label="Non-Default Recall"
    )
    plt.plot(threshold_list, thresh_accs_list, label="Model Accuracy")
    plt.xlabel("Probability Threshold")
    plt.ylabel("Score")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend()
    plt.title("Recall and Accuracy Score Tradeoff with Probability Threshold")
    plt.grid(False)
    return fig


def acceptance_rate_threshold_fig(probability_default, acceptancerate, bins):
    # Probability distribution
    probability_stat_distribution = probability_default.describe()

    # Acceptance rate threshold
    acc_rate_thresh = np.quantile(probability_default, acceptancerate)
    fig = plt.figure()

    plt.hist(
        probability_default,
        color="blue",
        bins=bins,
        histtype="bar",
        ec="white",
    )

    # Add a reference line to the plot for the threshold
    plt.axvline(x=acc_rate_thresh, color="red")
    plt.title("Acceptance Rate Thershold")

    return (
        fig,
        probability_stat_distribution,
        acc_rate_thresh,
    )
