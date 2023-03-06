from typing import OrderedDict
import streamlit as st
from sklearn.metrics import roc_auc_score
from common.data import SplitDataset
from common.views import (
    roc_auc_compare_n_models,
    streamlit_chart_setting_height_width,
    calibration_curve_report_commented_n,
)
from views.typing import ModelView


def roc_auc_for_model(split_dataset: SplitDataset, model_view: ModelView):
    roc_auc_model = roc_auc_score(
        split_dataset.y_test, model_view.predicted_default_status
    )

    if roc_auc_model > 0.9:
        roc_auc_lvl = f'Very good {"{:.2f}".format(roc_auc_model)} > 0.9)'
    elif 0.8 < roc_auc_model < 0.9:
        roc_auc_lvl = f'Good (0.8 < {"{:.2f}".format(roc_auc_model)} <0.9)'
    elif 0.7 < roc_auc_model < 0.8:
        roc_auc_lvl = f'Fair (0.7 <  {"{:.2f}".format(roc_auc_model)} < 0.8)'
    elif 0.6 < roc_auc_model < 0.7:
        roc_auc_lvl = f'Poor (0.6 <  {"{:.2f}".format(roc_auc_model)} < 0.7)'
    else:
        roc_auc_lvl = f'Fail ( {"{:.2f}".format(roc_auc_model)} < 0.6)'

    return roc_auc_model, roc_auc_lvl


def model_comparison_view(
    split_dataset: SplitDataset,
    model_views: OrderedDict[str, ModelView],
):
    st.header("Model Comparison")

    for model_name, model_view in model_views.items():
        roc_auc_model, roc_auc_lvl = roc_auc_for_model(
            split_dataset, model_view
        )
        st.subheader(
            f"Receiver Operating Characteristic (ROC) Curve - {model_name}"
        )
        st.markdown(
            f'Area Under the Receiver Operating Characteristic Curve from prediction scores from "{model_name}" model is {roc_auc_model}.\n'
        )
        st.markdown(
            f'The score of {"{:.2f}".format(roc_auc_model)} is in the {roc_auc_lvl} ROC AUC score category.'
        )
    fig1 = roc_auc_compare_n_models(
        split_dataset.y_test,
        model_views,
    )

    fig1 = fig1.figure

    (xsize_roc, ysize_roc) = streamlit_chart_setting_height_width(
        "Chart Settings", 7, 7, "xsize_roc", "ysize_roc"
    )

    fig1.set_size_inches(xsize_roc, ysize_roc)

    st.pyplot(fig1)

    st.subheader("Models Calibration Curve")

    fig2 = calibration_curve_report_commented_n(
        split_dataset.y_test,
        model_views,
        10,
    )
    fig2 = fig2.figure

    (xsize_cal, ysize_cal) = streamlit_chart_setting_height_width(
        "Chart Settings", 7, 7, "xsize_cal", "ysize_cal"
    )

    fig2.set_size_inches(xsize_cal, ysize_cal)

    st.pyplot(fig2.figure)
