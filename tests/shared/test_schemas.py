"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from shared.schemas.loan import LoanApplication, LoanDataset
from shared.schemas.metrics import ConfusionMatrix, ThresholdResult
from shared.schemas.prediction import PredictionRequest
from shared.schemas.training import TrainingConfig


class TestLoanApplication:
    """Tests for LoanApplication schema."""

    def test_valid_loan_application(self, sample_loan_application):
        """Test creating a valid loan application."""
        assert sample_loan_application.person_age == 25
        assert sample_loan_application.person_income == 50000.0
        assert sample_loan_application.loan_grade == "B"

    def test_age_validation_too_young(self):
        """Test age validation rejects too young applicants."""
        with pytest.raises(ValidationError) as exc_info:
            LoanApplication(
                person_age=17,  # Too young
                person_income=50000.0,
                person_emp_length=3.0,
                loan_amnt=10000.0,
                loan_int_rate=10.5,
                loan_percent_income=0.2,
                cb_person_cred_hist_length=5,
                person_home_ownership="RENT",
                loan_intent="EDUCATION",
                loan_grade="B",
                cb_person_default_on_file="N",
            )
        assert "person_age" in str(exc_info.value)

    def test_age_validation_too_old(self):
        """Test age validation rejects unrealistic ages."""
        with pytest.raises(ValidationError) as exc_info:
            LoanApplication(
                person_age=121,  # Too old
                person_income=50000.0,
                person_emp_length=3.0,
                loan_amnt=10000.0,
                loan_int_rate=10.5,
                loan_percent_income=0.2,
                cb_person_cred_hist_length=5,
                person_home_ownership="RENT",
                loan_intent="EDUCATION",
                loan_grade="B",
                cb_person_default_on_file="N",
            )
        assert "person_age" in str(exc_info.value)

    def test_income_validation_negative(self):
        """Test income validation rejects negative values."""
        with pytest.raises(ValidationError) as exc_info:
            LoanApplication(
                person_age=25,
                person_income=-1000.0,  # Negative
                person_emp_length=3.0,
                loan_amnt=10000.0,
                loan_int_rate=10.5,
                loan_percent_income=0.2,
                cb_person_cred_hist_length=5,
                person_home_ownership="RENT",
                loan_intent="EDUCATION",
                loan_grade="B",
                cb_person_default_on_file="N",
            )
        assert "person_income" in str(exc_info.value)

    def test_loan_percent_income_validation(self):
        """Test loan_percent_income must be between 0 and 1."""
        with pytest.raises(ValidationError) as exc_info:
            LoanApplication(
                person_age=25,
                person_income=50000.0,
                person_emp_length=3.0,
                loan_amnt=10000.0,
                loan_int_rate=10.5,
                loan_percent_income=1.5,  # Greater than 1
                cb_person_cred_hist_length=5,
                person_home_ownership="RENT",
                loan_intent="EDUCATION",
                loan_grade="B",
                cb_person_default_on_file="N",
            )
        assert "loan_percent_income" in str(exc_info.value)

    def test_invalid_home_ownership(self):
        """Test home ownership must be valid literal."""
        with pytest.raises(ValidationError) as exc_info:
            LoanApplication(
                person_age=25,
                person_income=50000.0,
                person_emp_length=3.0,
                loan_amnt=10000.0,
                loan_int_rate=10.5,
                loan_percent_income=0.2,
                cb_person_cred_hist_length=5,
                person_home_ownership="INVALID",  # Invalid value
                loan_intent="EDUCATION",
                loan_grade="B",
                cb_person_default_on_file="N",
            )
        assert "person_home_ownership" in str(exc_info.value)

    def test_loan_application_immutable(self, sample_loan_application):
        """Test loan application is immutable (frozen)."""
        with pytest.raises(ValidationError):
            sample_loan_application.person_age = 30


