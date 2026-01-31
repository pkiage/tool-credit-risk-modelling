# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pandas>=2.2",
#     "numpy>=1.26",
#     "scikit-learn>=1.5",
#     "xgboost>=2.1",
#     "plotly>=5.22",
#     "pydantic>=2.7",
# ]
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium", app_title="Credit Risk — Threshold Optimization")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Threshold Optimization — Youden's J

        A classification threshold converts predicted probabilities into
        binary decisions (approve / deny). The **default 0.5** is rarely
        optimal.

        **Youden's J statistic** finds the threshold that maximises the
        separation between true positive rate (sensitivity) and false positive
        rate (1 − specificity):

        $$J = \\text{sensitivity} + \\text{specificity} - 1$$
        """
    )
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    from shared import constants
    from shared.logic.evaluation import (
        calculate_confusion_matrix,
        calculate_roc_curve,
    )
    from shared.logic.threshold import evaluate_threshold, find_optimal_threshold
    from shared.schemas.metrics import ThresholdResult

    return (
        RandomForestClassifier,
        ThresholdResult,
        calculate_confusion_matrix,
        calculate_roc_curve,
        constants,
        evaluate_threshold,
        find_optimal_threshold,
        go,
        make_subplots,
        np,
        pd,
        train_test_split,
    )


@app.cell
def _(RandomForestClassifier, constants, np, pd, train_test_split):
    # Train a single model for demonstration
    _df = pd.read_csv("data/processed/cr_loan_w2.csv")
    _X = _df[constants.ALL_FEATURES].values.astype(np.float64)
    _y = _df[constants.TARGET_COLUMN].values.astype(np.int_)

    _X_train, X_test, _y_train, y_test = train_test_split(
        _X, _y, test_size=0.2, random_state=42, stratify=_y
    )

    _model = RandomForestClassifier(**constants.RANDOM_FOREST_PARAMS)  # type: ignore
    _model.fit(_X_train, _y_train)
    y_proba = _model.predict_proba(X_test)[:, 1]
    return X_test, y_proba, y_test


@app.cell
def _(mo):
    mo.md(
        """
        ## Sensitivity vs Specificity

        - **Sensitivity (recall)**: proportion of actual defaults correctly
          identified → TP / (TP + FN)
        - **Specificity**: proportion of actual non-defaults correctly
          identified → TN / (TN + FP)

        Lowering the threshold catches more defaults (higher sensitivity) but
        increases false alarms (lower specificity).
        """
    )
    return


@app.cell
def _(find_optimal_threshold, y_proba, y_test):
    optimal = find_optimal_threshold(y_test, y_proba)
    return (optimal,)


@app.cell
def _(calculate_roc_curve, go, optimal, y_proba, y_test):
    _roc = calculate_roc_curve(y_test, y_proba)

    fig_roc = go.Figure()
    fig_roc.add_trace(
        go.Scatter(
            x=_roc.fpr,
            y=_roc.tpr,
            mode="lines",
            name="ROC Curve",
            line={"color": "#636EFA"},
        )
    )
    # Optimal point
    fig_roc.add_trace(
        go.Scatter(
            x=[1 - optimal.specificity],
            y=[optimal.sensitivity],
            mode="markers+text",
            name=f"Optimal (J={optimal.youden_j:.3f})",
            marker={"size": 12, "color": "#EF553B"},
            text=[f"t={optimal.threshold:.3f}"],
            textposition="top right",
        )
    )
    fig_roc.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line={"dash": "dash", "color": "gray"},
            name="Random",
        )
    )
    fig_roc.update_layout(
        title="ROC Curve with Optimal Threshold",
        xaxis_title="False Positive Rate (1 − Specificity)",
        yaxis_title="True Positive Rate (Sensitivity)",
        height=500,
    )
    fig_roc
    return (fig_roc,)


@app.cell
def _(mo):
    mo.md("## Interactive Threshold Explorer")
    return


@app.cell
def _(mo, optimal):
    threshold_slider = mo.ui.slider(
        start=0.0,
        stop=1.0,
        step=0.01,
        value=round(optimal.threshold, 2),
        label="Classification threshold",
        show_value=True,
    )
    threshold_slider
    return (threshold_slider,)


@app.cell
def _(evaluate_threshold, threshold_slider, y_proba, y_test):
    current = evaluate_threshold(y_test, y_proba, threshold_slider.value)
    return (current,)


@app.cell
def _(current, mo, optimal):
    mo.md(
        f"""
    ### Metrics at threshold = {current.threshold:.2f}

    | Metric | Current | Optimal ({optimal.threshold:.3f}) |
    |--------|---------|---------|
    | Sensitivity | {current.sensitivity:.4f} | {optimal.sensitivity:.4f} |
    | Specificity | {current.specificity:.4f} | {optimal.specificity:.4f} |
    | Precision | {current.precision:.4f} | {optimal.precision:.4f} |
    | F1 Score | {current.f1_score:.4f} | {optimal.f1_score:.4f} |
    | Youden's J | {current.youden_j:.4f} | {optimal.youden_j:.4f} |
    """
    )
    return


@app.cell
def _(mo):
    mo.md("### Confusion Matrix")
    return


@app.cell
def _(calculate_confusion_matrix, go, np, threshold_slider, y_proba, y_test):
    _y_pred = (y_proba >= threshold_slider.value).astype(np.int_)
    _cm = calculate_confusion_matrix(y_test, _y_pred)

    _labels = ["Non-Default", "Default"]
    _z = [
        [_cm.true_negatives, _cm.false_positives],
        [_cm.false_negatives, _cm.true_positives],
    ]
    _text = [
        [f"TN={_cm.true_negatives}", f"FP={_cm.false_positives}"],
        [f"FN={_cm.false_negatives}", f"TP={_cm.true_positives}"],
    ]

    fig_cm = go.Figure(
        data=go.Heatmap(
            z=_z,
            x=_labels,
            y=_labels,
            text=_text,
            texttemplate="%{text}",
            colorscale="Blues",
            showscale=False,
        )
    )
    fig_cm.update_layout(
        title=f"Confusion Matrix (threshold={threshold_slider.value:.2f})",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        height=400,
        width=450,
    )
    fig_cm
    return (fig_cm,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Youden's J Calculation

        Youden's J is computed at every possible threshold from the ROC curve
        and the maximum is selected. This balances sensitivity and specificity
        without requiring business-specific cost assumptions.
        """
    )
    return


