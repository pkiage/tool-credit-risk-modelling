"""Training tab component for the Gradio app."""

import logging
from typing import Any

import httpx
import plotly.graph_objects as go

import gradio as gr
from apps.gradio.api_client import CreditRiskAPI
from shared.constants import (
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_GROUP_LABELS,
    FEATURE_GROUPS,
    NUMERIC_FEATURES,
)

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


def _build_importance_plot(feature_importance: dict[str, float]) -> go.Figure:
    """Build a horizontal bar chart of feature importance.

    Args:
        feature_importance: Mapping of feature name to importance score.

    Returns:
        Plotly Figure with horizontal bars sorted by importance.
    """
    sorted_items = sorted(feature_importance.items(), key=lambda x: abs(x[1]))
    names = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker_color="#636EFA",
        )
    )
    fig.update_layout(
        title="Feature Importance",
        xaxis_title="Importance",
        height=max(400, len(names) * 25),
        width=600,
        margin={"l": 200},
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


def _column_display_name(col: str, group: str) -> str:
    """Extract the human-readable suffix from a one-hot encoded column name.

    Args:
        col: Full encoded column name (e.g. "person_home_ownership_RENT").
        group: Feature group name (e.g. "person_home_ownership").

    Returns:
        Suffix portion of the column name (e.g. "RENT").
    """
    prefix = f"{group}_"
    return col[len(prefix) :] if col.startswith(prefix) else col


def create_training_tab(api: CreditRiskAPI, training_results_state: gr.State) -> None:
    """Create the training tab UI and wire up event handlers.

    Args:
        api: CreditRiskAPI client instance.
        training_results_state: Session-scoped gr.State holding training results.
    """
    with gr.Row():
        with gr.Column(scale=1):
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

            gr.Markdown("### Feature Selection")

            # --- Auto Feature Selection ---
            with gr.Accordion("Auto Feature Selection", open=False):
                gr.Markdown(
                    "Run an algorithm to recommend features, "
                    "then apply the result to the checkboxes below."
                )
                fs_method = gr.Dropdown(
                    choices=[
                        ("Tree Importance (RF / XGB)", "tree_importance"),
                        ("LASSO (L1 Regularization)", "lasso"),
                        ("WoE / IV (Information Value)", "woe_iv"),
                        ("Boruta (All-Relevant)", "boruta"),
                        ("SHAP (Explainability)", "shap"),
                    ],
                    value="tree_importance",
                    label="Method",
                )

                # -- Tree Importance params --
                with gr.Column(visible=True) as fs_tree_group:
                    fs_tree_model = gr.Dropdown(
                        choices=[
                            ("Random Forest", "random_forest"),
                            ("XGBoost", "xgboost"),
                        ],
                        value="random_forest",
                        label="Model Type",
                    )
                    fs_tree_top_k = gr.Slider(
                        minimum=1,
                        maximum=26,
                        step=1,
                        value=10,
                        label="Top K Features",
                    )

                # -- LASSO params --
                with gr.Column(visible=False) as fs_lasso_group:
                    fs_lasso_c = gr.Slider(
                        minimum=0.01,
                        maximum=10,
                        step=0.01,
                        value=1.0,
                        label="Regularization (C) — lower = fewer features",
                    )

                # -- WoE/IV params --
                with gr.Column(visible=False) as fs_woe_group:
                    fs_woe_bins = gr.Slider(
                        minimum=5, maximum=20, step=1, value=10, label="Bins"
                    )
                    fs_woe_threshold = gr.Slider(
                        minimum=0,
                        maximum=0.5,
                        step=0.01,
                        value=0.1,
                        label="IV Threshold",
                    )
                    gr.Markdown(
                        "<0.02 useless · 0.02-0.1 weak · "
                        "0.1-0.3 medium · 0.3-0.5 strong · >0.5 suspicious"
                    )

                # -- Boruta params --
                with gr.Column(visible=False) as fs_boruta_group:
                    fs_boruta_iters = gr.Slider(
                        minimum=20,
                        maximum=200,
                        step=10,
                        value=100,
                        label="Iterations",
                    )
                    fs_boruta_tentative = gr.Checkbox(
                        value=False, label="Include tentative features"
                    )

                # -- SHAP params --
                with gr.Column(visible=False) as fs_shap_group:
                    fs_shap_model = gr.Dropdown(
                        choices=[
                            ("XGBoost", "xgboost"),
                            ("Random Forest", "random_forest"),
                        ],
                        value="xgboost",
                        label="Model Type",
                    )
                    fs_shap_top_k = gr.Slider(
                        minimum=1,
                        maximum=26,
                        step=1,
                        value=10,
                        label="Top K Features",
                    )

                fs_run_btn = gr.Button("Run Feature Selection", variant="secondary")
                fs_status = gr.Textbox(label="Status", interactive=False, visible=False)
                fs_plot = gr.Plot(label="Feature Scores")
                fs_result_state = gr.State(value=None)
                fs_apply_btn = gr.Button(
                    "Apply to Training", variant="primary", visible=False
                )

            # Numeric features — each maps to a single encoded column
            numeric_choices = [(FEATURE_GROUP_LABELS[f], f) for f in NUMERIC_FEATURES]
            numeric_group = gr.CheckboxGroup(
                choices=numeric_choices,
                value=list(NUMERIC_FEATURES),
                label="Numeric Features",
            )

            # Categorical features — each has multiple one-hot columns
            cat_col_groups: list[gr.CheckboxGroup] = []
            cat_select_alls: list[gr.Checkbox] = []
            cat_all_cols: list[list[str]] = []

            for cat_name in CATEGORICAL_FEATURES:
                label = FEATURE_GROUP_LABELS[cat_name]
                columns = FEATURE_GROUPS[cat_name]
                col_choices = [(_column_display_name(c, cat_name), c) for c in columns]
                with gr.Accordion(label, open=False):
                    select_all = gr.Checkbox(value=True, label="Select All")
                    col_group = gr.CheckboxGroup(
                        choices=col_choices,
                        value=list(columns),
                        label=f"{label} Columns",
                    )
                cat_select_alls.append(select_all)
                cat_col_groups.append(col_group)
                cat_all_cols.append(list(columns))

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
            importance_plot = gr.Plot(label="Feature Importance")
            error_display = gr.Textbox(label="Status", interactive=False, visible=False)

    # --- Auto Feature Selection event handlers ---

    def _switch_fs_params(method: str) -> tuple[Any, ...]:
        """Toggle visibility of method-specific parameter groups."""
        return (
            gr.update(visible=method == "tree_importance"),
            gr.update(visible=method == "lasso"),
            gr.update(visible=method == "woe_iv"),
            gr.update(visible=method == "boruta"),
            gr.update(visible=method == "shap"),
        )

    fs_method.change(
        fn=_switch_fs_params,
        inputs=[fs_method],
        outputs=[
            fs_tree_group,
            fs_lasso_group,
            fs_woe_group,
            fs_boruta_group,
            fs_shap_group,
        ],
    )

    def _run_fs(
        method: str,
        tree_model: str,
        tree_k: int,
        lasso_c: float,
        woe_bins: int,
        woe_thresh: float,
        boruta_iters: int,
        boruta_tent: bool,
        shap_model: str,
        shap_k: int,
    ) -> tuple[Any, ...]:
        """Call the feature-selection API and return results + chart."""
        request: dict[str, Any] = {"method": method}
        if method == "tree_importance":
            request["tree_params"] = {"model_type": tree_model, "top_k": int(tree_k)}
        elif method == "lasso":
            request["lasso_params"] = {"C": lasso_c}
        elif method == "woe_iv":
            request["woe_iv_params"] = {
                "n_bins": int(woe_bins),
                "iv_threshold": woe_thresh,
            }
        elif method == "boruta":
            request["boruta_params"] = {
                "n_iterations": int(boruta_iters),
                "include_tentative": boruta_tent,
            }
        elif method == "shap":
            request["shap_params"] = {"model_type": shap_model, "top_k": int(shap_k)}

        try:
            result = api.feature_selection(request)
        except httpx.HTTPStatusError as exc:
            logger.exception("Feature selection HTTP error")
            msg = f"API error {exc.response.status_code}"
            return (
                gr.update(visible=True, value=msg),
                None,
                None,
                gr.update(visible=False),
            )
        except Exception:
            logger.exception("Feature selection failed")
            return (
                gr.update(visible=True, value="Feature selection failed."),
                None,
                None,
                gr.update(visible=False),
            )

        # Build chart (top 15 for readability)
        scores = sorted(result["feature_scores"], key=lambda s: s["rank"])[:15]
        names = [s["feature_name"] for s in reversed(scores)]
        vals = [s["score"] for s in reversed(scores)]
        colors = ["#636EFA" if s["selected"] else "#CCCCCC" for s in reversed(scores)]

        fig = go.Figure(go.Bar(x=vals, y=names, orientation="h", marker_color=colors))
        method_label = method.replace("_", " ").title()
        fig.update_layout(
            title=f"Top Features — {method_label}",
            xaxis_title="Score",
            height=max(350, len(scores) * 28),
            margin={"l": 200},
        )

        status = f"Selected {result['n_selected']} of {result['n_total']} features"
        return (
            gr.update(visible=True, value=status),
            fig,
            result,
            gr.update(visible=True),
        )

    fs_run_btn.click(
        fn=_run_fs,
        inputs=[
            fs_method,
            fs_tree_model,
            fs_tree_top_k,
            fs_lasso_c,
            fs_woe_bins,
            fs_woe_threshold,
            fs_boruta_iters,
            fs_boruta_tentative,
            fs_shap_model,
            fs_shap_top_k,
        ],
        outputs=[fs_status, fs_plot, fs_result_state, fs_apply_btn],
    )

    def _apply_fs(
        result: dict[str, Any] | None,
    ) -> tuple[Any, ...]:
        """Transfer selected features into the manual checkboxes."""
        if not result:
            defaults = [list(FEATURE_GROUPS[c]) for c in CATEGORICAL_FEATURES]
            return (list(NUMERIC_FEATURES), *defaults)
        selected = set(result["selected_features"])
        numeric_sel = [f for f in NUMERIC_FEATURES if f in selected]
        cat_sels = [
            [c for c in FEATURE_GROUPS[cat] if c in selected]
            for cat in CATEGORICAL_FEATURES
        ]
        return (numeric_sel, *cat_sels)

    fs_apply_btn.click(
        fn=_apply_fs,
        inputs=[fs_result_state],
        outputs=[numeric_group, *cat_col_groups],
    )

    # Wire up Select All ↔ column toggle events for each categorical group.
    # Uses .input() for Select All to avoid event loops: .input() fires only
    # on direct user interaction, not programmatic updates.
    for i in range(len(CATEGORICAL_FEATURES)):
        select_all_cb = cat_select_alls[i]
        col_group_cb = cat_col_groups[i]
        all_cols = cat_all_cols[i]

        def _toggle_all(checked: bool, cols: list[str] = all_cols) -> list[str]:
            """Check or uncheck all columns when Select All is toggled."""
            return cols if checked else []

        def _sync_select_all(selected: list[str], cols: list[str] = all_cols) -> bool:
            """Update Select All checkbox to reflect column selection state."""
            return len(selected) == len(cols)

        select_all_cb.input(
            fn=_toggle_all, inputs=[select_all_cb], outputs=[col_group_cb]
        )
        col_group_cb.change(
            fn=_sync_select_all, inputs=[col_group_cb], outputs=[select_all_cb]
        )

    # Build train inputs: model config + numeric features + categorical columns + state
    train_inputs: list[Any] = [
        model_type,
        test_size,
        numeric_group,
        *cat_col_groups,
        training_results_state,
    ]

    train_outputs: list[Any] = [
        metrics_table,
        threshold_display,
        training_time_display,
        model_id_display,
        roc_plot,
        importance_plot,
        error_display,
        training_results_state,
    ]

    def _train(
        selected_model_type: str,
        selected_test_size: float,
        numeric_selected: list[str],
        *args: Any,
    ) -> tuple[Any, ...]:
        """Handle train button click.

        Args:
            selected_model_type: Model type from dropdown.
            selected_test_size: Test/train split ratio.
            numeric_selected: Selected numeric feature group names.
            *args: Categorical column selections (one list per group) followed
                by the training_results state dict as the last element.

        Returns:
            Tuple of updated component values and updated state.
        """
        # Last arg is training_results state; rest are categorical column selections
        training_results: dict[str, dict[str, Any]] = args[-1]
        cat_selections = args[:-1]

        # Collect all selected encoded column names
        selected_features: list[str] = list(numeric_selected)
        for sel in cat_selections:
            selected_features.extend(sel)

        if not selected_features:
            return (
                [],
                "",
                "",
                "",
                None,
                None,
                gr.update(
                    visible=True,
                    value="Please select at least one feature to train on.",
                ),
                training_results,
            )

        # Send None when all features are selected (backward compatible)
        features_param = (
            selected_features if len(selected_features) < len(ALL_FEATURES) else None
        )

        try:
            config: dict[str, Any] = {
                "model_type": selected_model_type,
                "test_size": selected_test_size,
            }
            if features_param is not None:
                config["selected_features"] = features_param

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

            importance_fig = None
            if result.get("feature_importance"):
                importance_fig = _build_importance_plot(result["feature_importance"])

            return (
                table_data,
                f"{threshold:.4f}",
                f"{train_time:.3f}s",
                model_id,
                roc_fig,
                importance_fig,
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
        inputs=train_inputs,
        outputs=train_outputs,
    )
