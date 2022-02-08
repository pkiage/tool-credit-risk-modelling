
import pandas as pd
import streamlit as st


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
