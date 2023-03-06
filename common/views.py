from typing import OrderedDict
import streamlit as st  # works on command prompt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    roc_curve,
)
from sklearn.calibration import calibration_curve
from xgboost import plot_tree
from views.typing import ModelView


def plot_logistic_coeff_barh(coef_dict, x, y):
    fig = plt.figure(figsize=(x, y))
    coef_dict_sorted = dict(
        sorted(coef_dict.items(), key=lambda item: item[1], reverse=False)
    )
    plt.barh(*zip(*coef_dict_sorted.items()))
    return fig


def print_negative_coefficients_logistic_model(coef_dict):
    # Equal to or less than 0
    NegativeCoefficients = dict(
        filter(lambda x: x[1] <= 0.0, coef_dict.items())
    )

    NegativeCoefficientsSorted = sorted(
        NegativeCoefficients.items(), key=lambda x: x[1], reverse=False
    )
    text = (
        "\n\nFeatures the model found to be negatively correlated with probability of default are:"
        "\n{negative_features}:"
    )
    st.markdown(text.format(negative_features=NegativeCoefficientsSorted))
    st.markdown(type(NegativeCoefficientsSorted))
    st.markdown(NegativeCoefficients.items())


def print_positive_coefficients_logistic_model(coef_dict):
    # Equal to or greater than 0
    PositiveCoefficients = dict(
        filter(lambda x: x[1] >= 0.0, coef_dict.items())
    )

    PositiveCoefficientsSorted = sorted(
        PositiveCoefficients.items(), key=lambda x: x[1], reverse=True
    )
    text = (
        "\n\nFeatures the model found to be positively correlated with probability of default are:"
        "\n{positive_features}:"
    )
    st.markdown(text.format(positive_features=PositiveCoefficientsSorted))


def plot_importance_gbt(clf_gbt_model, barxsize, barysize):
    axobject1 = xgb.plot_importance(clf_gbt_model, importance_type="weight")
    fig1 = axobject1.figure
    st.write("Feature Importance Plot (Gradient Boosted Tree)")
    fig1.set_size_inches(barxsize, barysize)
    return fig1


def download_importance_gbt(fig1, barxsize, barysize):
    if st.button(
        "Download Feature Importance Plot as png (Gradient Boosted Tree)"
    ):
        dpisize = max(barxsize, barysize)
        plt.savefig("bar.png", dpi=dpisize * 96, bbox_inches="tight")
        fig1.set_size_inches(barxsize, barysize)


def plot_tree_gbt(treexsize, treeysize, clf_gbt_model):
    plot_tree(clf_gbt_model)
    fig2 = plt.gcf()
    fig2.set_size_inches(treexsize, treeysize)
    return fig2


def download_tree_gbt(treexsize, treeysize):
    if st.button("Download Decision Tree Plot as png (Gradient Boosted Tree)"):
        dpisize = max(treexsize, treeysize)
        plt.savefig("tree.png", dpi=dpisize * 96, bbox_inches="tight")


def cross_validation_graph(cv, eval_metric, trees):

    # Plot the test AUC scores for each iteration
    fig = plt.figure()
    plt.plot(cv[cv.columns[2]])
    plt.title(
        "Test {eval_metric} Score Over {it_numbr} Iterations".format(
            eval_metric=eval_metric, it_numbr=trees
        )
    )
    plt.xlabel("Iteration Number")
    plt.ylabel("Test {eval_metric} Score".format(eval_metric=eval_metric))
    return fig


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


def roc_auc_compare_n_models(y, model_views: OrderedDict[str, ModelView]):
    colors = ["blue", "green"]
    fig = plt.figure()
    for color_idx, (model_name, model_view) in enumerate(model_views.items()):
        fpr, tpr, _thresholds = roc_curve(
            y, model_view.prediction_probability_df
        )
        plt.plot(fpr, tpr, color=colors[color_idx], label=f"{model_name}")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random Prediction")
    model_names = list(model_views.keys())
    if not model_names:
        model_name_str = "None"
    elif len(model_names) == 1:
        model_name_str = model_names[0]
    else:
        model_name_str = " and ".join(
            [", ".join(model_names[:-1]), model_names[-1]]
        )
    plt.title(f"ROC Chart for {model_name_str} on the Probability of Default")
    plt.xlabel("False Positive Rate (FP Rate)")
    plt.ylabel("True Positive Rate (TP Rate)")
    plt.legend()
    plt.grid(False)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    return fig


