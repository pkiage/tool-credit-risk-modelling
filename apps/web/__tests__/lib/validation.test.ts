import { describe, expect, it } from "vitest";
import type { LoanApplication } from "@/lib/types";
import { validateLoanApplication } from "@/lib/validation";

const validApplication: LoanApplication = {
	person_age: 30,
	person_income: 50000,
	person_emp_length: 5,
	loan_amnt: 10000,
	loan_int_rate: 10.5,
	loan_percent_income: 0.2,
	cb_person_cred_hist_length: 5,
	person_home_ownership: "RENT",
	loan_intent: "PERSONAL",
	loan_grade: "B",
	cb_person_default_on_file: "N",
};

describe("validateLoanApplication", () => {
	it("returns no errors for a valid application", () => {
		const errors = validateLoanApplication(validApplication);
		expect(Object.keys(errors)).toHaveLength(0);
	});

	describe("person_age", () => {
		it("rejects age below 18", () => {
			const errors = validateLoanApplication({ ...validApplication, person_age: 17 });
			expect(errors.person_age).toBeDefined();
		});

		it("rejects age above 120", () => {
			const errors = validateLoanApplication({ ...validApplication, person_age: 121 });
			expect(errors.person_age).toBeDefined();
		});

		it("rejects non-integer age", () => {
			const errors = validateLoanApplication({ ...validApplication, person_age: 30.5 });
			expect(errors.person_age).toBeDefined();
		});

		it("accepts boundary value 18", () => {
			const errors = validateLoanApplication({ ...validApplication, person_age: 18 });
			expect(errors.person_age).toBeUndefined();
		});

		it("accepts boundary value 120", () => {
			const errors = validateLoanApplication({ ...validApplication, person_age: 120 });
			expect(errors.person_age).toBeUndefined();
		});
	});

	describe("person_income", () => {
		it("rejects zero income", () => {
			const errors = validateLoanApplication({ ...validApplication, person_income: 0 });
			expect(errors.person_income).toBeDefined();
		});

		it("rejects negative income", () => {
			const errors = validateLoanApplication({ ...validApplication, person_income: -1 });
			expect(errors.person_income).toBeDefined();
		});

		it("accepts positive income", () => {
			const errors = validateLoanApplication({ ...validApplication, person_income: 0.01 });
			expect(errors.person_income).toBeUndefined();
		});
	});

	describe("person_emp_length", () => {
		it("rejects negative employment length", () => {
			const errors = validateLoanApplication({ ...validApplication, person_emp_length: -1 });
			expect(errors.person_emp_length).toBeDefined();
		});

		it("accepts zero employment length", () => {
			const errors = validateLoanApplication({ ...validApplication, person_emp_length: 0 });
			expect(errors.person_emp_length).toBeUndefined();
		});
	});

	describe("loan_amnt", () => {
		it("rejects zero loan amount", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_amnt: 0 });
			expect(errors.loan_amnt).toBeDefined();
		});

		it("rejects negative loan amount", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_amnt: -100 });
			expect(errors.loan_amnt).toBeDefined();
		});
	});

	describe("loan_int_rate", () => {
		it("rejects zero interest rate", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_int_rate: 0 });
			expect(errors.loan_int_rate).toBeDefined();
		});

		it("rejects rate above 100", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_int_rate: 100.1 });
			expect(errors.loan_int_rate).toBeDefined();
		});

		it("accepts rate at 100", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_int_rate: 100 });
			expect(errors.loan_int_rate).toBeUndefined();
		});

		it("accepts small positive rate", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_int_rate: 0.01 });
			expect(errors.loan_int_rate).toBeUndefined();
		});
	});

	describe("loan_percent_income", () => {
		it("rejects negative value", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_percent_income: -0.1 });
			expect(errors.loan_percent_income).toBeDefined();
		});

		it("rejects value above 1", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_percent_income: 1.1 });
			expect(errors.loan_percent_income).toBeDefined();
		});

		it("accepts boundary value 0", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_percent_income: 0 });
			expect(errors.loan_percent_income).toBeUndefined();
		});

		it("accepts boundary value 1", () => {
			const errors = validateLoanApplication({ ...validApplication, loan_percent_income: 1 });
			expect(errors.loan_percent_income).toBeUndefined();
		});
	});

	describe("cb_person_cred_hist_length", () => {
		it("rejects negative value", () => {
			const errors = validateLoanApplication({
				...validApplication,
				cb_person_cred_hist_length: -1,
			});
			expect(errors.cb_person_cred_hist_length).toBeDefined();
		});

		it("rejects non-integer value", () => {
			const errors = validateLoanApplication({
				...validApplication,
				cb_person_cred_hist_length: 2.5,
			});
			expect(errors.cb_person_cred_hist_length).toBeDefined();
		});

		it("accepts zero", () => {
			const errors = validateLoanApplication({
				...validApplication,
				cb_person_cred_hist_length: 0,
			});
			expect(errors.cb_person_cred_hist_length).toBeUndefined();
		});
	});

	it("returns multiple errors for multiple invalid fields", () => {
		const errors = validateLoanApplication({
			...validApplication,
			person_age: 10,
			person_income: -1,
			loan_amnt: 0,
		});
		expect(Object.keys(errors)).toHaveLength(3);
		expect(errors.person_age).toBeDefined();
		expect(errors.person_income).toBeDefined();
		expect(errors.loan_amnt).toBeDefined();
	});
});
