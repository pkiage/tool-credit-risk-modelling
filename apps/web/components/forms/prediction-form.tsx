"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import type { LoanApplication, ModelMetadata } from "@/lib/types";
import { LoanFields } from "./loan-fields";

interface PredictionFormProps {
	models: ModelMetadata[];
	onSubmit: (modelId: string, application: LoanApplication) => void;
	loading?: boolean;
}

const defaultApplication: LoanApplication = {
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

export function PredictionForm({ models, onSubmit, loading = false }: PredictionFormProps) {
	const [modelId, setModelId] = useState(models[0]?.model_id ?? "");
	const [application, setApplication] = useState<LoanApplication>(defaultApplication);

	const handleFieldChange = (field: keyof LoanApplication, value: string | number) => {
		setApplication({ ...application, [field]: value });
	};

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (!modelId) return;
		onSubmit(modelId, application);
	};

	const modelOptions = models.map((m) => ({
		value: m.model_id,
		label: `${m.model_type} (AUC: ${m.roc_auc.toFixed(3)})`,
	}));

	if (models.length === 0) {
		return (
			<div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
				No trained models available. Train a model first.
			</div>
		);
	}

	return (
		<form onSubmit={handleSubmit} className="space-y-6">
			<Select
				label="Select Model"
				options={modelOptions}
				value={modelId}
				onChange={(e) => setModelId(e.target.value)}
			/>

			<LoanFields values={application} onChange={handleFieldChange} />

			<Button type="submit" loading={loading} className="w-full">
				{loading ? "Predicting..." : "Get Prediction"}
			</Button>
		</form>
	);
}
