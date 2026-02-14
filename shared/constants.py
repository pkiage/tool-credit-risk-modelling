"""Constants for credit risk modeling."""

from typing import Any

# Feature definitions based on cr_loan_w2.csv dataset

NUMERIC_FEATURES: list[str] = [
    "person_age",
    "person_income",
    "person_emp_length",
    "loan_amnt",
    "loan_int_rate",
    "loan_percent_income",
    "cb_person_cred_hist_length",
]

# One-hot encoded categorical features in the processed dataset
CATEGORICAL_FEATURES_ENCODED: list[str] = [
    "person_home_ownership_MORTGAGE",
    "person_home_ownership_OTHER",
    "person_home_ownership_OWN",
    "person_home_ownership_RENT",
    "loan_intent_DEBTCONSOLIDATION",
    "loan_intent_EDUCATION",
    "loan_intent_HOMEIMPROVEMENT",
    "loan_intent_MEDICAL",
    "loan_intent_PERSONAL",
    "loan_intent_VENTURE",
    "loan_grade_A",
    "loan_grade_B",
    "loan_grade_C",
    "loan_grade_D",
    "loan_grade_E",
    "loan_grade_F",
    "loan_grade_G",
    "cb_person_default_on_file_N",
    "cb_person_default_on_file_Y",
]

# Original categorical feature names (before one-hot encoding)
CATEGORICAL_FEATURES: list[str] = [
    "person_home_ownership",
    "loan_intent",
    "loan_grade",
    "cb_person_default_on_file",
]

# All feature columns (numeric + encoded categorical)
ALL_FEATURES: list[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES_ENCODED

# Feature groups: maps a logical feature name to its encoded column(s).
# Numeric features map 1:1; categorical features expand to their one-hot columns.
FEATURE_GROUPS: dict[str, list[str]] = {
    "person_age": ["person_age"],
    "person_income": ["person_income"],
    "person_emp_length": ["person_emp_length"],
    "loan_amnt": ["loan_amnt"],
    "loan_int_rate": ["loan_int_rate"],
    "loan_percent_income": ["loan_percent_income"],
    "cb_person_cred_hist_length": ["cb_person_cred_hist_length"],
    "person_home_ownership": [
        "person_home_ownership_MORTGAGE",
        "person_home_ownership_OTHER",
        "person_home_ownership_OWN",
        "person_home_ownership_RENT",
    ],
    "loan_intent": [
        "loan_intent_DEBTCONSOLIDATION",
        "loan_intent_EDUCATION",
        "loan_intent_HOMEIMPROVEMENT",
        "loan_intent_MEDICAL",
        "loan_intent_PERSONAL",
        "loan_intent_VENTURE",
    ],
    "loan_grade": [
        "loan_grade_A",
        "loan_grade_B",
        "loan_grade_C",
        "loan_grade_D",
        "loan_grade_E",
        "loan_grade_F",
        "loan_grade_G",
    ],
    "cb_person_default_on_file": [
        "cb_person_default_on_file_N",
        "cb_person_default_on_file_Y",
    ],
}

ALL_FEATURE_GROUPS: list[str] = list(FEATURE_GROUPS.keys())

# Human-readable labels for feature groups (used in Gradio UI)
FEATURE_GROUP_LABELS: dict[str, str] = {
    "person_age": "Age",
    "person_income": "Income",
    "person_emp_length": "Employment Length",
    "loan_amnt": "Loan Amount",
    "loan_int_rate": "Interest Rate",
    "loan_percent_income": "Loan % of Income",
    "cb_person_cred_hist_length": "Credit History Length",
    "person_home_ownership": "Home Ownership",
    "loan_intent": "Loan Intent",
    "loan_grade": "Loan Grade",
    "cb_person_default_on_file": "Previous Default",
}

# Target column
TARGET_COLUMN: str = "loan_status"

# Default training configuration
DEFAULT_TEST_SIZE: float = 0.2
DEFAULT_RANDOM_STATE: int = 42
DEFAULT_CV_FOLDS: int = 5

# Model types
MODEL_TYPES: list[str] = ["logistic_regression", "xgboost", "random_forest"]

# Default hyperparameters for models
LOGISTIC_REGRESSION_PARAMS: dict[str, int | float | str | None] = {
    "max_iter": 1000,
    "random_state": DEFAULT_RANDOM_STATE,
    "solver": "lbfgs",
    "penalty": "l2",
    "C": 1.0,
}

XGBOOST_PARAMS: dict[str, int | float | str | None] = {
    "learning_rate": 0.1,
    "max_depth": 7,
    "n_estimators": 100,
    "random_state": DEFAULT_RANDOM_STATE,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
}

RANDOM_FOREST_PARAMS: dict[str, int | float | str | None] = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": DEFAULT_RANDOM_STATE,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
}

# Threshold optimization
DEFAULT_THRESHOLD: float = 0.5
MIN_THRESHOLD: float = 0.0
MAX_THRESHOLD: float = 1.0

# Data validation bounds (from loan schema)
MIN_AGE: int = 18
MAX_AGE: int = 120
MIN_INCOME: float = 0.0
MIN_EMPLOYMENT_LENGTH: float = 0.0
MIN_LOAN_AMOUNT: float = 0.0
MIN_INTEREST_RATE: float = 0.0
MAX_INTEREST_RATE: float = 100.0
MIN_LOAN_PERCENT_INCOME: float = 0.0
MAX_LOAN_PERCENT_INCOME: float = 1.0
MIN_CREDIT_HISTORY_LENGTH: int = 0

