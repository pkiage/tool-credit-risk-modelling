"""Training tab component for the Gradio app."""

import logging
from typing import Any

import httpx
import plotly.graph_objects as go

import gradio as gr
from apps.gradio.api_client import CreditRiskAPI

logger = logging.getLogger(__name__)


def _build_roc_plot(roc_data: dict[str, Any], model_type: str) -> go.Figure:
    """Build a Plotly ROC curve figure from API response data.

    Args:
        roc_data: ROC curve data with fpr, tpr, and thresholds.
        model_type: Name of the model for the legend.

    Returns:
        Plotly Figure with the ROC curve.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=roc_data["fpr"],
            y=roc_data["tpr"],
            mode="lines",
            name=f"{model_type} (ROC)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Random",
            line={"dash": "dash", "color": "gray"},
        )
    )
    fig.update_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        width=600,
        height=450,
    )
    return fig


def _format_metrics_table(metrics: dict[str, Any]) -> list[list[str]]:
    """Format model metrics into a table rows list.

    Args:
        metrics: ModelMetrics dictionary from the API.

    Returns:
        List of [metric_name, value] rows.
    """
    return [
        ["Accuracy", f"{metrics['accuracy']:.4f}"],
        ["Precision", f"{metrics['precision']:.4f}"],
        ["Recall", f"{metrics['recall']:.4f}"],
        ["F1 Score", f"{metrics['f1_score']:.4f}"],
        ["ROC-AUC", f"{metrics['roc_auc']:.4f}"],
    ]


def create_training_tab(api: CreditRiskAPI, training_results_state: gr.State) -> None:
    """Create the training tab UI and wire up event handlers.

    Args:
        api: CreditRiskAPI client instance.
        training_results_state: Session-scoped gr.State holding training results.
    """
    with gr.Row():
        with gr.Column(scale=1):
            # Model types match shared.constants.MODEL_HYPERPARAMETERS keys.
            # Update here if new model types are added to shared/.
            model_type = gr.Dropdown(
                choices=["logistic_regression", "xgboost", "random_forest"],
                value="logistic_regression",
                label="Model Type",
            )
            test_size = gr.Slider(
                minimum=0.1,
                maximum=0.5,
                step=0.05,
                value=0.2,
                label="Test Size",
            )
            train_btn = gr.Button("Train Model", variant="primary")

        with gr.Column(scale=2):
            metrics_table = gr.Dataframe(
                headers=["Metric", "Value"],
                label="Model Metrics",
                interactive=False,
            )
            threshold_display = gr.Textbox(label="Optimal Threshold", interactive=False)
            training_time_display = gr.Textbox(label="Training Time", interactive=False)
            model_id_display = gr.Textbox(label="Model ID", interactive=False)
            roc_plot = gr.Plot(label="ROC Curve")
            error_display = gr.Textbox(label="Status", interactive=False, visible=False)

    def _train(
        selected_model_type: str,
        selected_test_size: float,
        training_results: dict[str, dict[str, Any]],
    ) -> tuple[
        Any,  # metrics_table
        str,  # threshold_display
        str,  # training_time_display
        str,  # model_id_display
        go.Figure | None,  # roc_plot
        Any,  # error_display update
        dict[str, dict[str, Any]],  # updated training_results_state
    ]:
        """Handle train button click.

        Args:
            selected_model_type: Model type from dropdown.
            selected_test_size: Test/train split ratio.
            training_results: Session-scoped training results cache.

        Returns:
            Tuple of updated component values and updated state.
        """
        try:
            config = {
                "model_type": selected_model_type,
                "test_size": selected_test_size,
            }
            result = api.train(config)

            # Store result in session state for comparison tab
            training_results[result["model_id"]] = result

            metrics = result["metrics"]
            table_data = _format_metrics_table(metrics)
            threshold = result["optimal_threshold"]
            train_time = result.get("training_time_seconds", 0)
            model_id = result["model_id"]

            roc_fig = None
            if "roc_curve" in metrics:
                roc_fig = _build_roc_plot(metrics["roc_curve"], selected_model_type)

            return (
                table_data,
                f"{threshold:.4f}",
                f"{train_time:.3f}s",
                model_id,
                roc_fig,
                gr.update(visible=False, value=""),
                training_results,
            )
        except httpx.HTTPStatusError as exc:
            logger.exception("Training HTTP error")
            status = exc.response.status_code
            if status == 401:
                msg = "Authentication failed. Please check your API key."
            elif status == 429:
                msg = "Rate limit exceeded. Please try again later."
            else:
                msg = "Training request failed. Please try again."
            return (
                [],
                "",
                "",
                "",
                None,
                gr.update(visible=True, value=msg),
                training_results,
            )
        except Exception:
            logger.exception("Training request failed")
            return (
                [],
                "",
                "",
                "",
                None,
                gr.update(
                    visible=True,
                    value="An unexpected error occurred. Please try again.",
                ),
                training_results,
            )

    def _show_training_status() -> Any:
        """Show a loading message while training is in progress."""
        return gr.update(visible=True, value="Training in progress\u2026")

    train_btn.click(
        fn=_show_training_status,
        inputs=[],
        outputs=[error_display],
    ).then(
        fn=_train,
        inputs=[model_type, test_size, training_results_state],
        outputs=[
            metrics_table,
            threshold_display,
            training_time_display,
            model_id_display,
            roc_plot,
            error_display,
            training_results_state,
        ],
    )
