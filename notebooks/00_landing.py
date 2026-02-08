# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="medium", app_title="Credit Risk Platform")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Credit Risk Modeling Platform

        Interactive notebooks for exploring credit risk data, training models,
        and optimizing decision thresholds.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Notebooks

        ### [📊 Exploratory Data Analysis](/01_eda)
        Dataset overview, feature distributions, correlation analysis,
        and target variable exploration.

        ### [🤖 Model Comparison](/02_model_comparison)
        Train and compare multiple classification models
        (Logistic Regression, XGBoost, Random Forest) side-by-side
        with ROC curves and feature importance.

        ### [⚖️ Threshold Optimization](/03_threshold_optimization)
        Interactive threshold tuning using Youden's J statistic
        with sensitivity vs specificity trade-offs
        and cost-based optimization.

        ### [📈 Probability Calibration](/04_calibration)
        Evaluate model calibration with reliability diagrams,
        Brier scores, and compare sigmoid vs isotonic
        calibration methods.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ---

        **Live Demo**: [huggingface.co/spaces/pkiage/credit-risk-notebooks](https://huggingface.co/spaces/pkiage/credit-risk-notebooks)
        """
    )
    return


if __name__ == "__main__":
    app.run()
