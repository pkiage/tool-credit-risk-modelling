import streamlit as st


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
