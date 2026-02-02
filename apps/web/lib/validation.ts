/**
 * Client-side validation matching Pydantic constraints in shared/schemas/loan.py.
 */

import type { LoanApplication } from "./types";

type ValidationErrors = Partial<Record<keyof LoanApplication, string>>;

/**
 * Validate a loan application against Pydantic schema constraints.
 * Returns an object with field-level error messages (empty if valid).
 */
export function validateLoanApplication(app: LoanApplication): ValidationErrors {
	const errors: ValidationErrors = {};

	// person_age: int, ge=18, le=120
	if (!Number.isInteger(app.person_age) || app.person_age < 18 || app.person_age > 120) {
		errors.person_age = "Age must be a whole number between 18 and 120";
	}

	// person_income: float, gt=0
	if (app.person_income <= 0) {
		errors.person_income = "Income must be greater than 0";
	}

	// person_emp_length: float, ge=0
	if (app.person_emp_length < 0) {
		errors.person_emp_length = "Employment length cannot be negative";
	}

	// loan_amnt: float, gt=0
	if (app.loan_amnt <= 0) {
		errors.loan_amnt = "Loan amount must be greater than 0";
	}

	// loan_int_rate: float, gt=0, le=100
	if (app.loan_int_rate <= 0 || app.loan_int_rate > 100) {
		errors.loan_int_rate = "Interest rate must be between 0 (exclusive) and 100";
	}

	// loan_percent_income: float, ge=0, le=1
	if (app.loan_percent_income < 0 || app.loan_percent_income > 1) {
		errors.loan_percent_income = "Loan % of income must be between 0 and 1";
	}

	// cb_person_cred_hist_length: int, ge=0
	if (!Number.isInteger(app.cb_person_cred_hist_length) || app.cb_person_cred_hist_length < 0) {
		errors.cb_person_cred_hist_length = "Credit history length must be a non-negative whole number";
	}

	return errors;
}
