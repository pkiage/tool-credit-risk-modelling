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

    api_healthy = api.health()
    if not api_healthy:
        gr.Markdown(
            "**Warning:** API not reachable at "
            f"`{API_BASE_URL}`. Start the API server first."
        )

    with gr.Tabs():
        with gr.Tab("Train"):
            create_training_tab(api)
        with gr.Tab("Predict"):
            create_prediction_tab(api)
        with gr.Tab("Compare"):
            create_comparison_tab(api)

if __name__ == "__main__":
    app.launch()
