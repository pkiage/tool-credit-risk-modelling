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
app = marimo.App(width="medium", app_title="Credit Risk — Model Comparison")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Model Training & Comparison

        Train multiple credit risk models and compare their performance
        side-by-side with ROC curves, precision-recall curves, and feature
        importance.
        """
    )
    return


@app.cell
def _():
    import uuid

    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from xgboost import XGBClassifier

    from shared import constants
    from shared.logic.evaluation import evaluate_model
    from shared.logic.preprocessing import undersample_majority_class
    from shared.schemas.training import TrainingConfig, TrainingResult

    return (
        LogisticRegression,
        RandomForestClassifier,
        TrainingConfig,
        TrainingResult,
        XGBClassifier,
        constants,
        evaluate_model,
        go,
        make_subplots,
        np,
        pd,
        px,
        train_test_split,
        undersample_majority_class,
        uuid,
    )


@app.cell
def _(mo):
    mo.md("## Configuration")
    return


@app.cell
def _(mo):
    upload_widget = mo.ui.file(
        filetypes=[".csv"],
        label="Upload custom CSV (optional — uses default dataset if empty)",
    )
    upload_widget
    return (upload_widget,)


@app.cell
def _(constants, mo):
    model_selector = mo.ui.multiselect(
        options=constants.MODEL_TYPES,
        value=constants.MODEL_TYPES,
        label="Models to train",
    )
    test_size_slider = mo.ui.slider(
        start=0.1, stop=0.5, step=0.05, value=0.2, label="Test size"
    )
    random_state_input = mo.ui.number(
        start=0, stop=9999, value=42, label="Random state"
    )
    undersample_toggle = mo.ui.switch(value=False, label="Undersample majority class")

    mo.hstack(
        [model_selector, test_size_slider, random_state_input, undersample_toggle],
        wrap=True,
    )
    return (
        model_selector,
        random_state_input,
        test_size_slider,
        undersample_toggle,
    )


@app.cell
def _(mo):
    train_button = mo.ui.run_button(label="Train models")
    train_button
    return (train_button,)


@app.cell
def _(
    LogisticRegression,
    RandomForestClassifier,
    TrainingConfig,
    TrainingResult,
    XGBClassifier,
    constants,
    evaluate_model,
    model_selector,
    np,
    pd,
    random_state_input,
    test_size_slider,
    train_button,
    train_test_split,
    undersample_majority_class,
    undersample_toggle,
    upload_widget,
    uuid,
):
    # Only run when button is pressed
    train_button.value

    _models_to_train = model_selector.value
    if not _models_to_train:
        results: dict[str, TrainingResult] = {}
        models_trained: dict[str, object] = {}
        X_test_arr = np.array([])
        y_test_arr = np.array([])
        probas: dict[str, np.ndarray] = {}
    else:
        if upload_widget.value:
            import io

            _df = pd.read_csv(io.BytesIO(upload_widget.value[0].contents))
        else:
            _df = pd.read_csv("data/processed/cr_loan_w2.csv")
        _X = _df[constants.ALL_FEATURES].values.astype(np.float64)
        _y = _df[constants.TARGET_COLUMN].values.astype(np.int_)

        _X_train, X_test_arr, _y_train, y_test_arr = train_test_split(
            _X,
            _y,
            test_size=test_size_slider.value,
            random_state=int(random_state_input.value),
            stratify=_y,
        )

        if undersample_toggle.value:
            _X_train, _y_train = undersample_majority_class(
                _X_train, _y_train, random_state=int(random_state_input.value)
            )

        _model_factories = {
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

        results = {}
        models_trained = {}
        probas = {}
        for _mt in _models_to_train:
            _model = _model_factories[_mt]()
            _model.fit(_X_train, _y_train)
            _y_proba = _model.predict_proba(X_test_arr)[:, 1]

            _metrics = evaluate_model(y_test_arr, _y_proba)

            _feat_imp = None
            if hasattr(_model, "feature_importances_"):
                _feat_imp = {
                    f: float(v)
                    for f, v in zip(constants.ALL_FEATURES, _model.feature_importances_)
                }

            _config = TrainingConfig(
                model_type=_mt,
                test_size=test_size_slider.value,
                random_state=int(random_state_input.value),
                undersample=undersample_toggle.value,
            )
            results[_mt] = TrainingResult(
                model_id=f"model_{uuid.uuid4().hex[:8]}",
                model_type=_mt,
                metrics=_metrics,
                optimal_threshold=_metrics.threshold_analysis.threshold,
                feature_importance=_feat_imp,
                training_config=_config,
            )
            models_trained[_mt] = _model
            probas[_mt] = _y_proba

    return X_test_arr, models_trained, probas, results, y_test_arr


@app.cell
def _(mo):
    mo.md("## Metrics Comparison")
    return


@app.cell
def _(mo, pd, results):
    if not results:
        mo.md("_Press **Train models** to see results._")
    else:
        _rows = []
        for _mt, _r in results.items():
            _m = _r.metrics
            _rows.append(
                {
                    "Model": _mt,
                    "Accuracy": f"{_m.accuracy:.4f}",
                    "Precision": f"{_m.precision:.4f}",
                    "Recall": f"{_m.recall:.4f}",
                    "F1": f"{_m.f1_score:.4f}",
                    "ROC AUC": f"{_m.roc_auc:.4f}",
                    "Threshold": f"{_r.optimal_threshold:.3f}",
                }
            )
        mo.ui.table(pd.DataFrame(_rows), selection=None)
    return


@app.cell
def _(mo):
    mo.md("## ROC Curves")
    return


@app.cell
def _(go, results):
    fig_roc = go.Figure()

    for _mt, _r in results.items():
        _roc = _r.metrics.roc_curve
        fig_roc.add_trace(
            go.Scatter(
                x=_roc.fpr,
                y=_roc.tpr,
                mode="lines",
                name=f"{_mt} (AUC={_r.metrics.roc_auc:.3f})",
            )
        )

    fig_roc.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            line={"dash": "dash", "color": "gray"},
            name="Random",
            showlegend=True,
        )
    )
    fig_roc.update_layout(
        title="ROC Curves",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=500,
    )
    fig_roc
    return (fig_roc,)


@app.cell
def _(mo):
    mo.md("## Precision-Recall Curves")
    return


@app.cell
def _(go, np, probas, y_test_arr):
    from sklearn.metrics import precision_recall_curve

    fig_pr = go.Figure()

    for _mt, _yp in probas.items():
        if len(_yp) == 0:
            continue
        _prec, _rec, _ = precision_recall_curve(y_test_arr, _yp)
        fig_pr.add_trace(go.Scatter(x=_rec, y=_prec, mode="lines", name=_mt))

    # Baseline = prevalence
    if len(y_test_arr) > 0:
        _prevalence = float(np.mean(y_test_arr))
        fig_pr.add_shape(
            type="line",
            x0=0,
            x1=1,
            y0=_prevalence,
            y1=_prevalence,
            line={"dash": "dash", "color": "gray"},
        )

    fig_pr.update_layout(
        title="Precision-Recall Curves",
        xaxis_title="Recall",
        yaxis_title="Precision",
        height=500,
    )
    fig_pr
    return (fig_pr, precision_recall_curve)


@app.cell
def _(mo):
    mo.md("## Feature Importance")
    return


@app.cell
def _(go, make_subplots, results):
    _with_imp = {mt: r for mt, r in results.items() if r.feature_importance is not None}

    if _with_imp:
        _n = len(_with_imp)
        fig_imp = make_subplots(
            rows=1,
            cols=_n,
            subplot_titles=list(_with_imp.keys()),
            shared_yaxes=True,
        )

        for _i, (_mt, _r) in enumerate(_with_imp.items()):
            _sorted = sorted(
                _r.feature_importance.items(), key=lambda x: x[1], reverse=True
            )[:15]
            _names = [s[0] for s in _sorted][::-1]
            _vals = [s[1] for s in _sorted][::-1]
            fig_imp.add_trace(
                go.Bar(x=_vals, y=_names, orientation="h", name=_mt),
                row=1,
                col=_i + 1,
            )

        fig_imp.update_layout(
            height=600,
            title_text="Top 15 Feature Importances",
            showlegend=False,
        )
        fig_imp
    else:
        fig_imp = go.Figure()
    return (fig_imp,)


if __name__ == "__main__":
    app.run()
