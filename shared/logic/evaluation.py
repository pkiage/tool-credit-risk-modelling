"""Model evaluation functions for ROC, AUC, confusion matrix, and calibration."""

import numpy as np
from numpy.typing import NDArray
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from shared.logic.threshold import find_optimal_threshold
from shared.schemas.metrics import (
    CalibrationCurve,
    ConfusionMatrix,
    ModelMetrics,
    ROCCurveData,
)


def calculate_roc_curve(
    y_true: NDArray[np.int_], y_proba: NDArray[np.float64]
) -> ROCCurveData:
    """Calculate ROC curve data points.

    Args:
        y_true: True binary labels (0 or 1).
        y_proba: Predicted probabilities for the positive class.

    Returns:
        ROCCurveData containing FPR, TPR, and threshold arrays.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)

    return ROCCurveData(
        fpr=fpr.tolist(), tpr=tpr.tolist(), thresholds=thresholds.tolist()
    )


def calculate_confusion_matrix(
    y_true: NDArray[np.int_], y_pred: NDArray[np.int_]
) -> ConfusionMatrix:
    """Calculate confusion matrix with labeled components.

    Args:
        y_true: True binary labels (0 or 1).
        y_pred: Predicted binary labels (0 or 1).

    Returns:
        ConfusionMatrix with matrix and individual components.
    """
    cm = confusion_matrix(y_true, y_pred)

    # Ensure we have a 2x2 matrix
    if cm.shape != (2, 2):
        raise ValueError(f"Expected 2x2 confusion matrix, got shape {cm.shape}")

    tn, fp, fn, tp = cm.ravel()

    return ConfusionMatrix(
        matrix=cm.tolist(),
        true_negatives=int(tn),
        false_positives=int(fp),
        false_negatives=int(fn),
        true_positives=int(tp),
    )


def calculate_calibration_curve(
    y_true: NDArray[np.int_], y_proba: NDArray[np.float64], n_bins: int = 10
) -> CalibrationCurve:
    """Calculate calibration curve to assess probability calibration.

    Args:
        y_true: True binary labels (0 or 1).
        y_proba: Predicted probabilities for the positive class.
        n_bins: Number of bins for calibration curve (default: 10).

    Returns:
        CalibrationCurve with true and predicted probabilities per bin.
    """
    prob_true, prob_pred = calibration_curve(
        y_true, y_proba, n_bins=n_bins, strategy="uniform"
    )

    return CalibrationCurve(
        prob_true=prob_true.tolist(), prob_pred=prob_pred.tolist(), n_bins=n_bins
    )


def evaluate_model(
    y_true: NDArray[np.int_],
    y_proba: NDArray[np.float64],
    threshold: float | None = None,
    include_calibration: bool = True,
) -> ModelMetrics:
    """Comprehensive model evaluation with all metrics.

    Args:
        y_true: True binary labels (0 or 1).
        y_proba: Predicted probabilities for the positive class.
        threshold: Classification threshold (if None, optimal is calculated).
        include_calibration: Whether to calculate calibration curve.

    Returns:
        ModelMetrics with comprehensive performance metrics.

    Example:
        >>> y_true = np.array([0, 0, 1, 1])
        >>> y_proba = np.array([0.1, 0.4, 0.6, 0.9])
        >>> metrics = evaluate_model(y_true, y_proba)
        >>> metrics.roc_auc
        1.0
    """
    # Calculate ROC curve and AUC
    roc_data = calculate_roc_curve(y_true, y_proba)
    auc = float(roc_auc_score(y_true, y_proba))

    # Find or use provided threshold
    if threshold is None:
        threshold_result = find_optimal_threshold(y_true, y_proba)
        threshold = threshold_result.threshold
    else:
        from shared.logic.threshold import evaluate_threshold

        threshold_result = evaluate_threshold(y_true, y_proba, threshold)

    # Make predictions using threshold
    y_pred = (y_proba >= threshold).astype(int)

    # Calculate basic metrics
    accuracy = float(accuracy_score(y_true, y_pred))
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    # Calculate confusion matrix
    cm = calculate_confusion_matrix(y_true, y_pred)

    # Calculate calibration curve if requested
    calibration = None
    if include_calibration:
        try:
            calibration = calculate_calibration_curve(y_true, y_proba)
        except (ValueError, IndexError):
            # Skip calibration if there's insufficient data
            pass

    return ModelMetrics(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        roc_auc=auc,
        threshold_analysis=threshold_result,
        roc_curve=roc_data,
        confusion_matrix=cm,
        calibration_curve=calibration,
    )


def calculate_model_confidence(
    y_proba: NDArray[np.float64], threshold: float
) -> NDArray[np.float64]:
    """Calculate prediction confidence based on distance from threshold.

    Confidence is defined as the absolute distance from the threshold,
    normalized to [0, 1] where 1 means maximally confident.

    Args:
        y_proba: Predicted probabilities for the positive class.
        threshold: Classification threshold.

    Returns:
        Array of confidence scores (0-1).

    Example:
        >>> y_proba = np.array([0.1, 0.49, 0.51, 0.9])
        >>> threshold = 0.5
        >>> confidence = calculate_model_confidence(y_proba, threshold)
        >>> confidence
        array([0.8, 0.02, 0.02, 0.8])
    """
    # Distance from threshold
    distances = np.abs(y_proba - threshold)

    # Maximum possible distance is either threshold or (1 - threshold)
    max_distance = max(threshold, 1 - threshold)

    # Normalize to [0, 1]
    confidence = distances / max_distance

    return confidence
