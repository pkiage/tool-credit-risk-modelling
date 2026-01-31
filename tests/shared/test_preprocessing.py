"""Tests for preprocessing logic."""

import numpy as np
import pytest

from shared.logic.preprocessing import (
    decode_home_ownership,
    decode_loan_grade,
    decode_loan_intent,
    encode_default_on_file,
    encode_home_ownership,
    encode_loan_grade,
    encode_loan_intent,
    undersample_majority_class,
)


class TestEncodeHomeOwnership:
    """Tests for encode_home_ownership function."""

    def test_encode_valid_values(self):
        """Test encoding valid home ownership values."""
        values = ["RENT", "OWN", "MORTGAGE", "OTHER"]
        encoded = encode_home_ownership(values)

        assert len(encoded) == 4
        assert encoded[0] == 0  # RENT
        assert encoded[1] == 1  # OWN
        assert encoded[2] == 2  # MORTGAGE
        assert encoded[3] == 3  # OTHER

    def test_encode_invalid_value(self):
        """Test encoding invalid value raises error."""
        with pytest.raises(ValueError, match="Unknown home_ownership value"):
            encode_home_ownership(["RENT", "INVALID"])

    def test_encode_empty_list(self):
        """Test encoding empty list."""
        encoded = encode_home_ownership([])
        assert len(encoded) == 0

    def test_encode_numpy_array(self):
        """Test encoding numpy array input."""
        values = np.array(["RENT", "OWN"])
        encoded = encode_home_ownership(values)

        assert isinstance(encoded, np.ndarray)
        assert encoded[0] == 0
        assert encoded[1] == 1


class TestEncodeLoanIntent:
    """Tests for encode_loan_intent function."""

    def test_encode_valid_values(self):
        """Test encoding valid loan intent values."""
        values = ["EDUCATION", "MEDICAL", "VENTURE"]
        encoded = encode_loan_intent(values)

        assert len(encoded) == 3
        assert encoded[0] == 0  # EDUCATION
        assert encoded[1] == 1  # MEDICAL
        assert encoded[2] == 2  # VENTURE

    def test_encode_all_intents(self):
        """Test encoding all loan intent categories."""
        values = [
            "EDUCATION",
            "MEDICAL",
            "VENTURE",
            "PERSONAL",
            "DEBTCONSOLIDATION",
            "HOMEIMPROVEMENT",
        ]
        encoded = encode_loan_intent(values)

        assert len(encoded) == 6
        assert list(encoded) == [0, 1, 2, 3, 4, 5]

    def test_encode_invalid_intent(self):
        """Test encoding invalid intent raises error."""
        with pytest.raises(ValueError, match="Unknown loan_intent value"):
            encode_loan_intent(["EDUCATION", "INVALID_INTENT"])


class TestEncodeLoanGrade:
    """Tests for encode_loan_grade function."""

    def test_encode_valid_grades(self):
        """Test encoding valid loan grades."""
        values = ["A", "B", "C", "D", "E", "F", "G"]
        encoded = encode_loan_grade(values)

        assert len(encoded) == 7
        assert list(encoded) == [0, 1, 2, 3, 4, 5, 6]

    def test_encode_invalid_grade(self):
        """Test encoding invalid grade raises error."""
        with pytest.raises(ValueError, match="Unknown loan_grade value"):
            encode_loan_grade(["A", "H"])  # H is not valid

    def test_encode_partial_grades(self):
        """Test encoding subset of grades."""
        values = ["A", "C", "E"]
        encoded = encode_loan_grade(values)

        assert encoded[0] == 0
        assert encoded[1] == 2
        assert encoded[2] == 4


class TestEncodeDefaultOnFile:
    """Tests for encode_default_on_file function."""

    def test_encode_valid_values(self):
        """Test encoding valid default on file values."""
        values = ["N", "Y", "N"]
        encoded = encode_default_on_file(values)

        assert len(encoded) == 3
        assert encoded[0] == 0  # N
        assert encoded[1] == 1  # Y
        assert encoded[2] == 0  # N

    def test_encode_invalid_value(self):
        """Test encoding invalid value raises error."""
        with pytest.raises(ValueError, match="Unknown default_on_file value"):
            encode_default_on_file(["N", "MAYBE"])


class TestDecodeHomeOwnership:
    """Tests for decode_home_ownership function."""

    def test_decode_valid_values(self):
        """Test decoding valid encoded values."""
        encoded = [0, 1, 2, 3]
        decoded = decode_home_ownership(encoded)

        assert decoded == ["RENT", "OWN", "MORTGAGE", "OTHER"]

    def test_roundtrip_encoding(self):
        """Test encode -> decode roundtrip."""
        original = ["RENT", "OWN", "MORTGAGE"]
        encoded = encode_home_ownership(original)
        decoded = decode_home_ownership(encoded)

        assert decoded == original


