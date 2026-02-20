# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pandas>=2.2",
#     "numpy>=1.26",
#     "scikit-learn>=1.5",
#     "plotly>=5.22",
#     "pydantic>=2.7",
# ]
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium", app_title="Credit Risk — Synthetic Data Exploration")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Synthetic Data Exploration

        Generate synthetic credit risk datasets and explore their distributions.
        Compare synthetic vs real data characteristics and model performance.
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

    from shared.constants import (
        CATEGORICAL_FEATURES,
        FEATURE_GROUP_LABELS,
        FEATURE_GROUPS,
        NUMERIC_FEATURES,
        SYNTHETIC_PRESETS,
    )
    from shared.logic.synthetic import generate_synthetic_dataset
    from shared.schemas.synthetic import SyntheticConfig, SyntheticDistribution

    return (
        CATEGORICAL_FEATURES,
        FEATURE_GROUP_LABELS,
        FEATURE_GROUPS,
        NUMERIC_FEATURES,
        SYNTHETIC_PRESETS,
        SyntheticConfig,
        SyntheticDistribution,
        generate_synthetic_dataset,
        go,
        make_subplots,
        np,
        pd,
        px,
    )


@app.cell
def _(SYNTHETIC_PRESETS, mo):
    preset_dropdown = mo.ui.dropdown(
        options={"Custom": "custom", **{k: k for k in SYNTHETIC_PRESETS}},
        value="Custom",
        label="Preset",
    )
    n_samples_slider = mo.ui.slider(
        start=100, stop=50000, step=100, value=5000, label="Number of Samples"
    )
    default_rate_slider = mo.ui.slider(
        start=0.01, stop=0.99, step=0.01, value=0.22, label="Default Rate"
    )
    seed_input = mo.ui.number(value=42, label="Random Seed")

    mo.md("### Generation Config")
    mo.hstack([preset_dropdown, n_samples_slider, default_rate_slider, seed_input])
    return (default_rate_slider, n_samples_slider, preset_dropdown, seed_input)


@app.cell
def _(
    SYNTHETIC_PRESETS,
    SyntheticConfig,
    default_rate_slider,
    generate_synthetic_dataset,
    n_samples_slider,
    preset_dropdown,
    seed_input,
):
    # Apply preset if selected
    if preset_dropdown.value != "custom" and preset_dropdown.value in SYNTHETIC_PRESETS:
        _preset = SYNTHETIC_PRESETS[preset_dropdown.value]
        config = SyntheticConfig(
            n_samples=_preset.get("n_samples", n_samples_slider.value),
            default_rate=_preset.get("default_rate", default_rate_slider.value),
            distributions=_preset.get("distributions", []),
            random_seed=int(seed_input.value) if seed_input.value else 42,
        )
    else:
        config = SyntheticConfig(
            n_samples=n_samples_slider.value,
            default_rate=default_rate_slider.value,
            random_seed=int(seed_input.value) if seed_input.value else 42,
        )

    X_synth, y_synth, feature_names, metadata = generate_synthetic_dataset(config)
    return (X_synth, config, feature_names, metadata, y_synth)


@app.cell
def _(metadata, mo, pd):
    mo.md(
        f"""
        ### Generated Dataset Summary
        - **Samples:** {metadata.n_samples}
        - **Features:** {metadata.n_features}
        - **Actual Default Rate:** {metadata.default_rate_actual:.2%}
        """
    )

    _stats_df = pd.DataFrame(metadata.summary_stats).T
    _stats_df.index.name = "Feature"
    _stats_df = _stats_df.round(3)
    mo.ui.table(_stats_df.reset_index())
    return


@app.cell
def _(
    FEATURE_GROUP_LABELS,
    NUMERIC_FEATURES,
    X_synth,
    feature_names,
    go,
    make_subplots,
):
    _n_numeric = len(NUMERIC_FEATURES)
    _titles = [FEATURE_GROUP_LABELS[f] for f in NUMERIC_FEATURES] + [""]
    fig_numeric = make_subplots(rows=2, cols=4, subplot_titles=_titles)

    for _i, _feat in enumerate(NUMERIC_FEATURES):
        _col_idx = feature_names.index(_feat)
        _row = _i // 4 + 1
        _col = _i % 4 + 1
        fig_numeric.add_trace(
            go.Histogram(
                x=X_synth[:, _col_idx],
                name=FEATURE_GROUP_LABELS[_feat],
                showlegend=False,
                marker_color="#636EFA",
            ),
            row=_row,
            col=_col,
        )

    fig_numeric.update_layout(title="Numeric Feature Distributions", height=500)
    fig_numeric
    return (fig_numeric,)


