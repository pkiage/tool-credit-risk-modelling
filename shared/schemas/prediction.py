"""Prediction request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from shared.schemas.loan import LoanApplication


class PredictionRequest(BaseModel):
    """Request for loan default predictions.

    Attributes:
        model_id: ID of the trained model to use for predictions.
        applications: List of loan applications to predict.
        threshold: Classification threshold (default uses model's optimal threshold).
        include_probabilities: Whether to include probability scores in response.
    """

    model_id: str = Field(description="Trained model identifier")
    applications: list[LoanApplication] = Field(
        min_length=1, description="Loan applications to predict"
    )
    threshold: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Classification threshold (None uses model default)",
    )
    include_probabilities: bool = Field(
        default=True, description="Include probability scores"
    )


class PredictionResult(BaseModel):
    """Single loan prediction result.

    Attributes:
        application: The loan application that was evaluated.
        predicted_default: Whether default is predicted (True) or not (False).
        default_probability: Probability of default (0-1).
        confidence: Confidence level based on distance from threshold.
    """

    application: LoanApplication = Field(description="Loan application")
    predicted_default: bool = Field(description="Predicted default indicator")
    default_probability: float = Field(ge=0, le=1, description="Probability of default")
    confidence: float = Field(
        ge=0, le=1, description="Prediction confidence (distance from threshold)"
    )


class PredictionResponse(BaseModel):
    """Response containing predictions for loan applications.

    Attributes:
        model_id: ID of the model used for predictions.
        model_type: Type of model used.
        threshold: Classification threshold used.
        predictions: List of prediction results.
        timestamp: When predictions were made.
        total_applications: Total number of applications processed.
        predicted_defaults: Number of predicted defaults.
        predicted_approvals: Number of predicted approvals.
    """

    model_id: str = Field(description="Model identifier used")
    model_type: str = Field(description="Model type")
    threshold: float = Field(ge=0, le=1, description="Classification threshold used")
    predictions: list[PredictionResult] = Field(description="Prediction results")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Prediction timestamp"
    )
    total_applications: int = Field(ge=0, description="Total applications")
    predicted_defaults: int = Field(ge=0, description="Number of predicted defaults")
    predicted_approvals: int = Field(ge=0, description="Number of predicted approvals")

    def __len__(self) -> int:
        """Return number of predictions."""
        return len(self.predictions)