class TestDecodeLoanIntent:
    """Tests for decode_loan_intent function."""

    def test_decode_valid_values(self):
        """Test decoding valid encoded values."""
        encoded = [0, 1, 2]
        decoded = decode_loan_intent(encoded)

        assert decoded == ["EDUCATION", "MEDICAL", "VENTURE"]

    def test_roundtrip_encoding(self):
        """Test encode -> decode roundtrip."""
        original = ["EDUCATION", "PERSONAL", "HOMEIMPROVEMENT"]
        encoded = encode_loan_intent(original)
        decoded = decode_loan_intent(encoded)

        assert decoded == original


class TestDecodeLoanGrade:
    """Tests for decode_loan_grade function."""

    def test_decode_valid_values(self):
        """Test decoding valid encoded values."""
        encoded = [0, 1, 2, 3, 4, 5, 6]
        decoded = decode_loan_grade(encoded)

        assert decoded == ["A", "B", "C", "D", "E", "F", "G"]

    def test_roundtrip_encoding(self):
        """Test encode -> decode roundtrip."""
        original = ["A", "C", "E", "G"]
        encoded = encode_loan_grade(original)
        decoded = decode_loan_grade(encoded)

        assert decoded == original


class TestUndersampleMajorityClass:
    """Tests for undersample_majority_class function."""

    def test_undersample_basic(self, imbalanced_data):
        """Test basic undersampling functionality."""
        X, y = imbalanced_data

        X_balanced, y_balanced = undersample_majority_class(X, y, random_state=42)

        # Should have equal number of each class
        unique, counts = np.unique(y_balanced, return_counts=True)
        assert len(unique) == 2
        assert counts[0] == counts[1]

        # Total samples should be 2 * minority_class_size
        minority_size = min(np.sum(y == 0), np.sum(y == 1))
        assert len(y_balanced) == 2 * minority_size

        # All labels should be valid
        assert all(label in [0, 1] for label in y_balanced)

    def test_undersample_preserves_features(self, imbalanced_data):
        """Test that undersampling preserves feature dimensions."""
        X, y = imbalanced_data
        original_n_features = X.shape[1]

        X_balanced, y_balanced = undersample_majority_class(X, y)

        # Feature dimension should be preserved
        assert X_balanced.shape[1] == original_n_features

        # Length of X and y should match
        assert len(X_balanced) == len(y_balanced)

    def test_undersample_random_state(self, imbalanced_data):
        """Test that random state produces reproducible results."""
        X, y = imbalanced_data

        X1, y1 = undersample_majority_class(X, y, random_state=42)
        X2, y2 = undersample_majority_class(X, y, random_state=42)

        # Should produce identical results with same random state
        np.testing.assert_array_equal(X1, X2)
        np.testing.assert_array_equal(y1, y2)

    def test_undersample_different_random_state(self, imbalanced_data):
        """Test that different random states produce different results."""
        X, y = imbalanced_data

        X1, y1 = undersample_majority_class(X, y, random_state=42)
        X2, y2 = undersample_majority_class(X, y, random_state=123)

        # Should produce different results with different random states
        # (with very high probability)
        assert not np.array_equal(X1, X2)

    def test_undersample_balanced_data(self):
        """Test undersampling already balanced data."""
        X = np.random.randn(20, 5)
        y = np.array([0] * 10 + [1] * 10)

        X_balanced, y_balanced = undersample_majority_class(X, y)

        # Should still have equal classes
        unique, counts = np.unique(y_balanced, return_counts=True)
        assert counts[0] == counts[1]

    def test_undersample_non_binary_raises_error(self):
        """Test that non-binary classification raises error."""
        X = np.random.randn(30, 5)
        y = np.array([0] * 10 + [1] * 10 + [2] * 10)  # 3 classes

        with pytest.raises(ValueError, match="Expected binary classification"):
            undersample_majority_class(X, y)

    def test_undersample_maintains_samples(self, imbalanced_data):
        """Test that undersampled data contains valid original samples."""
        X, y = imbalanced_data

        X_balanced, y_balanced = undersample_majority_class(X, y)

        # Each row in X_balanced should exist in original X
        for i in range(len(X_balanced)):
            found = False
            for j in range(len(X)):
                if np.array_equal(X_balanced[i], X[j]) and y_balanced[i] == y[j]:
                    found = True
                    break
            assert found, f"Sample {i} not found in original data"