def calibration_curve_report_commented_n(
    y, model_views: OrderedDict[str, ModelView], bins: int
):
    fig = plt.figure()
    for model_name, model_view in model_views.items():
        frac_of_pos, mean_pred_val = calibration_curve(
            y,
            model_view.prediction_probability_df,
            n_bins=bins,
            normalize=True,
        )
        plt.plot(mean_pred_val, frac_of_pos, "s-", label=f"{model_name}")

    # Create the calibration curve plot with the guideline
    plt.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")

    plt.ylabel("Fraction of positives")
    plt.xlabel("Average Predicted Probability")
    plt.title("Calibration Curve")
    plt.legend()
    plt.grid(False)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
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


def streamlit_2columns_metrics_pct_df(
    column1name_label: str,
    column2name_label: str,
    df: pd.DataFrame,
):
    (
        column1name,
        column2name,
    ) = st.columns(2)

    with column1name:
        st.metric(
            label=column1name_label,
            value="{:.0%}".format(df.value_counts().get(1) / df.shape[0]),
            delta=None,
            delta_color="normal",
        )

    with column2name:
        st.metric(
            label=column2name_label,
            value="{:.0%}".format(df.value_counts().get(0) / df.shape[0]),
            delta=None,
            delta_color="normal",
        )


def streamlit_2columns_metrics_df(
    column1name_label: str,
    column2name_label: str,
    df: pd.DataFrame,
):
    (
        column1name,
        column2name,
    ) = st.columns(2)

    with column1name:
        st.metric(
            label=column1name_label,
            value=df.value_counts().get(1),
            delta=None,
            delta_color="normal",
        )

    with column2name:
        st.metric(
            label=column2name_label,
            value=df.value_counts().get(0),
            delta=None,
            delta_color="normal",
        )


def streamlit_2columns_metrics_df_shape(df: pd.DataFrame):
    (
        column1name,
        column2name,
    ) = st.columns(2)

    with column1name:
        st.metric(
            label="Rows",
            value=df.shape[0],
            delta=None,
            delta_color="normal",
        )

    with column2name:
        st.metric(
            label="Columns",
            value=df.shape[1],
            delta=None,
            delta_color="normal",
        )


def streamlit_2columns_metrics_pct_series(
    column1name_label: str,
    column2name_label: str,
    series: pd.Series,
):
    (
        column1name,
        column2name,
    ) = st.columns(2)
    with column1name:
        st.metric(
            label=column1name_label,
            value="{:.0%}".format(series.get(1) / series.sum()),
            delta=None,
            delta_color="normal",
        )

    with column2name:
        st.metric(
            label=column2name_label,
            value="{:.0%}".format(series.get(0) / series.sum()),
            delta=None,
            delta_color="normal",
        )


def streamlit_2columns_metrics_series(
    column1name_label: str,
    column2name_label: str,
    series: pd.Series,
):
    (
        column1name,
        column2name,
    ) = st.columns(2)
    with column1name:
        st.metric(
            label=column1name_label,
            value=series.get(1),
            delta=None,
            delta_color="normal",
        )

    with column2name:
        st.metric(
            label=column2name_label,
            value=series.get(0),
            delta=None,
            delta_color="normal",
        )


def streamlit_chart_setting_height_width(
    title: str,
    default_widthvalue: int,
    default_heightvalue: int,
    widthkey: str,
    heightkey: str,
):
    with st.expander(title):

        lbarx_col, lbary_col = st.columns(2)

        with lbarx_col:
            width_size = st.number_input(
                label="Width in inches:",
                value=default_widthvalue,
                key=widthkey,
            )

        with lbary_col:
            height_size = st.number_input(
                label="Height in inches:",
                value=default_heightvalue,
                key=heightkey,
            )
    return width_size, height_size
