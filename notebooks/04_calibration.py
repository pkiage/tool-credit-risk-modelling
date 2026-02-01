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
app = marimo.App(width="medium", app_title="Credit Risk — Calibration")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Probability Calibration

        A model's predicted probability should reflect the true likelihood of
        default. If a model says "30% chance of default", roughly 30% of those
        loans should actually default. When this holds, the model is
        **well-calibrated**.

        Poorly calibrated probabilities mislead threshold selection and risk
        pricing. This notebook visualises calibration and applies correction
        methods.
        """
    )
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import brier_score_loss
    from sklearn.model_selection import train_test_split

    from shared import constants
    from shared.logic.evaluation import calculate_calibration_curve

    return (
        CalibratedClassifierCV,
        brier_score_loss,
        calculate_calibration_curve,
        constants,
        go,
        make_subplots,
        np,
        pd,
        train_test_split,
    )


@app.cell
def _(mo):
    upload_widget = mo.ui.file(
        filetypes=[".csv"],
        label="Upload custom CSV (optional — uses default dataset if empty)",
    )
    model_type_selector = mo.ui.dropdown(
        options=["random_forest", "logistic_regression", "xgboost"],
        value="random_forest",
        label="Model",
    )
    mo.hstack([upload_widget, model_type_selector])
    return model_type_selector, upload_widget


@app.cell
def _(constants, model_type_selector, np, pd, train_test_split, upload_widget):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from xgboost import XGBClassifier

    if upload_widget.value:
        import io

        _df = pd.read_csv(io.BytesIO(upload_widget.value[0].contents))
    else:
        _df = pd.read_csv("data/processed/cr_loan_w2.csv")

    _X = _df[constants.ALL_FEATURES].values.astype(np.float64)
    _y = _df[constants.TARGET_COLUMN].values.astype(np.int_)

    # Three-way split: train / calibration / test
    _X_trainval, X_test, _y_trainval, y_test = train_test_split(
        _X, _y, test_size=0.2, random_state=42, stratify=_y
    )
    X_train, X_cal, y_train, y_cal = train_test_split(
        _X_trainval, _y_trainval, test_size=0.25, random_state=42, stratify=_y_trainval
    )

    _factories = {
        "logistic_regression": lambda: LogisticRegression(
            **constants.LOGISTIC_REGRESSION_PARAMS  # type: ignore
        ),
        "xgboost": lambda: XGBClassifier(
            **constants.XGBOOST_PARAMS  # type: ignore
        ),
        "random_forest": lambda: RandomForestClassifier(
            **constants.RANDOM_FOREST_PARAMS  # type: ignore
        ),
    }
    base_model = _factories[model_type_selector.value]()
    base_model.fit(X_train, y_train)

    y_proba_uncal = base_model.predict_proba(X_test)[:, 1]
    return (
        X_cal,
        X_test,
        X_train,
        base_model,
        y_cal,
        y_proba_uncal,
        y_test,
        y_train,
    )


@app.cell
def _(mo):
    mo.md(
        """
        ## Calibration Curve (Reliability Diagram)

        The calibration curve plots predicted probability bins against the
        observed fraction of positives. A perfectly calibrated model follows
        the diagonal.
        """
    )
    return


@app.cell
def _(mo):
    bins_slider = mo.ui.slider(
        start=5, stop=30, step=1, value=10, label="Number of bins", show_value=True
    )
    bins_slider
    return (bins_slider,)


@app.cell
def _(
    bins_slider,
    brier_score_loss,
    constants,
    calculate_calibration_curve,
    go,
    y_proba_uncal,
    y_test,
):
    _cal_curve = calculate_calibration_curve(
        y_test, y_proba_uncal, n_bins=int(bins_slider.value)
    )
    brier_before = brier_score_loss(y_test, y_proba_uncal)

    fig_cal_before = go.Figure()
    fig_cal_before.add_trace(
        go.Scatter(
            x=_cal_curve.prob_pred,
            y=_cal_curve.prob_true,
            mode="lines+markers",
            name="Uncalibrated",
            line={"color": constants.COLOR_DANGER},
        )
    )
    fig_cal_before.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line={"dash": "dash", "color": "gray"},
            name="Perfectly calibrated",
        )
    )
    fig_cal_before.update_layout(
        title=f"Calibration Curve — Uncalibrated (Brier={brier_before:.4f})",
        xaxis_title="Mean Predicted Probability",
        yaxis_title="Fraction of Positives",
        height=500,
    )
    fig_cal_before
    return brier_before, fig_cal_before


@app.cell
def _(mo):
    mo.md(
        """
        ## Apply Calibration

        Two common post-hoc calibration methods:

        - **Platt scaling (sigmoid)**: fits a logistic regression on the
          model's output probabilities. Works well for models with sigmoid-
          shaped distortion.
        - **Isotonic regression**: non-parametric, fits a step-wise
          non-decreasing function. More flexible but can overfit with small
          calibration sets.
        """
    )
    return


@app.cell
def _(mo):
    method_selector = mo.ui.dropdown(
        options=["sigmoid", "isotonic"],
        value="sigmoid",
        label="Calibration method",
    )
    method_selector
    return (method_selector,)


@app.cell
def _(
    CalibratedClassifierCV,
    X_cal,
    X_test,
    base_model,
    method_selector,
    y_cal,
):
    calibrated_model = CalibratedClassifierCV(
        estimator=base_model,
        method=method_selector.value,
        cv="prefit",
    )
    calibrated_model.fit(X_cal, y_cal)
    y_proba_cal = calibrated_model.predict_proba(X_test)[:, 1]
    return calibrated_model, y_proba_cal


@app.cell
def _(mo):
    mo.md("## Before vs After Calibration")
    return


@app.cell
def _(
    bins_slider,
    brier_before,
    brier_score_loss,
    calculate_calibration_curve,
    constants,
    go,
    make_subplots,
    method_selector,
    y_proba_cal,
    y_proba_uncal,
    y_test,
):
    _n_bins = int(bins_slider.value)
    _cal_before = calculate_calibration_curve(y_test, y_proba_uncal, n_bins=_n_bins)
    _cal_after = calculate_calibration_curve(y_test, y_proba_cal, n_bins=_n_bins)
    brier_after = brier_score_loss(y_test, y_proba_cal)

    fig_compare = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=[
            f"Uncalibrated (Brier={brier_before:.4f})",
            f"{method_selector.value.title()} (Brier={brier_after:.4f})",
        ],
    )

    # Before
    fig_compare.add_trace(
        go.Scatter(
            x=_cal_before.prob_pred,
            y=_cal_before.prob_true,
            mode="lines+markers",
            name="Uncalibrated",
            line={"color": constants.COLOR_DANGER},
        ),
        row=1,
        col=1,
    )
    fig_compare.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line={"dash": "dash", "color": "gray"},
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # After
    fig_compare.add_trace(
        go.Scatter(
            x=_cal_after.prob_pred,
            y=_cal_after.prob_true,
            mode="lines+markers",
            name="Calibrated",
            line={"color": constants.COLOR_SUCCESS},
        ),
        row=1,
        col=2,
    )
    fig_compare.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line={"dash": "dash", "color": "gray"},
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    fig_compare.update_xaxes(title_text="Mean Predicted Probability")
    fig_compare.update_yaxes(title_text="Fraction of Positives")
    fig_compare.update_layout(height=500, title_text="Calibration Comparison")
    fig_compare
    return brier_after, fig_compare


@app.cell
def _(brier_after, brier_before, method_selector, mo):
    _improvement = brier_before - brier_after
    _direction = "improved" if _improvement > 0 else "worsened"
    mo.md(
        f"""
    ### Brier Score Summary

    | | Score |
    |---|---|
    | Uncalibrated | {brier_before:.4f} |
    | {method_selector.value.title()} | {brier_after:.4f} |
    | Change | {_improvement:+.4f} ({_direction}) |

    Lower Brier score = better calibration (0 = perfect).
    """
    )
    return


@app.cell
def _(mo):
    mo.md("## Calibrated Probability Distribution")
    return


@app.cell
def _(constants, go, make_subplots, y_proba_cal, y_proba_uncal):
    fig_dist = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Uncalibrated", "Calibrated"],
    )

    fig_dist.add_trace(
        go.Histogram(
            x=y_proba_uncal,
            nbinsx=50,
            marker_color=constants.COLOR_DANGER,
            opacity=0.7,
            name="Uncalibrated",
        ),
        row=1,
        col=1,
    )
    fig_dist.add_trace(
        go.Histogram(
            x=y_proba_cal,
            nbinsx=50,
            marker_color=constants.COLOR_SUCCESS,
            opacity=0.7,
            name="Calibrated",
        ),
        row=1,
        col=2,
    )

    fig_dist.update_xaxes(title_text="Predicted Probability")
    fig_dist.update_yaxes(title_text="Count")
    fig_dist.update_layout(
        height=400,
        title_text="Probability Distributions Before and After Calibration",
        showlegend=False,
    )
    fig_dist
    return (fig_dist,)


if __name__ == "__main__":
    app.run()
