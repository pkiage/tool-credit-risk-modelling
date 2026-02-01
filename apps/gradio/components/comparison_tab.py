"""Model comparison tab component for the Gradio app."""

import logging
from typing import Any

import plotly.graph_objects as go

import gradio as gr
from apps.gradio.api_client import CreditRiskAPI

logger = logging.getLogger(__name__)


def _get_model_choices(api: CreditRiskAPI) -> list[str]:
    """Fetch available model IDs from the API.

    Args:
        api: CreditRiskAPI client instance.

    Returns:
        List of model ID strings.
    """
    try:
        models = api.list_models()
        return [m["model_id"] for m in models]
    except Exception:
        logger.exception("Failed to fetch model list")
        return []


def _build_roc_overlay(
    selected_ids: list[str],
    training_results: dict[str, dict[str, Any]],
) -> go.Figure | None:
    """Build an overlay ROC plot for multiple models.

    Args:
        selected_ids: List of model IDs to compare.
        training_results: Session-scoped training results cache.

    Returns:
        Plotly Figure with overlaid ROC curves, or None on error.
    """
    fig = go.Figure()
    has_curves = False

    for model_id in selected_ids:
        result = training_results.get(model_id)
        if result is None:
            continue
        metrics = result.get("metrics", {})
        roc = metrics.get("roc_curve")
        if roc is None:
            continue
        model_type = result.get("model_type", model_id)
        auc = metrics.get("roc_auc", 0)
        fig.add_trace(
            go.Scatter(
                x=roc["fpr"],
                y=roc["tpr"],
                mode="lines",
                name=f"{model_type} (AUC={auc:.3f})",
            )
        )
        has_curves = True

    if not has_curves:
        return None

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
        title="ROC Curve Comparison",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        width=700,
        height=500,
    )
    return fig


def _build_metrics_bar(
    selected_ids: list[str],
    training_results: dict[str, dict[str, Any]],
) -> go.Figure | None:
    """Build a grouped bar chart comparing key metrics across models.

    Args:
        selected_ids: List of model IDs to compare.
        training_results: Session-scoped training results cache.

    Returns:
        Plotly Figure with grouped bars, or None if no data.
    """
    metric_names = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    traces = []

    for model_id in selected_ids:
        result = training_results.get(model_id)
        if result is None:
            continue
        metrics = result.get("metrics", {})
        model_type = result.get("model_type", model_id)
        values = [metrics.get(m, 0) for m in metric_names]
        traces.append(
            go.Bar(
                name=model_type,
                x=[m.replace("_", " ").title() for m in metric_names],
                y=values,
            )
        )

    if not traces:
        return None

    fig = go.Figure(data=traces)
    fig.update_layout(
        barmode="group",
        title="Metrics Comparison",
        yaxis_title="Score",
        width=700,
        height=450,
    )
    return fig


def _build_comparison_table(
    selected_ids: list[str],
    training_results: dict[str, dict[str, Any]],
) -> list[list[str]]:
    """Build a comparison table with rows per model and metric columns.

    Args:
        selected_ids: List of model IDs to compare.
        training_results: Session-scoped training results cache.

    Returns:
        List of rows: [model_type, accuracy, precision, recall, f1, roc_auc, threshold].
    """
    rows: list[list[str]] = []
    for model_id in selected_ids:
        result = training_results.get(model_id)
        if result is None:
            continue
        metrics = result.get("metrics", {})
        model_type = result.get("model_type", model_id)
        threshold = result.get("optimal_threshold", 0)
        rows.append(
            [
                model_type,
                f"{metrics.get('accuracy', 0):.4f}",
                f"{metrics.get('precision', 0):.4f}",
                f"{metrics.get('recall', 0):.4f}",
                f"{metrics.get('f1_score', 0):.4f}",
                f"{metrics.get('roc_auc', 0):.4f}",
                f"{threshold:.4f}",
            ]
        )
    return rows


def create_comparison_tab(api: CreditRiskAPI, training_results_state: gr.State) -> None:
    """Create the comparison tab UI and wire up event handlers.

    Args:
        api: CreditRiskAPI client instance.
        training_results_state: Session-scoped gr.State holding training results.
    """
    with gr.Row():
        model_multiselect = gr.Dropdown(
            choices=[],
            multiselect=True,
            label="Select Models to Compare",
            interactive=True,
        )
        refresh_btn = gr.Button("Refresh Models")

    roc_overlay = gr.Plot(label="ROC Curves")
    metrics_bar = gr.Plot(label="Metrics Comparison")
    comparison_table = gr.Dataframe(
        headers=[
            "Model",
            "Accuracy",
            "Precision",
            "Recall",
            "F1",
            "ROC-AUC",
            "Threshold",
        ],
        label="Metrics Table",
        interactive=False,
    )
    error_display = gr.Textbox(label="Status", interactive=False, visible=False)

    def _refresh() -> Any:
        """Refresh the model multiselect dropdown choices."""
        choices = _get_model_choices(api)
        return gr.update(choices=choices, value=[])

    def _compare(
        selected: list[str],
        training_results: dict[str, dict[str, Any]],
    ) -> tuple[go.Figure | None, go.Figure | None, list[list[str]], Any]:
        """Compare selected models.

        Args:
            selected: List of selected model IDs.
            training_results: Session-scoped training results cache.

        Returns:
            Tuple of (roc_figure, bar_figure, table_rows, error_update).
        """
        if not selected:
            return (
                None,
                None,
                [],
                gr.update(visible=True, value="Select at least one model to compare."),
            )

        # Check which models have cached results
        missing = [mid for mid in selected if mid not in training_results]
        if missing:
            return (
                None,
                None,
                [],
                gr.update(
                    visible=True,
                    value=(
                        f"No training data cached for: {', '.join(missing)}. "
                        "Models must be trained in this session to compare."
                    ),
                ),
            )

        roc_fig = _build_roc_overlay(selected, training_results)
        bar_fig = _build_metrics_bar(selected, training_results)
        table = _build_comparison_table(selected, training_results)

        return (roc_fig, bar_fig, table, gr.update(visible=False, value=""))

    refresh_btn.click(fn=_refresh, inputs=[], outputs=[model_multiselect])

    model_multiselect.change(
        fn=_compare,
        inputs=[model_multiselect, training_results_state],
        outputs=[roc_overlay, metrics_bar, comparison_table, error_display],
    )
