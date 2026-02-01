"""Gradio stakeholder demo for credit risk modeling."""

import gradio as gr
from apps.gradio.api_client import CreditRiskAPI
from apps.gradio.components.comparison_tab import create_comparison_tab
from apps.gradio.components.prediction_tab import create_prediction_tab
from apps.gradio.components.training_tab import create_training_tab
from apps.gradio.config import API_BASE_URL, APP_TITLE

api = CreditRiskAPI(API_BASE_URL)

with gr.Blocks(title=APP_TITLE) as app:
    gr.Markdown(f"# {APP_TITLE}")

    # Session-scoped state for training results (isolated per user session).
    training_results_state = gr.State(value={})

    # Dynamic health banner — checked on each page load, not just at startup.
    api_status = gr.Markdown(visible=False)

    with gr.Tabs():
        with gr.Tab("Train"):
            create_training_tab(api, training_results_state)
        with gr.Tab("Predict"):
            create_prediction_tab(api)
        with gr.Tab("Compare"):
            create_comparison_tab(api, training_results_state)

    def _check_health() -> Any:
        """Check API health and return a visible warning if unreachable."""
        if api.health():
            return gr.update(visible=False, value="")
        return gr.update(
            visible=True,
            value=(
                f"**Warning:** API not reachable at "
                f"`{API_BASE_URL}`. Start the API server first."
            ),
        )

    app.load(fn=_check_health, inputs=[], outputs=[api_status])

if __name__ == "__main__":
    app.launch()
