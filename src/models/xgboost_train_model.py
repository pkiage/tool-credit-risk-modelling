import pickle

import numpy as np
import xgboost as xgb
from src.features.build_features import SplitDataset
import streamlit as st

from src.visualization.graphs_decision_tree import(plot_importance_gbt,
                                                   plot_tree_gbt)

from src.visualization.graphs_settings import streamlit_chart_setting_height_width

from src.visualization.graphs_download import (download_importance_gbt,
                                               download_tree_gbt)


@ st.cache(suppress_st_warning=True, hash_funcs={
    xgb.XGBClassifier: pickle.dumps
})
def create_clf_xgbt_model(X_train, y_train):
    # Using hyperparameters learning_rate and max_depth
    return xgb.XGBClassifier(
        learning_rate=0.1,
        max_depth=7,
        use_label_encoder=False,
        eval_metric="logloss",
    ).fit(X_train, np.ravel(y_train), eval_metric="logloss")


def interpret_clf_xgbt_model(clf_xgbt_model):
    st.subheader("XGBoost Decision Tree Feature Importance")

    (barxsize, barysize,) = streamlit_chart_setting_height_width(
        "Chart Settings", 10, 15, "barxsize", "barysize"
    )

    fig1 = plot_importance_gbt(clf_xgbt_model, barxsize, barysize)

    st.pyplot(fig1)

    download_importance_gbt(fig1, barxsize, barysize)

    st.subheader("XGBoost Decision Tree Structure")

    (treexsize, treeysize,) = streamlit_chart_setting_height_width(
        "Chart Settings", 15, 10, "treexsize", "treeysize"
    )

    fig2 = plot_tree_gbt(treexsize, treeysize, clf_xgbt_model)

    st.pyplot(fig2)

    download_tree_gbt(treexsize, treeysize)
    st.markdown(
        "Note: The downloaded XGBoost Decision Tree plot chart in png has higher resolution than that displayed here."
    )


def xgboost_train_model(split_dataset: SplitDataset, currency: str):
    st.header("XGBoost Decision Trees")

    clf_xgbt_model = create_clf_xgbt_model(
        split_dataset.X_train, split_dataset.y_train
    )

    interpret_clf_xgbt_model(clf_xgbt_model)

    return clf_xgbt_model
