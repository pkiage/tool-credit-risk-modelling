"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import type { TrainingConfig } from "@/lib/types";

interface TrainingFormProps {
	onSubmit: (config: TrainingConfig) => void;
	loading?: boolean;
}

const modelTypeOptions = [
	{ value: "logistic_regression", label: "Logistic Regression" },
	{ value: "xgboost", label: "XGBoost" },
	{ value: "random_forest", label: "Random Forest" },
];

export function TrainingForm({ onSubmit, loading = false }: TrainingFormProps) {
	const [config, setConfig] = useState<TrainingConfig>({
		model_type: "logistic_regression",
		test_size: 0.2,
		random_state: 42,
		undersample: false,
		cv_folds: 5,
	});

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		onSubmit(config);
	};

	return (
		<form onSubmit={handleSubmit} className="space-y-6">
			<Select
				label="Model Type"
				options={modelTypeOptions}
				value={config.model_type}
				onChange={(e) =>
					setConfig({ ...config, model_type: e.target.value as TrainingConfig["model_type"] })
				}
			/>

			<Slider
				label="Test Size"
				min={0.1}
				max={0.5}
				step={0.05}
				value={config.test_size}
				displayValue={`${(config.test_size * 100).toFixed(0)}%`}
				onChange={(e) =>
					setConfig({ ...config, test_size: Number(e.target.value) })
				}
			/>

			<Slider
				label="CV Folds"
				min={2}
				max={10}
				step={1}
				value={config.cv_folds}
				displayValue={String(config.cv_folds)}
				onChange={(e) =>
					setConfig({ ...config, cv_folds: Number(e.target.value) })
				}
			/>

			<div className="flex items-center gap-2">
				<input
					id="undersample"
					type="checkbox"
					className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					checked={config.undersample}
					onChange={(e) =>
						setConfig({ ...config, undersample: e.target.checked })
					}
				/>
				<label htmlFor="undersample" className="text-sm font-medium text-gray-700">
					Undersample majority class
				</label>
			</div>

			<Button type="submit" loading={loading} className="w-full">
				{loading ? "Training Model..." : "Train Model"}
			</Button>
		</form>
	);
}
