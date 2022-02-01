from typing import Tuple, cast

import pandas as pd
import streamlit as st

from common.data import Dataset, SplitDataset
from common.util import (
    undersample_training_data,
)
from common.views import (
    streamlit_2columns_metrics_df_shape,
    streamlit_2columns_metrics_series,
    streamlit_2columns_metrics_pct_series,
    streamlit_2columns_metrics_df,
    streamlit_2columns_metrics_pct_df,
)


# Initialize dataframe session state
def initialise_data() -> Tuple[Dataset, SplitDataset]:
    if "input_data_frame" not in st.session_state:
        st.session_state.input_data_frame = pd.read_csv(
            r"./data/processed/cr_loan_w2.csv"
        )
    if "dataset" not in st.session_state:
        df = cast(pd.DataFrame, st.session_state.input_data_frame)
        dataset = Dataset(
            df=df,
            random_state=123235,
            test_size=40,
        )
        st.session_state.dataset = dataset
    else:
        dataset = st.session_state.dataset

    st.write(
        "Assuming data is already cleaned and relevant features (predictors) added."
    )

    with st.expander("Input Dataframe (X and y)"):
        st.dataframe(dataset.df)
        streamlit_2columns_metrics_df_shape(dataset.df)

    st.header("Predictors")

    possible_columns = dataset.x_values_column_names

    selected_columns = st.sidebar.multiselect(
        label="Select Predictors",
        options=possible_columns,
        default=possible_columns,
    )

    selected_x_values = dataset.x_values_filtered_columns(selected_columns)

    st.sidebar.metric(
        label="# of Predictors Selected",
        value=selected_x_values.shape[1],
        delta=None,
        delta_color="normal",
    )
    with st.expander("Predictors Dataframe (X)"):
        st.dataframe(selected_x_values)
        streamlit_2columns_metrics_df_shape(selected_x_values)

    # 40% of data used for training
    # 14321 as random seed for reproducability

    st.header("Split Testing and Training Data")

    test_size_slider_col, seed_col = st.columns(2)

    with test_size_slider_col:
        # Initialize test size
        dataset.test_size = st.slider(
            label="Test Size Percentage of Input Dataframe:",
            min_value=0,
            max_value=100,
            value=dataset.test_size,
            key="init_test_size",
            format="%f%%",
        )

    with seed_col:
        dataset.random_state = int(
            st.number_input(label="Random State:", value=dataset.random_state)
        )

    split_dataset = dataset.train_test_split(selected_x_values)

    # Series
    true_status = split_dataset.y_test.to_frame().value_counts()

    st.sidebar.metric(
        label="Testing Data # of Actual Default (=1)",
        value=true_status.get(1),
    )

    st.sidebar.metric(
        label="Testing Data % of Actual Default",
        value="{:.0%}".format(true_status.get(1) / true_status.sum()),
    )

    st.sidebar.metric(
        label="Testing Data # of Actual Non-Default (=0)",
        value=true_status.get(0),
    )

    st.sidebar.metric(
        label="Testing Data % of Actual Non-Default",
        value="{:.0%}".format(true_status.get(0) / true_status.sum()),
    )

    # Concat the testing sets
    X_y_test = split_dataset.X_y_test
    X_y_train = split_dataset.X_y_train

    with st.expander("Testing Dataframe (X and y)"):
        st.dataframe(X_y_test)
        streamlit_2columns_metrics_df_shape(X_y_test)

    streamlit_2columns_metrics_series(
        "# Defaults(=1) (Testing Data)",
        "# Non-Defaults(=0) (Testing Data)",
        true_status,
    )

    streamlit_2columns_metrics_pct_series(
        "% Defaults (Testing Data)",
        "% Non-Defaults (Testing Data)",
        true_status,
    )

    st.header("Training Data")

    with st.expander("Training Dataframe (X and y)"):
        st.dataframe(X_y_train)
        streamlit_2columns_metrics_df_shape(X_y_train)

    st.subheader("Class Count")

    streamlit_2columns_metrics_df(
        "# Defaults (Training Data Class Balance Check)",
        "# Non-Defaults (Training Data Class Balance Check)",
        split_dataset.y_train,
    )

    streamlit_2columns_metrics_pct_df(
        "% Defaults (Training Data Class Balance Check)",
        "% Non-Defaults (Training Data Class Balance Check)",
        split_dataset.y_train,
    )

    balance_the_classes = st.radio(
        label="Balance the Classes:", options=("Yes", "No")
    )

    if balance_the_classes == "Yes":
        st.subheader("Balanced Classes (by Undersampling)")

        (
            split_dataset.X_train,
            split_dataset.y_train,
            _X_y_train,
            class_balance_default,
        ) = undersample_training_data(X_y_train, "loan_status", split_dataset)

        streamlit_2columns_metrics_series(
            "# Defaults (Training Data with Class Balance)",
            "# Non-Defaults (Training Data with Class Balance)",
            class_balance_default,
        )

        streamlit_2columns_metrics_pct_series(
            "% of Defaults (Training Data with Class Balance)",
            "% of Non-Defaults (Training Data with Class Balance)",
            class_balance_default,
        )

    return dataset, split_dataset
