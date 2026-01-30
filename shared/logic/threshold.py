"""Threshold optimization using Youden's J statistic."""

import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import roc_curve

from shared.schemas.metrics import ThresholdResult


def find_optimal_threshold(
    y_true: NDArray[np.int_], y_proba: NDArray[np.float64]
) -> ThresholdResult:
    """Find optimal classification threshold using Youden's J statistic.

    Youden's J statistic (J = sensitivity + specificity - 1) is maximized to find
    the optimal threshold. This balances true positive rate and true negative rate.

    Args:
        y_true: True binary labels (0 or 1).
        y_proba: Predicted probabilities for the positive class.

    Returns:
        ThresholdResult containing optimal threshold and performance metrics.

    Raises:
        ValueError: If arrays are empty or have mismatched lengths.

    Example:
        >>> y_true = np.array([0, 0, 1, 1])
        >>> y_proba = np.array([0.1, 0.4, 0.6, 0.9])
        >>> result = find_optimal_threshold(y_true, y_proba)
        >>> result.threshold
        0.6
    """
    if len(y_true) == 0 or len(y_proba) == 0:
        raise ValueError("Input arrays cannot be empty")

    if len(y_true) != len(y_proba):
        raise ValueError(
            f"Array length mismatch: y_true={len(y_true)}, y_proba={len(y_proba)}"
        )

    # Check for degenerate cases (all same class)
    unique_classes = np.unique(y_true)
    if len(unique_classes) == 1:
        raise ValueError(
            f"Cannot calculate ROC curve with only one class present. "
            f"Found only class {unique_classes[0]}"
        )

    # Calculate ROC curve points
    fpr, tpr, thresholds = roc_curve(y_true, y_proba)

    # Calculate Youden's J statistic (J = sensitivity + specificity - 1)
    # Since specificity = 1 - fpr and sensitivity = tpr:
    # J = tpr + (1 - fpr) - 1 = tpr - fpr
    youden_j = tpr - fpr

    # Find index of maximum J statistic
    optimal_idx = int(np.argmax(youden_j))

    # Get optimal threshold and corresponding metrics
    optimal_threshold = float(thresholds[optimal_idx])

    # Handle inf/nan values from edge cases
    if not np.isfinite(optimal_threshold):
        optimal_threshold = 0.5  # Default fallback

    optimal_tpr = float(tpr[optimal_idx])
    optimal_fpr = float(fpr[optimal_idx])

    # Handle nan values in TPR/FPR
    if not np.isfinite(optimal_tpr):
        optimal_tpr = 0.0
    if not np.isfinite(optimal_fpr):
        optimal_fpr = 0.0

    optimal_tnr = 1.0 - optimal_fpr  # specificity
    optimal_j = float(youden_j[optimal_idx])

    # Handle nan in Youden's J
    if not np.isfinite(optimal_j):
        optimal_j = 0.0

    # Calculate precision and F1 at optimal threshold
    y_pred = (y_proba >= optimal_threshold).astype(int)
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1_score = (
        2 * (precision * optimal_tpr) / (precision + optimal_tpr)
        if (precision + optimal_tpr) > 0
        else 0.0
    )

    return ThresholdResult(
        threshold=optimal_threshold,
        sensitivity=optimal_tpr,
        specificity=optimal_tnr,
        youden_j=optimal_j,
        precision=precision,
        f1_score=f1_score,
    )


def evaluate_threshold(
    y_true: NDArray[np.int_], y_proba: NDArray[np.float64], threshold: float
) -> ThresholdResult:
    """Evaluate a specific threshold value.

    Args:
        y_true: True binary labels (0 or 1).
        y_proba: Predicted probabilities for the positive class.
        threshold: Classification threshold to evaluate (0-1).

    Returns:
        ThresholdResult with metrics for the given threshold.

    Raises:
        ValueError: If threshold is not in [0, 1] or arrays have issues.
    """
    if not 0 <= threshold <= 1:
        raise ValueError(f"Threshold must be in [0, 1], got {threshold}")

    if len(y_true) != len(y_proba):
        raise ValueError(
            f"Array length mismatch: y_true={len(y_true)}, y_proba={len(y_proba)}"
        )

    # Make predictions using the threshold
    y_pred = (y_proba >= threshold).astype(int)

    # Calculate confusion matrix components
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    # Calculate metrics
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    youden_j = sensitivity + specificity - 1.0

    f1 = (
        2 * (precision * sensitivity) / (precision + sensitivity)
        if (precision + sensitivity) > 0
        else 0.0
    )

    return ThresholdResult(
        threshold=threshold,
        sensitivity=sensitivity,
        specificity=specificity,
        youden_j=youden_j,
        precision=precision,
        f1_score=f1,
    )
