"""Loan application and dataset schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class LoanApplication(BaseModel):
    """A loan application with all required features for credit risk prediction.

    Attributes:
        person_age: Age of the loan applicant (18-120 years).
        person_income: Annual income of the applicant (must be positive).
        person_emp_length: Length of employment in years (non-negative).
        loan_amnt: Requested loan amount (must be positive).
        loan_int_rate: Interest rate percentage (0-100).
        loan_percent_income: Loan amount as percentage of income (0-1).
        cb_person_cred_hist_length: Length of credit history in years (non-negative).
        person_home_ownership: Type of home ownership.
        loan_intent: Purpose of the loan.
        loan_grade: Loan grade assigned by credit bureau.
        cb_person_default_on_file: Whether person has previous defaults on file.
    """

    person_age: int = Field(ge=18, le=120, description="Age of the applicant")
    person_income: float = Field(gt=0, description="Annual income in dollars")
    person_emp_length: float = Field(ge=0, description="Employment length in years")
    loan_amnt: float = Field(gt=0, description="Requested loan amount")
    loan_int_rate: float = Field(gt=0, le=100, description="Interest rate percentage")
    loan_percent_income: float = Field(
        ge=0, le=1, description="Loan amount as fraction of income"
    )
    cb_person_cred_hist_length: int = Field(
        ge=0, description="Credit history length in years"
    )
    person_home_ownership: Literal["RENT", "OWN", "MORTGAGE", "OTHER"] = Field(
        description="Home ownership status"
    )
    loan_intent: Literal[
        "EDUCATION",
        "MEDICAL",
        "VENTURE",
        "PERSONAL",
        "DEBTCONSOLIDATION",
        "HOMEIMPROVEMENT",
    ] = Field(description="Purpose of loan")
    loan_grade: Literal["A", "B", "C", "D", "E", "F", "G"] = Field(
        description="Credit grade"
    )
    cb_person_default_on_file: Literal["Y", "N"] = Field(
        description="Previous default indicator"
    )

    model_config = {"frozen": True}


class LoanDataset(BaseModel):
    """A collection of loan applications with labels for training/evaluation.

    Attributes:
        applications: List of loan applications.
        labels: List of loan status labels (0=paid, 1=default) corresponding
            to applications.
        test_size: Fraction of data reserved for testing (0.1-0.5).
        random_state: Random seed for reproducibility.
    """

    applications: list[LoanApplication]
    labels: list[int] = Field(description="0=paid, 1=default")
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    random_state: int = Field(default=42)

    def __len__(self) -> int:
        """Return number of loan applications in dataset."""
        return len(self.applications)
