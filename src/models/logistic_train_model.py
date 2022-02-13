
import numpy as np
from sklearn.linear_model import LogisticRegression
from src.features.build_features import SplitDataset
import streamlit as st
import pandas as pd

from src.visualization.graphs_logistic import plot_logistic_coeff_barh


@st.cache(suppress_st_warning=True)
def create_clf_logistic_model(X_train, y_train):
    # Create and fit the logistic regression model
    return LogisticRegression(solver="lbfgs").fit(X_train, np.ravel(y_train))


@st.cache(suppress_st_warning=True)
def create_coeff_dict_logistic_model(
    logistic_model, training_data
):
    return {
        feat: coef
        for coef, feat in zip(
            logistic_model.coef_[0, :], training_data.columns
        )
    }


def coeff_dict_to_sorted_df(coef_dict):
    coef_dict_sorted = dict(
        sorted(coef_dict.items(), key=lambda item: item[1], reverse=False)
    )

    data_items = coef_dict_sorted.items()
    data_list = list(data_items)

    return pd.DataFrame(data_list, columns=["Coefficient", "Value"])


def interpret_clf_logistic_model(clf_logistic_model, split_dataset):
    st.metric(
        label="# of Coefficients in Logistic Regression",
        value=clf_logistic_model.n_features_in_,
        delta=None,
        delta_color="normal",
    )

    st.subheader("Logistic Regression Coefficient Values")

    coef_dict = create_coeff_dict_logistic_model(
        clf_logistic_model, split_dataset.X_y_train)

    df = coeff_dict_to_sorted_df(coef_dict)

    fig = plot_logistic_coeff_barh(df)

    st.plotly_chart(fig)


def logistic_train_model(split_dataset: SplitDataset):
    st.header("Logistic Regression Model")

    clf_logistic_model = create_clf_logistic_model(
        split_dataset.X_train, split_dataset.y_train
    )

    interpret_clf_logistic_model(clf_logistic_model, split_dataset)

    return clf_logistic_model
