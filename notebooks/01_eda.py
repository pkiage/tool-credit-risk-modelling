# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pandas>=2.2",
#     "numpy>=1.26",
#     "plotly>=5.22",
#     "pydantic>=2.7",
# ]
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium", app_title="Credit Risk — EDA")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Exploratory Data Analysis

        Explore the credit risk loan dataset: distributions, correlations,
        and feature-target relationships.
        """
    )
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    from shared import constants

    return constants, go, make_subplots, np, pd, px


@app.cell
def _(mo):
    upload_widget = mo.ui.file(
        filetypes=[".csv"],
        label="Upload custom CSV (optional — uses default dataset if empty)",
    )
    upload_widget
    return (upload_widget,)


@app.cell
def _(constants, pd, upload_widget):
    if upload_widget.value:
        _bytes = upload_widget.value[0].contents
        import io

        df = pd.read_csv(io.BytesIO(_bytes))
    else:
        df = pd.read_csv("data/processed/cr_loan_w2.csv")

    target = constants.TARGET_COLUMN
    numeric_cols = [c for c in constants.NUMERIC_FEATURES if c in df.columns]
    categorical_encoded = [
        c for c in constants.CATEGORICAL_FEATURES_ENCODED if c in df.columns
    ]
    return categorical_encoded, df, numeric_cols, target


@app.cell
def _(mo):
    mo.md("## 1 — Dataset Overview")
    return


@app.cell
def _(df, mo, target):
    _shape = f"**Rows:** {df.shape[0]:,}  |  **Columns:** {df.shape[1]}"
    _dtypes = df.dtypes.value_counts().to_frame("count").to_markdown()
    _missing = df.isnull().sum()
    _missing_total = int(_missing.sum())
    _missing_info = (
        "No missing values" if _missing_total == 0 else f"{_missing_total} missing"
    )
    _target_counts = df[target].value_counts().to_dict()

    mo.md(
        f"""
    {_shape}

    | Metric | Value |
    |--------|-------|
    | Missing values | {_missing_info} |
    | Default rate | {_target_counts.get(1, 0) / len(df):.2%} |
    | Non-default | {_target_counts.get(0, 0):,} |
    | Default | {_target_counts.get(1, 0):,} |

    **Data types**

    {_dtypes}
    """
    )
    return


@app.cell
def _(mo):
    mo.md("## 2 — Target Distribution")
    return


@app.cell
def _(df, px, target):
    _counts = df[target].value_counts().reset_index()
    _counts.columns = [target, "count"]
    _counts[target] = _counts[target].map({0: "Non-Default", 1: "Default"})

    fig_target = px.bar(
        _counts,
        x=target,
        y="count",
        color=target,
        color_discrete_map={"Non-Default": "#636EFA", "Default": "#EF553B"},
        title="Loan Default Distribution",
        text="count",
    )
    fig_target.update_layout(showlegend=False)
    fig_target
    return (fig_target,)


@app.cell
def _(mo):
    mo.md("## 3 — Numeric Feature Distributions")
    return


@app.cell
def _(df, make_subplots, go, numeric_cols, target):
    _n = len(numeric_cols)
    _cols = 2
    _rows = (_n + 1) // _cols

    fig_numeric = make_subplots(rows=_rows, cols=_cols, subplot_titles=numeric_cols)

    for _i, _col in enumerate(numeric_cols):
        _r = _i // _cols + 1
        _c = _i % _cols + 1
        for _label, _color in [(0, "#636EFA"), (1, "#EF553B")]:
            _vals = df.loc[df[target] == _label, _col]
            fig_numeric.add_trace(
                go.Histogram(
                    x=_vals,
                    name=f"{'Default' if _label else 'Non-Default'}",
                    marker_color=_color,
                    opacity=0.6,
                    showlegend=(_i == 0),
                ),
                row=_r,
                col=_c,
            )

    fig_numeric.update_layout(
        barmode="overlay",
        height=300 * _rows,
        title_text="Numeric Feature Distributions by Default Status",
    )
    fig_numeric
    return (fig_numeric,)


@app.cell
def _(mo):
    mo.md("## 4 — Categorical Feature Distributions")
    return


@app.cell
def _(categorical_encoded, constants, df, make_subplots, go, target):
    # Group one-hot columns back into original categories
    _cat_groups: dict[str, list[str]] = {}
    for _orig in constants.CATEGORICAL_FEATURES:
        _cat_groups[_orig] = [
            c for c in categorical_encoded if c.startswith(_orig + "_")
        ]

    _n_cats = len(_cat_groups)
    fig_cat = make_subplots(
        rows=_n_cats,
        cols=1,
        subplot_titles=list(_cat_groups.keys()),
    )

    for _i, (_name, _cols) in enumerate(_cat_groups.items()):
        _labels = [c.replace(_name + "_", "") for c in _cols]
        for _label_val, _color, _legend in [
            (0, "#636EFA", "Non-Default"),
            (1, "#EF553B", "Default"),
        ]:
            _subset = df[df[target] == _label_val]
            _counts = [int(_subset[c].sum()) for c in _cols]
            fig_cat.add_trace(
                go.Bar(
                    x=_labels,
                    y=_counts,
                    name=_legend,
                    marker_color=_color,
                    showlegend=(_i == 0),
                ),
                row=_i + 1,
                col=1,
            )

    fig_cat.update_layout(
        barmode="group",
        height=350 * _n_cats,
        title_text="Categorical Features by Default Status",
    )
    fig_cat
    return (fig_cat,)


@app.cell
def _(mo):
    mo.md("## 5 — Correlation Heatmap")
    return


@app.cell
def _(df, numeric_cols, px, target):
    _corr_cols = numeric_cols + [target]
    _corr = df[_corr_cols].corr()

    fig_corr = px.imshow(
        _corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Matrix (Numeric Features + Target)",
    )
    fig_corr.update_layout(height=600, width=700)
    fig_corr
    return (fig_corr,)


@app.cell
def _(mo):
    mo.md("## 6 — Feature-Target Relationships")
    return


@app.cell
def _(df, mo, numeric_cols):
    feature_select = mo.ui.dropdown(
        options=numeric_cols,
        value=numeric_cols[0],
        label="Select feature",
    )
    feature_select
    return (feature_select,)


@app.cell
def _(df, feature_select, px, target):
    _col = feature_select.value
    _df_plot = df[[_col, target]].copy()
    _df_plot["Default Status"] = _df_plot[target].map({0: "Non-Default", 1: "Default"})

    fig_relationship = px.box(
        _df_plot,
        x="Default Status",
        y=_col,
        color="Default Status",
        color_discrete_map={"Non-Default": "#636EFA", "Default": "#EF553B"},
        title=f"{_col} by Default Status",
    )
    fig_relationship
    return (fig_relationship,)


if __name__ == "__main__":
    app.run()
