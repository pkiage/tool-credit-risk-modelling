"use client";

import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { LoanApplication } from "@/lib/types";

interface LoanFieldsProps {
	values: LoanApplication;
	onChange: (field: keyof LoanApplication, value: string | number) => void;
	errors?: Partial<Record<keyof LoanApplication, string>>;
}

const homeOwnershipOptions = [
	{ value: "RENT", label: "Rent" },
	{ value: "OWN", label: "Own" },
	{ value: "MORTGAGE", label: "Mortgage" },
	{ value: "OTHER", label: "Other" },
];

const loanIntentOptions = [
	{ value: "EDUCATION", label: "Education" },
	{ value: "MEDICAL", label: "Medical" },
	{ value: "VENTURE", label: "Venture" },
	{ value: "PERSONAL", label: "Personal" },
	{ value: "DEBTCONSOLIDATION", label: "Debt Consolidation" },
	{ value: "HOMEIMPROVEMENT", label: "Home Improvement" },
];

const loanGradeOptions = [
	{ value: "A", label: "A" },
	{ value: "B", label: "B" },
	{ value: "C", label: "C" },
	{ value: "D", label: "D" },
	{ value: "E", label: "E" },
	{ value: "F", label: "F" },
	{ value: "G", label: "G" },
];

const defaultOnFileOptions = [
	{ value: "N", label: "No" },
	{ value: "Y", label: "Yes" },
];

export function LoanFields({ values, onChange, errors = {} }: LoanFieldsProps) {
	return (
		<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
			<Input
				label="Age"
				type="number"
				min={18}
				max={120}
				value={values.person_age}
				onChange={(e) => onChange("person_age", Number(e.target.value))}
				error={errors.person_age}
			/>
			<Input
				label="Annual Income"
				type="number"
				min={1}
				step={1000}
				value={values.person_income}
				onChange={(e) => onChange("person_income", Number(e.target.value))}
				error={errors.person_income}
			/>
			<Input
				label="Employment Length (years)"
				type="number"
				min={0}
				step={0.5}
				value={values.person_emp_length}
				onChange={(e) => onChange("person_emp_length", Number(e.target.value))}
				error={errors.person_emp_length}
			/>
			<Input
				label="Loan Amount"
				type="number"
				min={1}
				step={500}
				value={values.loan_amnt}
				onChange={(e) => onChange("loan_amnt", Number(e.target.value))}
				error={errors.loan_amnt}
			/>
			<Input
				label="Interest Rate (%)"
				type="number"
				min={0.01}
				max={100}
				step={0.01}
				value={values.loan_int_rate}
				onChange={(e) => onChange("loan_int_rate", Number(e.target.value))}
				error={errors.loan_int_rate}
			/>
			<Input
				label="Loan % of Income"
				type="number"
				min={0}
				max={1}
				step={0.01}
				value={values.loan_percent_income}
				onChange={(e) => onChange("loan_percent_income", Number(e.target.value))}
				error={errors.loan_percent_income}
			/>
			<Input
				label="Credit History Length (years)"
				type="number"
				min={0}
				value={values.cb_person_cred_hist_length}
				onChange={(e) => onChange("cb_person_cred_hist_length", Number(e.target.value))}
				error={errors.cb_person_cred_hist_length}
			/>
			<Select
				label="Home Ownership"
				options={homeOwnershipOptions}
				value={values.person_home_ownership}
				onChange={(e) => onChange("person_home_ownership", e.target.value)}
				error={errors.person_home_ownership}
			/>
			<Select
				label="Loan Intent"
				options={loanIntentOptions}
				value={values.loan_intent}
				onChange={(e) => onChange("loan_intent", e.target.value)}
				error={errors.loan_intent}
			/>
			<Select
				label="Loan Grade"
				options={loanGradeOptions}
				value={values.loan_grade}
				onChange={(e) => onChange("loan_grade", e.target.value)}
				error={errors.loan_grade}
			/>
			<Select
				label="Default on File"
				options={defaultOnFileOptions}
				value={values.cb_person_default_on_file}
				onChange={(e) => onChange("cb_person_default_on_file", e.target.value)}
				error={errors.cb_person_default_on_file}
			/>
		</div>
	);
}
