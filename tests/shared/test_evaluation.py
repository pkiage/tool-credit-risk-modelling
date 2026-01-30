"""Tests for evaluation logic."""

import numpy as np
import pytest

from shared.logic.evaluation import (
    calculate_calibration_curve,
    calculate_confusion_matrix,
    calculate_model_confidence,
    calculate_roc_curve,
    evaluate_model,
)


class TestCalculateROCCurve:
    """Tests for calculate_roc_curve function."""

    def test_roc_curve_basic(self, binary_classification_data):
        """Test ROC curve calculation with basic data."""
        y_true, y_proba = binary_classification_data
        roc_data = calculate_roc_curve(y_true, y_proba)

        # Check structure
        assert len(roc_data.fpr) > 0
        assert len(roc_data.tpr) > 0
        assert len(roc_data.thresholds) > 0
        assert len(roc_data.fpr) == len(roc_data.tpr)

        # FPR and TPR should be in [0, 1]
        assert all(0 <= x <= 1 for x in roc_data.fpr)
        assert all(0 <= x <= 1 for x in roc_data.tpr)

        # First point should be (0, 0) or close, last should be (1, 1) or close
        # (ROC curve starts at bottom-left, ends at top-right)

    def test_roc_curve_perfect(self, perfect_predictions):
        """Test ROC curve with perfect predictions."""
        y_true, y_proba = perfect_predictions
        roc_data = calculate_roc_curve(y_true, y_proba)

        # With perfect predictions, AUC should be 1.0
        # Check that we have the expected points
        assert len(roc_data.fpr) > 0
        assert len(roc_data.tpr) > 0