@app.cell
def _(
    CATEGORICAL_FEATURES,
    FEATURE_GROUP_LABELS,
    FEATURE_GROUPS,
    X_synth,
    feature_names,
    go,
):
    fig_categorical = go.Figure()
    for _cat in CATEGORICAL_FEATURES:
        _cols = FEATURE_GROUPS[_cat]
        _indices = [feature_names.index(c) for c in _cols]
        _counts = X_synth[:, _indices].sum(axis=0)
        _proportions = _counts / _counts.sum()
        _categories = [c.split("_")[-1] for c in _cols]

        fig_categorical.add_trace(
            go.Bar(
                x=_categories,
                y=_proportions,
                name=FEATURE_GROUP_LABELS[_cat],
            )
        )

    fig_categorical.update_layout(
        title="Categorical Feature Distributions",
        barmode="group",
        height=400,
    )
    fig_categorical
    return (fig_categorical,)


@app.cell
def _(pd):
    real_df = pd.read_csv("data/processed/cr_loan_w2.csv")
    return (real_df,)


@app.cell
def _(
    FEATURE_GROUP_LABELS,
    NUMERIC_FEATURES,
    X_synth,
    feature_names,
    go,
    make_subplots,
    real_df,
):
    _titles = [FEATURE_GROUP_LABELS[f] for f in NUMERIC_FEATURES] + [""]
    fig_compare = make_subplots(rows=2, cols=4, subplot_titles=_titles)

    for _i, _feat in enumerate(NUMERIC_FEATURES):
        _col_idx = feature_names.index(_feat)
        _row = _i // 4 + 1
        _col = _i % 4 + 1
        # Real
        fig_compare.add_trace(
            go.Histogram(
                x=real_df[_feat].values,
                name="Real",
                opacity=0.5,
                marker_color="#EF553B",
                showlegend=(_i == 0),
            ),
            row=_row,
            col=_col,
        )
        # Synthetic
        fig_compare.add_trace(
            go.Histogram(
                x=X_synth[:, _col_idx],
                name="Synthetic",
                opacity=0.5,
                marker_color="#636EFA",
                showlegend=(_i == 0),
            ),
            row=_row,
            col=_col,
        )

    fig_compare.update_layout(
        title="Real vs Synthetic — Numeric Features",
        barmode="overlay",
        height=500,
    )
    fig_compare
    return (fig_compare,)


@app.cell
def _(mo):
    mo.md(
        """
        ### Model Comparison: Real vs Synthetic Training Data

        Train the same model type on both datasets and compare metrics.
        """
    )
    return


@app.cell
def _(X_synth, np, real_df, y_synth):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    from shared import constants
    from shared.logic.evaluation import evaluate_model

    # Real data
    _X_real = real_df[constants.ALL_FEATURES].values.astype(np.float64)
    _y_real = real_df[constants.TARGET_COLUMN].values.astype(np.int_)

    results = {}
    for _label, _X, _y in [("Real", _X_real, _y_real), ("Synthetic", X_synth, y_synth)]:
        _X_train, _X_test, _y_train, _y_test = train_test_split(
            _X, _y, test_size=0.2, random_state=42, stratify=_y
        )
        _model = LogisticRegression(max_iter=1000, random_state=42)
        _model.fit(_X_train, _y_train)
        _y_proba = _model.predict_proba(_X_test)[:, 1]
        _metrics = evaluate_model(_y_test, _y_proba)
        results[_label] = _metrics

    return (results,)


@app.cell
def _(mo, pd, results):
    _rows = []
    for _label, _m in results.items():
        _rows.append(
            {
                "Dataset": _label,
                "Accuracy": f"{_m.accuracy:.4f}",
                "Precision": f"{_m.precision:.4f}",
                "Recall": f"{_m.recall:.4f}",
                "F1": f"{_m.f1_score:.4f}",
                "ROC-AUC": f"{_m.roc_auc:.4f}",
            }
        )
    mo.ui.table(pd.DataFrame(_rows), selection=None)
    return


if __name__ == "__main__":
    app.run()
