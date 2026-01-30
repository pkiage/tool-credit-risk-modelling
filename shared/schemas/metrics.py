"""Model evaluation metrics schemas."""

from pydantic import BaseModel, Field


class ThresholdResult(BaseModel):
    """Results from threshold optimization analysis.

    Attributes:
        threshold: Classification threshold value (0-1).
        sensitivity: True positive rate (recall).
        specificity: True negative rate.
        youden_j: Youden's J statistic (sensitivity + specificity - 1).
        precision: Positive predictive value.
        f1_score: Harmonic mean of precision and recall.
    """

    threshold: float = Field(ge=0, le=1, description="Classification threshold")
    sensitivity: float = Field(ge=0, le=1, description="True positive rate (recall)")
    specificity: float = Field(ge=0, le=1, description="True negative rate")
    youden_j: float = Field(ge=-1, le=1, description="Youden's J statistic")
    precision: float = Field(
        ge=0, le=1, description="Positive predictive value (precision)"
    )
    f1_score: float = Field(ge=0, le=1, description="F1 score")


class ROCCurveData(BaseModel):
    """ROC curve data points.

    Attributes:
        fpr: False positive rates at each threshold.
        tpr: True positive rates at each threshold.
        thresholds: Threshold values.
    """

    fpr: list[float] = Field(description="False positive rates")
    tpr: list[float] = Field(description="True positive rates")
    thresholds: list[float] = Field(description="Threshold values")


class ConfusionMatrix(BaseModel):
    """Confusion matrix with labels.

    Attributes:
        matrix: 2x2 confusion matrix [[TN, FP], [FN, TP]].
        true_negatives: Count of true negatives.
        false_positives: Count of false positives.
        false_negatives: Count of false negatives.
        true_positives: Count of true positives.
    """

    matrix: list[list[int]] = Field(description="2x2 confusion matrix")
    true_negatives: int = Field(ge=0, description="True negatives")
    false_positives: int = Field(ge=0, description="False positives")
    false_negatives: int = Field(ge=0, description="False negatives")
    true_positives: int = Field(ge=0, description="True positives")


class CalibrationCurve(BaseModel):
    """Calibration curve data for probability calibration assessment.

    Attributes:
        prob_true: Fraction of positives in each bin.
        prob_pred: Mean predicted probability in each bin.
        n_bins: Number of bins used.
    """

    prob_true: list[float] = Field(description="True probability per bin")
    prob_pred: list[float] = Field(description="Predicted probability per bin")
    n_bins: int = Field(gt=0, description="Number of bins")


class ModelMetrics(BaseModel):
    """Comprehensive model performance metrics.

    Attributes:
        accuracy: Overall accuracy (0-1).
        precision: Positive predictive value (0-1).
        recall: Sensitivity / true positive rate (0-1).
        f1_score: Harmonic mean of precision and recall (0-1).
        roc_auc: Area under ROC curve (0-1).
        threshold_analysis: Optimal threshold analysis results.
        roc_curve: ROC curve data points.
        confusion_matrix: Confusion matrix at optimal threshold.
        calibration_curve: Probability calibration assessment.
    """

    accuracy: float = Field(ge=0, le=1, description="Overall accuracy")
    precision: float = Field(ge=0, le=1, description="Positive predictive value")
    recall: float = Field(ge=0, le=1, description="Sensitivity (TPR)")
    f1_score: float = Field(ge=0, le=1, description="F1 score")
    roc_auc: float = Field(ge=0, le=1, description="Area under ROC curve")
    threshold_analysis: ThresholdResult = Field(
        description="Optimal threshold analysis"
    )
    roc_curve: ROCCurveData = Field(description="ROC curve data")
    confusion_matrix: ConfusionMatrix = Field(
        description="Confusion matrix at optimal threshold"
    )
    calibration_curve: CalibrationCurve | None = Field(
        default=None, description="Calibration curve data"
    )