@app.cell
def _(calculate_roc_curve, go, np, optimal, y_proba, y_test):
    _roc = calculate_roc_curve(y_test, y_proba)
    _j_values = [t - f for t, f in zip(_roc.tpr, _roc.fpr)]

    fig_j = go.Figure()
    fig_j.add_trace(
        go.Scatter(
            x=_roc.thresholds,
            y=_j_values[: len(_roc.thresholds)],
            mode="lines",
            name="Youden's J",
            line={"color": "#636EFA"},
        )
    )
    fig_j.add_vline(
        x=optimal.threshold,
        line_dash="dash",
        line_color="#EF553B",
        annotation_text=f"Optimal={optimal.threshold:.3f}",
    )
    fig_j.update_layout(
        title="Youden's J across Thresholds",
        xaxis_title="Threshold",
        yaxis_title="J = Sensitivity + Specificity − 1",
        height=400,
    )
    fig_j
    return (fig_j,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Business Impact Calculator

        In practice, the costs of false positives (denying a good loan) and
        false negatives (approving a bad loan) differ. Adjust the costs below
        to find the threshold that minimises total expected loss.
        """
    )
    return


@app.cell
def _(mo):
    fp_cost_input = mo.ui.number(
        start=0, stop=100000, value=100, step=10, label="Cost per False Positive ($)"
    )
    fn_cost_input = mo.ui.number(
        start=0, stop=100000, value=500, step=10, label="Cost per False Negative ($)"
    )
    mo.hstack([fp_cost_input, fn_cost_input])
    return fn_cost_input, fp_cost_input


@app.cell
def _(
    calculate_confusion_matrix,
    fn_cost_input,
    fp_cost_input,
    go,
    mo,
    np,
    y_proba,
    y_test,
):
    _thresholds = np.arange(0.05, 0.96, 0.01)
    _costs = []
    for _t in _thresholds:
        _yp = (y_proba >= _t).astype(np.int_)
        _cm = calculate_confusion_matrix(y_test, _yp)
        _total = (
            _cm.false_positives * fp_cost_input.value
            + _cm.false_negatives * fn_cost_input.value
        )
        _costs.append(_total)

    _min_idx = int(np.argmin(_costs))
    _best_t = float(_thresholds[_min_idx])
    _best_cost = _costs[_min_idx]

    fig_cost = go.Figure()
    fig_cost.add_trace(
        go.Scatter(
            x=_thresholds.tolist(),
            y=_costs,
            mode="lines",
            name="Total Cost",
            line={"color": "#636EFA"},
        )
    )
    fig_cost.add_vline(
        x=_best_t,
        line_dash="dash",
        line_color="#EF553B",
        annotation_text=f"Min cost @ {_best_t:.2f}",
    )
    fig_cost.update_layout(
        title="Expected Cost by Threshold",
        xaxis_title="Threshold",
        yaxis_title="Total Cost ($)",
        height=400,
    )

    mo.vstack(
        [
            fig_cost,
            mo.md(
                f"**Cost-optimal threshold: {_best_t:.2f}** — "
                f"total cost: ${_best_cost:,.0f} "
                f"(FP=${fp_cost_input.value}, FN=${fn_cost_input.value})"
            ),
        ]
    )
    return (fig_cost,)


if __name__ == "__main__":
    app.run()
