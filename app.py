from typing import OrderedDict
import streamlit as st
from data_setup import initialise_data
from views.decision_tree import decisiontree_view
from views.logistic import logistic_view
from views.model_comparison import model_comparison_view
from views.strategy_table import strategy_table_view
import os
os.environ["PATH"] += os.pathsep + 'C:\Program Files (x86)\Graphviz0.19.1/bin/'


def main():
    currency_options = ["USD", "KES", "GBP"]

    currency = st.sidebar.selectbox(
        label="What currency will you be using?", options=currency_options
    )

    st.title("GUI for Credit Risk Modelling")

    st.title("Data")

    (_dataset, split_dataset) = initialise_data()

    st.title("Modelling")

    model_options = ["Logistic Regression", "Decision Trees"]

    # Returns list
    models_selected_list = st.sidebar.multiselect(
        label="Select model", options=model_options, default=model_options
    )

    models_selected_set = set(models_selected_list)
    model_views = OrderedDict()

    if "Logistic Regression" in models_selected_set:
        logistic_model_view = logistic_view(split_dataset, currency)
        model_views["Logistic Regression"] = logistic_model_view

    if "Decision Trees" in models_selected_set:
        decision_tree_model_view = decisiontree_view(split_dataset, currency)
        model_views["Decision Trees"] = decision_tree_model_view

    if models_selected_list:
        model_comparison_view(
            split_dataset,
            model_views,
        )
        strategy_table_view(currency, model_views)


if __name__ == "__main__":
    main()
