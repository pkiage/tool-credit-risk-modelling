"""Data preprocessing utilities for categorical encoding."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from shared import constants

if TYPE_CHECKING:
    from shared.schemas.loan import LoanApplication

# Categorical mappings based on loan schema
HOME_OWNERSHIP_MAP = {"RENT": 0, "OWN": 1, "MORTGAGE": 2, "OTHER": 3}

LOAN_INTENT_MAP = {
    "EDUCATION": 0,
    "MEDICAL": 1,
    "VENTURE": 2,
    "PERSONAL": 3,
    "DEBTCONSOLIDATION": 4,
    "HOMEIMPROVEMENT": 5,
}

LOAN_GRADE_MAP = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}

DEFAULT_ON_FILE_MAP = {"N": 0, "Y": 1}


def encode_home_ownership(
    values: list[str] | NDArray[np.str_],
) -> NDArray[np.int_]:
    """Encode home ownership categorical values to integers.

    Args:
        values: List or array of home ownership values.

    Returns:
        Array of encoded integer values.

    Raises:
        ValueError: If an unknown home ownership value is encountered.

    Example:
        >>> encode_home_ownership(["RENT", "OWN", "MORTGAGE"])
        array([0, 1, 2])
    """
    encoded = []
    for val in values:
        if val not in HOME_OWNERSHIP_MAP:
            raise ValueError(
                f"Unknown home_ownership value: {val}. "
                f"Valid values: {list(HOME_OWNERSHIP_MAP.keys())}"
            )
        encoded.append(HOME_OWNERSHIP_MAP[val])

    return np.array(encoded, dtype=np.int_)


def encode_loan_intent(values: list[str] | NDArray[np.str_]) -> NDArray[np.int_]:
    """Encode loan intent categorical values to integers.

    Args:
        values: List or array of loan intent values.

    Returns:
        Array of encoded integer values.

    Raises:
        ValueError: If an unknown loan intent value is encountered.

    Example:
        >>> encode_loan_intent(["EDUCATION", "MEDICAL"])
        array([0, 1])
    """
    encoded = []
    for val in values:
        if val not in LOAN_INTENT_MAP:
            raise ValueError(
                f"Unknown loan_intent value: {val}. "
                f"Valid values: {list(LOAN_INTENT_MAP.keys())}"
            )
        encoded.append(LOAN_INTENT_MAP[val])

    return np.array(encoded, dtype=np.int_)


def encode_loan_grade(values: list[str] | NDArray[np.str_]) -> NDArray[np.int_]:
    """Encode loan grade categorical values to integers.

    Args:
        values: List or array of loan grade values.

    Returns:
        Array of encoded integer values.

    Raises:
        ValueError: If an unknown loan grade value is encountered.

    Example:
        >>> encode_loan_grade(["A", "B", "C"])
        array([0, 1, 2])
    """
    encoded = []
    for val in values:
        if val not in LOAN_GRADE_MAP:
            raise ValueError(
                f"Unknown loan_grade value: {val}. "
                f"Valid values: {list(LOAN_GRADE_MAP.keys())}"
            )
        encoded.append(LOAN_GRADE_MAP[val])

    return np.array(encoded, dtype=np.int_)


def encode_default_on_file(values: list[str] | NDArray[np.str_]) -> NDArray[np.int_]:
    """Encode default on file categorical values to integers.

    Args:
        values: List or array of default on file values ("Y" or "N").

    Returns:
        Array of encoded integer values (0 for "N", 1 for "Y").

    Raises:
        ValueError: If an unknown value is encountered.

    Example:
        >>> encode_default_on_file(["N", "Y", "N"])
        array([0, 1, 0])
    """
    encoded = []
    for val in values:
        if val not in DEFAULT_ON_FILE_MAP:
            raise ValueError(
                f"Unknown default_on_file value: {val}. "
                f"Valid values: {list(DEFAULT_ON_FILE_MAP.keys())}"
            )
        encoded.append(DEFAULT_ON_FILE_MAP[val])

    return np.array(encoded, dtype=np.int_)


def decode_home_ownership(values: list[int] | NDArray[np.int_]) -> list[str]:
    """Decode home ownership integers back to categorical values.

    Args:
        values: List or array of encoded integer values.

    Returns:
        List of decoded string values.

    Example:
        >>> decode_home_ownership([0, 1, 2])
        ['RENT', 'OWN', 'MORTGAGE']
    """
    reverse_map = {v: k for k, v in HOME_OWNERSHIP_MAP.items()}
    return [reverse_map[int(val)] for val in values]


def decode_loan_intent(values: list[int] | NDArray[np.int_]) -> list[str]:
    """Decode loan intent integers back to categorical values.

    Args:
        values: List or array of encoded integer values.

    Returns:
        List of decoded string values.
    """
    reverse_map = {v: k for k, v in LOAN_INTENT_MAP.items()}
    return [reverse_map[int(val)] for val in values]


def decode_loan_grade(values: list[int] | NDArray[np.int_]) -> list[str]:
    """Decode loan grade integers back to categorical values.

    Args:
        values: List or array of encoded integer values.

    Returns:
        List of decoded string values.
    """
    reverse_map = {v: k for k, v in LOAN_GRADE_MAP.items()}
    return [reverse_map[int(val)] for val in values]


def undersample_majority_class(
    X: NDArray[np.float64], y: NDArray[np.int_], random_state: int = 42
) -> tuple[NDArray[np.float64], NDArray[np.int_]]:
    """Undersample the majority class to balance the dataset.

    Args:
        X: Feature matrix.
        y: Target labels (0 or 1).
        random_state: Random seed for reproducibility.

    Returns:
        Tuple of (X_resampled, y_resampled) with balanced classes.

    Example:
        >>> X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        >>> y = np.array([0, 0, 0, 1])
        >>> X_balanced, y_balanced = undersample_majority_class(X, y)
        >>> len(X_balanced)
        2
    """
    rng = np.random.RandomState(random_state)

    # Count samples in each class
    unique, counts = np.unique(y, return_counts=True)

    if len(unique) != 2:
        raise ValueError(f"Expected binary classification, got {len(unique)} classes")

    # Find minority class size
    min_samples = int(counts.min())

    # Get indices for each class
    indices_0 = np.where(y == 0)[0]
    indices_1 = np.where(y == 1)[0]

    # Undersample both to minority class size
    sampled_0 = rng.choice(indices_0, size=min_samples, replace=False)
    sampled_1 = rng.choice(indices_1, size=min_samples, replace=False)

    # Combine and shuffle
    sampled_indices = np.concatenate([sampled_0, sampled_1])
    rng.shuffle(sampled_indices)

    return X[sampled_indices], y[sampled_indices]


def loan_application_to_feature_vector(
    application: LoanApplication,
) -> NDArray[np.float64]:
    """Convert a LoanApplication to a feature vector matching constants.ALL_FEATURES.

    Derives one-hot encoding from constants.CATEGORICAL_FEATURES_ENCODED column
    names, ensuring the feature vector always stays in sync with the training
    data format.

    Args:
        application: Loan application with all required fields.

    Returns:
        Feature vector of shape (len(constants.ALL_FEATURES),).

    Example:
        >>> from shared.schemas.loan import LoanApplication
        >>> app = LoanApplication(
        ...     person_age=25, person_income=50000.0, person_emp_length=3.0,
        ...     loan_amnt=10000.0, loan_int_rate=10.5, loan_percent_income=0.2,
        ...     cb_person_cred_hist_length=5, person_home_ownership="RENT",
        ...     loan_intent="EDUCATION", loan_grade="B",
        ...     cb_person_default_on_file="N"
        ... )
        >>> features = loan_application_to_feature_vector(app)
        >>> assert features.shape == (len(constants.ALL_FEATURES),)
    """
    # Numeric features in constants.NUMERIC_FEATURES order
    numeric_values = [
        float(application.person_age),
        float(application.person_income),
        float(application.person_emp_length),
        float(application.loan_amnt),
        float(application.loan_int_rate),
        float(application.loan_percent_income),
        float(application.cb_person_cred_hist_length),
    ]

    # Map categorical field names to their application values
    field_values = {
        "person_home_ownership": application.person_home_ownership,
        "loan_intent": application.loan_intent,
        "loan_grade": application.loan_grade,
        "cb_person_default_on_file": application.cb_person_default_on_file,
    }

    # One-hot encode from CATEGORICAL_FEATURES_ENCODED column names
    # Column names follow the pattern: "{field_name}_{category_value}"
    categorical_values: list[float] = []
    for col_name in constants.CATEGORICAL_FEATURES_ENCODED:
        matched = False
        for field_name, field_value in field_values.items():
            prefix = f"{field_name}_"
            if col_name.startswith(prefix):
                category = col_name[len(prefix) :]
                categorical_values.append(1.0 if field_value == category else 0.0)
                matched = True
                break
        if not matched:
            raise ValueError(f"Unknown encoded column: {col_name}")

    return np.array(numeric_values + categorical_values, dtype=np.float64)