class TestLoanDataset:
    """Tests for LoanDataset schema."""

    def test_valid_loan_dataset(self, sample_loan_applications):
        """Test creating a valid loan dataset."""
        dataset = LoanDataset(applications=sample_loan_applications, labels=[0, 0, 1])
        assert len(dataset) == 3
        assert dataset.test_size == 0.2
        assert dataset.random_state == 42

    def test_custom_test_size(self, sample_loan_applications):
        """Test custom test size."""
        dataset = LoanDataset(
            applications=sample_loan_applications, labels=[0, 0, 1], test_size=0.3
        )
        assert dataset.test_size == 0.3

    def test_invalid_test_size_too_small(self, sample_loan_applications):
        """Test test_size validation rejects too small values."""
        with pytest.raises(ValidationError):
            LoanDataset(
                applications=sample_loan_applications,
                labels=[0, 0, 1],
                test_size=0.05,  # Too small
            )

    def test_invalid_test_size_too_large(self, sample_loan_applications):
        """Test test_size validation rejects too large values."""
        with pytest.raises(ValidationError):
            LoanDataset(
                applications=sample_loan_applications,
                labels=[0, 0, 1],
                test_size=0.6,  # Too large
            )


class TestTrainingConfig:
    """Tests for TrainingConfig schema."""

    def test_valid_training_config(self):
        """Test creating a valid training config."""
        config = TrainingConfig(model_type="logistic_regression")
        assert config.model_type == "logistic_regression"
        assert config.test_size == 0.2
        assert config.random_state == 42
        assert config.undersample is False
        assert config.cv_folds == 5

    def test_invalid_model_type(self):
        """Test model_type validation rejects invalid types."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingConfig(model_type="invalid_model")
        assert "model_type" in str(exc_info.value)

    def test_custom_cv_folds(self):
        """Test custom CV folds."""
        config = TrainingConfig(model_type="xgboost", cv_folds=10)
        assert config.cv_folds == 10

    def test_invalid_cv_folds_too_few(self):
        """Test cv_folds validation rejects too few folds."""
        with pytest.raises(ValidationError):
            TrainingConfig(model_type="xgboost", cv_folds=1)


class TestThresholdResult:
    """Tests for ThresholdResult schema."""

    def test_valid_threshold_result(self):
        """Test creating a valid threshold result."""
        result = ThresholdResult(
            threshold=0.5,
            sensitivity=0.8,
            specificity=0.7,
            youden_j=0.5,
            precision=0.75,
            f1_score=0.77,
        )
        assert result.threshold == 0.5
        assert result.youden_j == 0.5

    def test_threshold_bounds(self):
        """Test threshold must be between 0 and 1."""
        with pytest.raises(ValidationError):
            ThresholdResult(
                threshold=1.5,  # Out of bounds
                sensitivity=0.8,
                specificity=0.7,
                youden_j=0.5,
                precision=0.75,
                f1_score=0.77,
            )


class TestConfusionMatrix:
    """Tests for ConfusionMatrix schema."""

    def test_valid_confusion_matrix(self):
        """Test creating a valid confusion matrix."""
        cm = ConfusionMatrix(
            matrix=[[50, 10], [5, 35]],
            true_negatives=50,
            false_positives=10,
            false_negatives=5,
            true_positives=35,
        )
        assert cm.true_positives == 35
        assert cm.true_negatives == 50
        assert cm.false_positives == 10
        assert cm.false_negatives == 5

    def test_negative_values_rejected(self):
        """Test confusion matrix rejects negative values."""
        with pytest.raises(ValidationError):
            ConfusionMatrix(
                matrix=[[50, 10], [5, 35]],
                true_negatives=-1,  # Negative
                false_positives=10,
                false_negatives=5,
                true_positives=35,
            )


class TestPredictionRequest:
    """Tests for PredictionRequest schema."""

    def test_valid_prediction_request(self, sample_loan_applications):
        """Test creating a valid prediction request."""
        request = PredictionRequest(
            model_id="model_123", applications=sample_loan_applications
        )
        assert request.model_id == "model_123"
        assert len(request.applications) == 3
        assert request.threshold is None
        assert request.include_probabilities is True

    def test_empty_applications_rejected(self):
        """Test prediction request requires at least one application."""
        with pytest.raises(ValidationError):
            PredictionRequest(model_id="model_123", applications=[])

    def test_custom_threshold(self, sample_loan_applications):
        """Test custom threshold in prediction request."""
        request = PredictionRequest(
            model_id="model_123",
            applications=sample_loan_applications,
            threshold=0.7,
        )
        assert request.threshold == 0.7

    def test_invalid_threshold(self, sample_loan_applications):
        """Test threshold validation."""
        with pytest.raises(ValidationError):
            PredictionRequest(
                model_id="model_123",
                applications=sample_loan_applications,
                threshold=1.5,  # Out of bounds
            )