# Valid categorical values
VALID_HOME_OWNERSHIP: list[str] = ["RENT", "OWN", "MORTGAGE", "OTHER"]
VALID_LOAN_INTENT: list[str] = [
    "EDUCATION",
    "MEDICAL",
    "VENTURE",
    "PERSONAL",
    "DEBTCONSOLIDATION",
    "HOMEIMPROVEMENT",
]
VALID_LOAN_GRADE: list[str] = ["A", "B", "C", "D", "E", "F", "G"]
VALID_DEFAULT_ON_FILE: list[str] = ["Y", "N"]

# Feature selection constants

# WoE/IV interpretation thresholds
IV_THRESHOLD_USELESS: float = 0.02
IV_THRESHOLD_WEAK: float = 0.1
IV_THRESHOLD_MEDIUM: float = 0.3
IV_THRESHOLD_STRONG: float = 0.5

# Boruta defaults
BORUTA_DEFAULT_N_ITERATIONS: int = 100
BORUTA_DEFAULT_CONFIDENCE_LEVEL: float = 0.95

# ---------------------------------------------------------------------------
# Synthetic data generation defaults
# ---------------------------------------------------------------------------
# Approximate real-dataset distributions for synthetic generation.
# Derived from cr_loan_w2.csv (29,459 rows).

NUMERIC_FEATURE_DEFAULTS: dict[str, dict[str, float]] = {
    "person_age": {
        "mean": 27.7001,
        "std": 6.1654,
        "min": 20.0,
        "max": 84.0,
    },
    "person_income": {
        "mean": 65803.7326,
        "std": 51331.0957,
        "min": 4000.0,
        "max": 2039784.0,
    },
    "person_emp_length": {
        "mean": 4.7584,
        "std": 3.9807,
        "min": 0.0,
        "max": 41.0,
    },
    "loan_amnt": {
        "mean": 9583.6009,
        "std": 6314.421,
        "min": 500.0,
        "max": 35000.0,
    },
    "loan_int_rate": {
        "mean": 11.0115,
        "std": 3.2405,
        "min": 5.42,
        "max": 23.22,
    },
    "loan_percent_income": {
        "mean": 0.1701,
        "std": 0.1068,
        "min": 0.0,
        "max": 0.83,
    },
    "cb_person_cred_hist_length": {
        "mean": 5.7881,
        "std": 4.0307,
        "min": 2.0,
        "max": 30.0,
    },
}

CATEGORICAL_FEATURE_DEFAULTS: dict[str, dict[str, float]] = {
    "person_home_ownership": {
        "MORTGAGE": 0.4114,
        "OTHER": 0.0032,
        "OWN": 0.08,
        "RENT": 0.5054,
    },
    "loan_intent": {
        "DEBTCONSOLIDATION": 0.1596,
        "EDUCATION": 0.1986,
        "HOMEIMPROVEMENT": 0.1117,
        "MEDICAL": 0.185,
        "PERSONAL": 0.1701,
        "VENTURE": 0.1749,
    },
    "loan_grade": {
        "A": 0.3317,
        "B": 0.3188,
        "C": 0.1978,
        "D": 0.1125,
        "E": 0.0299,
        "F": 0.0073,
        "G": 0.002,
    },
    "cb_person_default_on_file": {
        "N": 0.8231,
        "Y": 0.1769,
    },
}

# Correlation matrix for numeric features (preserves inter-feature relationships).
# Row/column order matches NUMERIC_FEATURES.
NUMERIC_CORRELATION_MATRIX: list[list[float]] = [
    # fmt: off
    [1.0, 0.1404, 0.174, 0.0558, 0.012, -0.0407, 0.8774],
    [0.1404, 1.0, 0.1616, 0.3276, -0.0011, -0.2987, 0.1217],
    [0.174, 0.1616, 1.0, 0.1092, -0.0556, -0.0601, 0.1498],
    [0.0558, 0.3276, 0.1092, 1.0, 0.1468, 0.5725, 0.0455],
    [0.012, -0.0011, -0.0556, 0.1468, 1.0, 0.1202, 0.0167],
    [-0.0407, -0.2987, -0.0601, 0.5725, 0.1202, 1.0, -0.0303],
    [0.8774, 0.1217, 0.1498, 0.0455, 0.0167, -0.0303, 1.0],
    # fmt: on
]

# Named presets for synthetic data generation.
# Keys are human-readable names; values are partial SyntheticConfig dicts.
SYNTHETIC_PRESETS: dict[str, dict[str, Any]] = {
    "Stress Test": {
        "n_samples": 5000,
        "default_rate": 0.50,
        "distributions": [
            {"feature": "person_income", "mean_shift": -15000.0, "std_scale": 1.5},
            {
                "feature": "loan_int_rate",
                "mean_shift": 4.0,
                "std_scale": 1.2,
            },
            {
                "feature": "loan_grade",
                "category_weights": {
                    "A": 0.05,
                    "B": 0.10,
                    "C": 0.20,
                    "D": 0.25,
                    "E": 0.20,
                    "F": 0.15,
                    "G": 0.05,
                },
            },
        ],
    },
    "Low Default": {"n_samples": 5000, "default_rate": 0.05},
    "Large Sample": {"n_samples": 50000, "default_rate": 0.22},
    "Balanced": {"n_samples": 5000, "default_rate": 0.50},
}

# Chart color palette (shared across all notebooks and apps)
COLOR_PRIMARY: str = "#636EFA"
COLOR_DANGER: str = "#EF553B"
COLOR_SUCCESS: str = "#00CC96"
