from common.data import SplitDataset
import streamlit as st
from common.util import (
    test_variables_gbt,
)
from common.views import (
    streamlit_chart_setting_height_width,
    plot_importance_gbt,
    plot_tree_gbt,
    download_importance_gbt,
    download_tree_gbt,
)
from views.typing import ModelView
from views.threshold import decision_tree_threshold_view
from views.evaluation import decision_tree_evaluation_view


def decisiontree_view(split_dataset: SplitDataset, currency: str):
    st.header("Decision Trees")

    clf_gbt_model = test_variables_gbt(
        split_dataset.X_train, split_dataset.y_train
    )

    st.subheader("Decision Tree Feature Importance")

    (barxsize, barysize,) = streamlit_chart_setting_height_width(
        "Chart Settings", 10, 15, "barxsize", "barysize"
    )

    fig1 = plot_importance_gbt(clf_gbt_model, barxsize, barysize)

    st.pyplot(fig1)

    download_importance_gbt(fig1, barxsize, barysize)

    st.subheader("Decision Tree Structure")

    (treexsize, treeysize,) = streamlit_chart_setting_height_width(
        "Chart Settings", 15, 10, "treexsize", "treeysize"
    )

    fig2 = plot_tree_gbt(treexsize, treeysize, clf_gbt_model)

    st.pyplot(fig2)

    download_tree_gbt(treexsize, treeysize)
    st.markdown(
        "Note: The downloaded decision tree plot chart in png has higher resolution than that displayed here."
    )

    threshold = decision_tree_threshold_view(clf_gbt_model, split_dataset)

    df_trueStatus_probabilityDefault_threshStatus_loanAmount = (
        decision_tree_evaluation_view(
            clf_gbt_model,
            split_dataset,
            currency,
            threshold.probability_threshold_selected,
            threshold.predicted_default_status,
        )
    )

    return ModelView(
        model=clf_gbt_model,
        trueStatus_probabilityDefault_threshStatus_loanAmount_df=df_trueStatus_probabilityDefault_threshStatus_loanAmount,
        probability_threshold_selected=threshold.probability_threshold_selected,
        predicted_default_status=threshold.predicted_default_status,
        prediction_probability_df=threshold.prediction_probability_df,
    )
