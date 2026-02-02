"""Prediction tab component for the Gradio app."""

import logging
from typing import Any

import httpx

import gradio as gr
from apps.gradio.api_client import CreditRiskAPI

logger = logging.getLogger(__name__)


def _refresh_model_choices(api: CreditRiskAPI) -> list[str]:
    """Fetch trained model IDs from the API.

    Args:
        api: CreditRiskAPI client instance.

    Returns:
        List of model ID strings, or empty list on error.
    """
    try:
        models = api.list_models()
        return [m["model_id"] for m in models]
    except Exception:
        logger.exception("Failed to fetch model list")
        return []


def create_prediction_tab(api: CreditRiskAPI) -> None:
    """Create the prediction tab UI and wire up event handlers.

    Args:
        api: CreditRiskAPI client instance.
    """
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Loan Application")
            person_age = gr.Number(label="Age", value=25, minimum=18, maximum=120)
            person_income = gr.Number(label="Annual Income ($)", value=50000, minimum=1)
            person_emp_length = gr.Number(
                label="Employment Length (years)", value=3, minimum=0
            )
            loan_amnt = gr.Number(label="Loan Amount ($)", value=10000, minimum=1)
            loan_int_rate = gr.Number(
                label="Interest Rate (%)", value=10.5, minimum=0.01, maximum=100
            )
            loan_percent_income = gr.Number(
                label="Loan % of Income", value=0.2, minimum=0, maximum=1
            )
            cb_person_cred_hist_length = gr.Number(
                label="Credit History Length (years)", value=5, minimum=0
            )
            person_home_ownership = gr.Dropdown(
                choices=["RENT", "OWN", "MORTGAGE", "OTHER"],
                value="RENT",
                label="Home Ownership",
            )
            loan_intent = gr.Dropdown(
                choices=[
                    "EDUCATION",
                    "MEDICAL",
                    "VENTURE",
                    "PERSONAL",
                    "DEBTCONSOLIDATION",
                    "HOMEIMPROVEMENT",
                ],
                value="EDUCATION",
                label="Loan Intent",
            )
            loan_grade = gr.Dropdown(
                choices=["A", "B", "C", "D", "E", "F", "G"],
                value="B",
                label="Loan Grade",
            )
            cb_default = gr.Dropdown(
                choices=["Y", "N"], value="N", label="Previous Default on File"
            )

        with gr.Column(scale=1):
            gr.Markdown("### Model & Prediction")
            model_selector = gr.Dropdown(
                choices=[],
                label="Select Model",
                interactive=True,
            )
            refresh_btn = gr.Button("Refresh Models")
            predict_btn = gr.Button("Predict", variant="primary")

            prediction_result = gr.Textbox(label="Prediction", interactive=False)
            probability_display = gr.Textbox(
                label="Default Probability", interactive=False
            )
            threshold_display = gr.Textbox(label="Threshold Used", interactive=False)
            error_display = gr.Textbox(label="Status", interactive=False, visible=False)

    def _refresh() -> Any:
        """Refresh the model selector dropdown choices."""
        choices = _refresh_model_choices(api)
        return gr.update(choices=choices, value=choices[0] if choices else None)

    def _predict(
        model_id: str | None,
        age: float,
        income: float,
        emp_length: float,
        amount: float,
        int_rate: float,
        pct_income: float,
        cred_hist: float,
        home: str,
        intent: str,
        grade: str,
        default_on_file: str,
    ) -> tuple[str, str, str, Any]:
        """Handle predict button click.

        Args:
            model_id: Selected model identifier.
            age: Applicant age.
            income: Annual income.
            emp_length: Employment length in years.
            amount: Loan amount.
            int_rate: Interest rate percentage.
            pct_income: Loan as fraction of income.
            cred_hist: Credit history length.
            home: Home ownership status.
            intent: Loan purpose.
            grade: Loan grade.
            default_on_file: Previous default indicator.

        Returns:
            Tuple of (prediction_text, probability_text, threshold_text, error_update).
        """
        if not model_id:
            return (
                "",
                "",
                "",
                gr.update(
                    visible=True,
                    value="No model selected. Train a model first, then refresh.",
                ),
            )

        try:
            request = {
                "model_id": model_id,
                "applications": [
                    {
                        "person_age": int(age),
                        "person_income": float(income),
                        "person_emp_length": float(emp_length),
                        "loan_amnt": float(amount),
                        "loan_int_rate": float(int_rate),
                        "loan_percent_income": float(pct_income),
                        "cb_person_cred_hist_length": int(cred_hist),
                        "person_home_ownership": home,
                        "loan_intent": intent,
                        "loan_grade": grade,
                        "cb_person_default_on_file": default_on_file,
                    }
                ],
                "include_probabilities": True,
            }
            result = api.predict(request)
            pred = result["predictions"][0]
            is_default = pred["predicted_default"]
            probability = pred["default_probability"]
            threshold = result["threshold"]

            label = "DEFAULT" if is_default else "NO DEFAULT"

            return (
                label,
                f"{probability:.4f} ({probability * 100:.1f}%)",
                f"{threshold:.4f}",
                gr.update(visible=False, value=""),
            )
        except httpx.HTTPStatusError as exc:
            logger.exception("Prediction HTTP error")
            status = exc.response.status_code
            if status == 401:
                msg = "Authentication failed. Please check your API key."
            elif status == 404:
                msg = "Model not found. Please select a valid model."
            elif status == 429:
                msg = "Rate limit exceeded. Please try again later."
            else:
                msg = "Prediction request failed. Please try again."
            return (
                "",
                "",
                "",
                gr.update(visible=True, value=msg),
            )
        except Exception:
            logger.exception("Prediction request failed")
            return (
                "",
                "",
                "",
                gr.update(
                    visible=True,
                    value="An unexpected error occurred. Please try again.",
                ),
            )

    refresh_btn.click(fn=_refresh, inputs=[], outputs=[model_selector])

    def _show_predicting_status() -> Any:
        """Show a loading message while prediction is in progress."""
        return gr.update(visible=True, value="Predicting\u2026")

    predict_btn.click(
        fn=_show_predicting_status,
        inputs=[],
        outputs=[error_display],
    ).then(
        fn=_predict,
        inputs=[
            model_selector,
            person_age,
            person_income,
            person_emp_length,
            loan_amnt,
            loan_int_rate,
            loan_percent_income,
            cb_person_cred_hist_length,
            person_home_ownership,
            loan_intent,
            loan_grade,
            cb_default,
        ],
        outputs=[
            prediction_result,
            probability_display,
            threshold_display,
            error_display,
        ],
    )
