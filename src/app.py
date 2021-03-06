import streamlit as st
from typing import OrderedDict


from features.build_features import initialise_data

from models.xgboost_model import xgboost_class
from models.logistic_model import logistic_class

from models.util_model_comparison import model_comparison_view

from models.util_strategy_table import strategy_table_view


def main():

    st.write("Source code: https://github.com/pkiage/tool-credit-risk-modelling")
    currency_options = ["USD", "KES", "GBP"]

    model_options = ["XGBoost", "Logistic"]

    currency = st.sidebar.selectbox(
        label="What currency will you be using?", options=currency_options
    )

    st.title("GUI for Credit Risk Modelling")

    st.title("Data")

    (_dataset, split_dataset) = initialise_data()

    st.title("Modelling")

    models_selected_list = st.sidebar.multiselect(
        label="Select model", options=model_options, default=model_options
    )

    models_selected_set = set(models_selected_list)

    model_classes = OrderedDict()

    if "Logistic" in models_selected_set:
        logistic_model_class = logistic_class(split_dataset, currency)
        model_classes["Logistic"] = logistic_model_class

    if "XGBoost" in models_selected_set:
        xgboost_model_class = xgboost_class(split_dataset, currency)
        model_classes["XGBoost"] = xgboost_model_class

    model_comparison_view(split_dataset, model_classes)

    strategy_table_view(currency, model_classes)


if __name__ == "__main__":
    main()
