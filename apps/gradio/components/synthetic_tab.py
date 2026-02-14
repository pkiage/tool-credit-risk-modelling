"""Synthetic data generation tab component for the Gradio app."""

import logging
from typing import Any

import httpx

import gradio as gr
from apps.gradio.api_client import CreditRiskAPI
from apps.gradio.components.training_tab import _build_roc_plot, _format_metrics_table
from shared.constants import (
    FEATURE_GROUP_LABELS,
    NUMERIC_FEATURES,
    SYNTHETIC_PRESETS,
)

logger = logging.getLogger(__name__)


def create_synthetic_tab(api: CreditRiskAPI, training_results_state: gr.State) -> None:
    """Create the synthetic data tab UI and wire up event handlers.

    Args:
        api: CreditRiskAPI client instance.
        training_results_state: Session-scoped gr.State holding training results.
    """
    preset_choices = list(SYNTHETIC_PRESETS.keys()) + ["Custom"]

    with gr.Row():
        # ── Left column: Generation config ──
        with gr.Column(scale=1):
            preset_dropdown = gr.Dropdown(
                choices=preset_choices,
                value="Custom",
                label="Preset",
            )
            n_samples = gr.Slider(
                minimum=100,
                maximum=50000,
                step=100,
                value=5000,
                label="Number of Samples",
            )
            default_rate = gr.Slider(
                minimum=0.01,
                maximum=0.99,
                step=0.01,
                value=0.22,
                label="Default Rate",
            )
            random_seed = gr.Number(value=42, precision=0, label="Random Seed")

            # Per-feature distribution overrides
            override_sliders: dict[str, tuple[gr.Slider, gr.Slider]] = {}
            with gr.Accordion("Distribution Overrides", open=False):
                for feature in NUMERIC_FEATURES:
                    label = FEATURE_GROUP_LABELS[feature]
                    with gr.Accordion(label, open=False):
                        mean_shift = gr.Slider(
                            minimum=-3.0,
                            maximum=3.0,
                            step=0.1,
                            value=0.0,
                            label=f"{label} — Mean Shift",
                        )
                        std_scale = gr.Slider(
                            minimum=0.1,
                            maximum=5.0,
                            step=0.1,
                            value=1.0,
                            label=f"{label} — Std Scale",
                        )
                        override_sliders[feature] = (mean_shift, std_scale)

            generate_btn = gr.Button("Generate Dataset", variant="primary")

        # ── Right column: Results ──
        with gr.Column(scale=2):
            dataset_id_display = gr.Textbox(label="Dataset ID", interactive=False)
            summary_table = gr.Dataframe(
                headers=["Feature", "Mean", "Std", "Min", "Max"],
                label="Summary Statistics",
                interactive=False,
            )
            status_display = gr.Textbox(
                label="Status", interactive=False, visible=False
            )

            gr.Markdown("### Train on This Dataset")
            synth_model_type = gr.Dropdown(
                choices=["logistic_regression", "xgboost", "random_forest"],
                value="logistic_regression",
                label="Model Type",
            )
            synth_test_size = gr.Slider(
                minimum=0.1,
                maximum=0.5,
                step=0.05,
                value=0.2,
                label="Test Size",
            )
            train_btn = gr.Button("Train on Synthetic", variant="secondary")
            train_metrics_table = gr.Dataframe(
                headers=["Metric", "Value"],
                label="Model Metrics",
                interactive=False,
            )
            train_roc_plot = gr.Plot(label="ROC Curve")
            train_status = gr.Textbox(label="Status", interactive=False, visible=False)

    # ── Event handlers ──

    def _apply_preset(preset_name: str) -> tuple[Any, ...]:
        """Update sliders when a preset is selected.

        Args:
            preset_name: Key from SYNTHETIC_PRESETS or "Custom".

        Returns:
            Updated values for n_samples, default_rate, and all override sliders.
        """
        if preset_name == "Custom" or preset_name not in SYNTHETIC_PRESETS:
            # Don't change anything
            return (gr.update(), gr.update())

        preset = SYNTHETIC_PRESETS[preset_name]
        return (
            gr.update(value=preset.get("n_samples", 5000)),
            gr.update(value=preset.get("default_rate", 0.22)),
        )

    preset_dropdown.change(
        fn=_apply_preset,
        inputs=[preset_dropdown],
        outputs=[n_samples, default_rate],
    )

    # Build generate inputs: base params + override slider pairs
    generate_inputs: list[Any] = [n_samples, default_rate, random_seed]
    for feature in NUMERIC_FEATURES:
        ms, ss = override_sliders[feature]
        generate_inputs.extend([ms, ss])

    generate_outputs: list[Any] = [dataset_id_display, summary_table, status_display]

    def _generate(
        n: int,
        dr: float,
        seed: float,
        *slider_values: Any,
    ) -> tuple[Any, ...]:
        """Handle generate button click.

        Args:
            n: Number of samples.
            dr: Default rate.
            seed: Random seed.
            *slider_values: Pairs of (mean_shift, std_scale) for each numeric feature.

        Returns:
            Updated dataset_id, summary table, and status display.
        """
        # Build distribution overrides from slider values
        distributions: list[dict[str, Any]] = []
        for i, feature in enumerate(NUMERIC_FEATURES):
            mean_shift_val = slider_values[i * 2]
            std_scale_val = slider_values[i * 2 + 1]
            if mean_shift_val != 0.0 or std_scale_val != 1.0:
                distributions.append(
                    {
                        "feature": feature,
                        "mean_shift": float(mean_shift_val),
                        "std_scale": float(std_scale_val),
                    }
                )

        config: dict[str, Any] = {
            "n_samples": int(n),
            "default_rate": float(dr),
            "random_seed": int(seed) if seed is not None else None,
        }
        if distributions:
            config["distributions"] = distributions

        try:
            result = api.generate_synthetic(config)
            dataset_id = result["dataset_id"]
            metadata = result["metadata"]
            summary_stats = metadata["summary_stats"]

            # Build summary table rows
            table_rows = []
            for fname in metadata["feature_names"]:
                if fname in summary_stats:
                    s = summary_stats[fname]
                    table_rows.append(
                        [
                            fname,
                            f"{s['mean']:.4f}",
                            f"{s['std']:.4f}",
                            f"{s['min']:.4f}",
                            f"{s['max']:.4f}",
                        ]
                    )

            return (
                dataset_id,
                table_rows,
                gr.update(visible=False, value=""),
            )
        except httpx.HTTPStatusError as exc:
            logger.exception("Synthetic generation HTTP error")
            status = exc.response.status_code
            if status == 401:
                msg = "Authentication failed. Please check your API key."
            elif status == 429:
                msg = "Rate limit exceeded. Please try again later."
            else:
                msg = f"Generation failed (HTTP {status}). Please try again."
            return (
                "",
                [],
                gr.update(visible=True, value=msg),
            )
        except httpx.TimeoutException:
            logger.warning("Synthetic generation timed out")
            return (
                "",
                [],
                gr.update(visible=True, value="Request timed out. Try fewer samples."),
            )
        except Exception:
            logger.exception("Synthetic generation failed")
            return (
                "",
                [],
                gr.update(
                    visible=True,
                    value="An unexpected error occurred. Please try again.",
                ),
            )

    generate_btn.click(
        fn=_generate,
        inputs=generate_inputs,
        outputs=generate_outputs,
    )

    # ── Train on synthetic dataset ──

    train_inputs: list[Any] = [
        dataset_id_display,
        synth_model_type,
        synth_test_size,
        training_results_state,
    ]

    train_outputs: list[Any] = [
        train_metrics_table,
        train_roc_plot,
        train_status,
        training_results_state,
    ]

    def _train_on_synthetic(
        dataset_id: str,
        model_type: str,
        test_size: float,
        training_results: dict[str, dict[str, Any]],
    ) -> tuple[Any, ...]:
        """Train a model on the generated synthetic dataset.

        Args:
            dataset_id: ID of the generated synthetic dataset.
            model_type: Model type to train.
            test_size: Test/train split ratio.
            training_results: Session state dict of training results.

        Returns:
            Updated metrics table, ROC plot, status, and state.
        """
        if not dataset_id:
            return (
                [],
                None,
                gr.update(
                    visible=True,
                    value="Generate a dataset first.",
                ),
                training_results,
            )

        try:
            config: dict[str, Any] = {
                "model_type": model_type,
                "test_size": test_size,
                "dataset_id": dataset_id,
            }
            result = api.train(config)

            # Store result in session state for comparison tab
            training_results[result["model_id"]] = result

            metrics = result["metrics"]
            table_data = _format_metrics_table(metrics)

            roc_fig = None
            if "roc_curve" in metrics:
                roc_fig = _build_roc_plot(metrics["roc_curve"], model_type)

            return (
                table_data,
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
                None,
                gr.update(visible=True, value=msg),
                training_results,
            )
        except Exception:
            logger.exception("Training on synthetic data failed")
            return (
                [],
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
        outputs=[train_status],
    ).then(
        fn=_train_on_synthetic,
        inputs=train_inputs,
        outputs=train_outputs,
    )