class TestCalculateConfusionMatrix:
    """Tests for calculate_confusion_matrix function."""

    def test_confusion_matrix_basic(self):
        """Test confusion matrix calculation."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 1, 0, 0])

        cm = calculate_confusion_matrix(y_true, y_pred)

        # Check that values sum to total samples
        total = (
            cm.true_negatives
            + cm.false_positives
            + cm.false_negatives
            + cm.true_positives
        )
        assert total == len(y_true)

        # Check matrix shape
        assert len(cm.matrix) == 2
        assert len(cm.matrix[0]) == 2

        # Check that matrix matches individual components
        assert cm.matrix[0][0] == cm.true_negatives
        assert cm.matrix[0][1] == cm.false_positives
        assert cm.matrix[1][0] == cm.false_negatives
        assert cm.matrix[1][1] == cm.true_positives

    def test_confusion_matrix_perfect(self):
        """Test confusion matrix with perfect predictions."""
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([0, 0, 1, 1])

        cm = calculate_confusion_matrix(y_true, y_pred)

        # Should have no false positives or false negatives
        assert cm.false_positives == 0
        assert cm.false_negatives == 0
        assert cm.true_positives == 2
        assert cm.true_negatives == 2

    def test_confusion_matrix_all_wrong(self):
        """Test confusion matrix with all wrong predictions."""
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([1, 1, 0, 0])

        cm = calculate_confusion_matrix(y_true, y_pred)

        # Should have no true positives or true negatives
        assert cm.true_positives == 0
        assert cm.true_negatives == 0
        assert cm.false_positives == 2
        assert cm.false_negatives == 2


class TestCalculateCalibrationCurve:
    """Tests for calculate_calibration_curve function."""

    def test_calibration_curve_basic(self, binary_classification_data):
        """Test calibration curve calculation."""
        y_true, y_proba = binary_classification_data
        cal_curve = calculate_calibration_curve(y_true, y_proba, n_bins=5)

        # Check structure
        assert len(cal_curve.prob_true) > 0
        assert len(cal_curve.prob_pred) > 0
        assert len(cal_curve.prob_true) == len(cal_curve.prob_pred)
        assert cal_curve.n_bins == 5

        # Probabilities should be in [0, 1]
        assert all(0 <= x <= 1 for x in cal_curve.prob_true)
        assert all(0 <= x <= 1 for x in cal_curve.prob_pred)

    def test_calibration_curve_custom_bins(self, binary_classification_data):
        """Test calibration curve with custom number of bins."""
        y_true, y_proba = binary_classification_data
        cal_curve = calculate_calibration_curve(y_true, y_proba, n_bins=3)

        assert cal_curve.n_bins == 3


class TestEvaluateModel:
    """Tests for evaluate_model function."""

    def test_evaluate_model_basic(self, binary_classification_data):
        """Test comprehensive model evaluation."""
        y_true, y_proba = binary_classification_data
        metrics = evaluate_model(y_true, y_proba)

        # Check all metrics are present
        assert 0 <= metrics.accuracy <= 1
        assert 0 <= metrics.precision <= 1
        assert 0 <= metrics.recall <= 1
        assert 0 <= metrics.f1_score <= 1
        assert 0 <= metrics.roc_auc <= 1

        # Check threshold analysis
        assert 0 <= metrics.threshold_analysis.threshold <= 1
        assert 0 <= metrics.threshold_analysis.sensitivity <= 1
        assert 0 <= metrics.threshold_analysis.specificity <= 1

        # Check ROC curve
        assert len(metrics.roc_curve.fpr) > 0
        assert len(metrics.roc_curve.tpr) > 0

        # Check confusion matrix
        assert metrics.confusion_matrix.true_positives >= 0
        assert metrics.confusion_matrix.true_negatives >= 0

        # Check calibration curve is included by default
        assert metrics.calibration_curve is not None

    def test_evaluate_model_without_calibration(self, binary_classification_data):
        """Test model evaluation without calibration curve."""
        y_true, y_proba = binary_classification_data
        metrics = evaluate_model(y_true, y_proba, include_calibration=False)

        # Calibration curve should be None
        assert metrics.calibration_curve is None

    def test_evaluate_model_custom_threshold(self, binary_classification_data):
        """Test model evaluation with custom threshold."""
        y_true, y_proba = binary_classification_data
        metrics = evaluate_model(y_true, y_proba, threshold=0.6)

        # Should use the specified threshold
        assert metrics.threshold_analysis.threshold == 0.6

    def test_evaluate_model_perfect(self, perfect_predictions):
        """Test model evaluation with perfect predictions."""
        y_true, y_proba = perfect_predictions
        metrics = evaluate_model(y_true, y_proba)

        # All metrics should be perfect (or very close)
        assert metrics.accuracy >= 0.99
        assert metrics.precision >= 0.99
        assert metrics.recall >= 0.99
        assert metrics.f1_score >= 0.99
        assert metrics.roc_auc >= 0.99

    def test_evaluate_model_consistency(self, binary_classification_data):
        """Test that evaluation is consistent across runs."""
        y_true, y_proba = binary_classification_data

        metrics1 = evaluate_model(y_true, y_proba, threshold=0.5)
        metrics2 = evaluate_model(y_true, y_proba, threshold=0.5)

        # Same inputs should give same results
        assert metrics1.accuracy == metrics2.accuracy
        assert metrics1.roc_auc == metrics2.roc_auc
        assert metrics1.threshold_analysis.threshold == metrics2.threshold_analysis.threshold


class TestCalculateModelConfidence:
    """Tests for calculate_model_confidence function."""

    def test_confidence_basic(self):
        """Test confidence calculation with basic data."""
        y_proba = np.array([0.1, 0.49, 0.51, 0.9])
        threshold = 0.5

        confidence = calculate_model_confidence(y_proba, threshold)

        # Check shape
        assert len(confidence) == len(y_proba)

        # All confidence values should be in [0, 1]
        assert all(0 <= c <= 1 for c in confidence)

        # Values far from threshold should have high confidence
        assert confidence[0] > confidence[1]  # 0.1 vs 0.49
        assert confidence[3] > confidence[2]  # 0.9 vs 0.51

    def test_confidence_at_threshold(self):
        """Test confidence is zero at threshold."""
        y_proba = np.array([0.5, 0.5, 0.5])
        threshold = 0.5

        confidence = calculate_model_confidence(y_proba, threshold)

        # Confidence should be 0 at threshold
        assert all(c == 0 for c in confidence)

    def test_confidence_symmetric(self):
        """Test confidence is symmetric around threshold."""
        y_proba = np.array([0.2, 0.8])
        threshold = 0.5

        confidence = calculate_model_confidence(y_proba, threshold)

        # 0.2 and 0.8 are equidistant from 0.5, so should have same confidence
        assert abs(confidence[0] - confidence[1]) < 0.01

    def test_confidence_extreme_values(self):
        """Test confidence at extreme probability values."""
        y_proba = np.array([0.0, 1.0])
        threshold = 0.5

        confidence = calculate_model_confidence(y_proba, threshold)

        # Maximum possible confidence at extremes
        assert confidence[0] == 1.0
        assert confidence[1] == 1.0

    def test_confidence_asymmetric_threshold(self):
        """Test confidence with non-0.5 threshold."""
        y_proba = np.array([0.0, 0.3, 0.7, 1.0])
        threshold = 0.7

        confidence = calculate_model_confidence(y_proba, threshold)

        # All should be valid
        assert all(0 <= c <= 1 for c in confidence)

        # Value at threshold should have lowest confidence
        assert confidence[2] < confidence[0]
        assert confidence[2] < confidence[3]
