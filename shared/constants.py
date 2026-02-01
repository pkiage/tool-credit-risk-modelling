"""Constants for credit risk modeling."""

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

# Chart color palette (shared across all notebooks and apps)
COLOR_PRIMARY: str = "#636EFA"
COLOR_DANGER: str = "#EF553B"
COLOR_SUCCESS: str = "#00CC96"
