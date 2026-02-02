"""Tests for threshold optimization logic."""

import numpy as np
import pytest

from shared.logic.threshold import evaluate_threshold, find_optimal_threshold


class TestFindOptimalThreshold:
    """Tests for find_optimal_threshold function."""

    def test_optimal_threshold_basic(self, binary_classification_data):
        """Test finding optimal threshold with basic data."""
        y_true, y_proba = binary_classification_data
        result = find_optimal_threshold(y_true, y_proba)

        # Check result structure
        assert 0 <= result.threshold <= 1
        assert 0 <= result.sensitivity <= 1
        assert 0 <= result.specificity <= 1
        assert -1 <= result.youden_j <= 1
        assert 0 <= result.precision <= 1
        assert 0 <= result.f1_score <= 1

        # Youden's J should equal sensitivity + specificity - 1
        expected_j = result.sensitivity + result.specificity - 1
        assert abs(result.youden_j - expected_j) < 0.01

    def test_optimal_threshold_perfect_predictions(self, perfect_predictions):
        """Test with perfect predictions."""
        y_true, y_proba = perfect_predictions
        result = find_optimal_threshold(y_true, y_proba)

        # With perfect predictions, we should get perfect metrics
        assert result.sensitivity == 1.0
        assert result.specificity == 1.0
        assert result.youden_j == 1.0
        assert result.precision == 1.0
        assert result.f1_score == 1.0

    def test_empty_arrays_raise_error(self):
        """Test that empty arrays raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            find_optimal_threshold(np.array([]), np.array([]))

    def test_mismatched_lengths_raise_error(self):
        """Test that mismatched array lengths raise ValueError."""
        y_true = np.array([0, 1, 0])
        y_proba = np.array([0.3, 0.7])  # Different length

        with pytest.raises(ValueError, match="length mismatch"):
            find_optimal_threshold(y_true, y_proba)

    def test_all_zeros(self):
        """Test with all negative class samples."""
        y_true = np.array([0, 0, 0, 0])
        y_proba = np.array([0.1, 0.2, 0.3, 0.4])

        # Should raise error with only one class
        with pytest.raises(ValueError, match="only one class"):
            find_optimal_threshold(y_true, y_proba)

    def test_all_ones(self):
        """Test with all positive class samples."""
        y_true = np.array([1, 1, 1, 1])
        y_proba = np.array([0.6, 0.7, 0.8, 0.9])

        # Should raise error with only one class
        with pytest.raises(ValueError, match="only one class"):
            find_optimal_threshold(y_true, y_proba)

    def test_random_seed_consistency(self):
        """Test that results are consistent for same input."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_proba = np.array([0.2, 0.3, 0.6, 0.8, 0.4, 0.7])

        result1 = find_optimal_threshold(y_true, y_proba)
        result2 = find_optimal_threshold(y_true, y_proba)

        assert result1.threshold == result2.threshold
        assert result1.youden_j == result2.youden_j

    def test_extreme_imbalance(self):
        """Test with extremely imbalanced data."""
        # 95% negative, 5% positive
        y_true = np.array([0] * 95 + [1] * 5)
        y_proba = np.concatenate(
            [np.random.uniform(0, 0.5, 95), np.random.uniform(0.5, 1, 5)]
        )

        result = find_optimal_threshold(y_true, y_proba)

        # Should still produce valid result
        assert 0 <= result.threshold <= 1
        assert -1 <= result.youden_j <= 1


class TestEvaluateThreshold:
    """Tests for evaluate_threshold function."""

    def test_evaluate_threshold_basic(self, binary_classification_data):
        """Test evaluating a specific threshold."""
        y_true, y_proba = binary_classification_data
        result = evaluate_threshold(y_true, y_proba, threshold=0.5)

        # Check result structure
        assert result.threshold == 0.5
        assert 0 <= result.sensitivity <= 1
        assert 0 <= result.specificity <= 1
        assert -1 <= result.youden_j <= 1

    def test_threshold_zero(self, binary_classification_data):
        """Test with threshold = 0 (predict all positive)."""
        y_true, y_proba = binary_classification_data
        result = evaluate_threshold(y_true, y_proba, threshold=0.0)

        # At threshold 0, all predictions should be positive
        # Sensitivity should be 1 (all positives caught)
        # Specificity should be 0 (no negatives caught)
        assert result.sensitivity == 1.0
        assert result.specificity == 0.0

    def test_threshold_one(self, binary_classification_data):
        """Test with threshold = 1 (predict all negative)."""
        y_true, y_proba = binary_classification_data
        result = evaluate_threshold(y_true, y_proba, threshold=1.0)

        # At threshold 1, all predictions should be negative
        # Sensitivity should be 0 (no positives caught)
        # Specificity should be 1 (all negatives caught)
        assert result.sensitivity == 0.0
        assert result.specificity == 1.0

    def test_invalid_threshold_negative(self, binary_classification_data):
        """Test that negative threshold raises ValueError."""
        y_true, y_proba = binary_classification_data

        with pytest.raises(ValueError, match="must be in"):
            evaluate_threshold(y_true, y_proba, threshold=-0.1)

    def test_invalid_threshold_too_high(self, binary_classification_data):
        """Test that threshold > 1 raises ValueError."""
        y_true, y_proba = binary_classification_data

        with pytest.raises(ValueError, match="must be in"):
            evaluate_threshold(y_true, y_proba, threshold=1.5)

    def test_mismatched_lengths(self):
        """Test that mismatched array lengths raise ValueError."""
        y_true = np.array([0, 1, 0])
        y_proba = np.array([0.3, 0.7])

        with pytest.raises(ValueError, match="length mismatch"):
            evaluate_threshold(y_true, y_proba, threshold=0.5)

    def test_perfect_separation(self):
        """Test with perfectly separable data."""
        y_true = np.array([0, 0, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.8, 0.9])

        result = evaluate_threshold(y_true, y_proba, threshold=0.5)

        # With perfect separation at 0.5, all metrics should be perfect
        assert result.sensitivity == 1.0
        assert result.specificity == 1.0
        assert result.precision == 1.0
        assert result.f1_score == 1.0
        assert result.youden_j == 1.0

    def test_youden_j_calculation(self):
        """Test that Youden's J is calculated correctly."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_proba = np.array([0.2, 0.3, 0.6, 0.8, 0.4, 0.7])

        result = evaluate_threshold(y_true, y_proba, threshold=0.5)

        # Youden's J = sensitivity + specificity - 1
        expected_j = result.sensitivity + result.specificity - 1
        assert abs(result.youden_j - expected_j) < 0.01

    def test_compare_with_optimal(self, binary_classification_data):
        """Test that optimal threshold gives best Youden's J."""
        y_true, y_proba = binary_classification_data

        # Find optimal threshold
        optimal_result = find_optimal_threshold(y_true, y_proba)

        # Evaluate at slightly different thresholds
        lower_result = evaluate_threshold(
            y_true, y_proba, threshold=max(0, optimal_result.threshold - 0.05)
        )
        higher_result = evaluate_threshold(
            y_true, y_proba, threshold=min(1, optimal_result.threshold + 0.05)
        )

        # Optimal should have highest (or tied) Youden's J
        assert optimal_result.youden_j >= lower_result.youden_j - 0.01
        assert optimal_result.youden_j >= higher_result.youden_j - 0.01
