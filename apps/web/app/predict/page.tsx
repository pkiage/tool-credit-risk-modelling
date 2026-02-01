"use client";

import { useEffect, useState } from "react";
import { PredictionForm } from "@/components/forms/prediction-form";
import { Card } from "@/components/ui/card";
import { ApiClientError, api } from "@/lib/api-client";
import type { LoanApplication, ModelMetadata, PredictionResponse } from "@/lib/types";

export default function PredictPage() {
	const [models, setModels] = useState<ModelMetadata[]>([]);
	const [modelsLoading, setModelsLoading] = useState(true);
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState<PredictionResponse | null>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		api
			.listModels()
			.then(setModels)
			.catch(() => setModels([]))
			.finally(() => setModelsLoading(false));
	}, []);

	const handlePredict = async (modelId: string, application: LoanApplication) => {
		setLoading(true);
		setError(null);
		setResult(null);

		try {
			const response = await api.predict({
				model_id: modelId,
				applications: [application],
				threshold: null,
				include_probabilities: true,
			});
			setResult(response);
		} catch (err) {
			if (err instanceof ApiClientError) {
				setError(err.message);
			} else {
				setError("An unexpected error occurred");
			}
		} finally {
			setLoading(false);
		}
	};

	const prediction = result?.predictions[0];

	return (
		<div className="space-y-8">
			<div>
				<h1 className="text-2xl font-bold text-gray-900">Predict Default</h1>
				<p className="mt-1 text-gray-600">Submit a loan application to predict default risk.</p>
			</div>

			{error && (
				<div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
					{error}
				</div>
			)}

			<div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
				<div className="lg:col-span-2">
					<Card title="Loan Application">
						{modelsLoading ? (
							<p className="text-sm text-gray-500">Loading models...</p>
						) : (
							<PredictionForm models={models} onSubmit={handlePredict} loading={loading} />
						)}
					</Card>
				</div>

				<div>
					{loading && (
						<Card>
							<div className="flex items-center justify-center py-8">
								<svg
									className="h-6 w-6 animate-spin text-blue-600"
									viewBox="0 0 24 24"
									fill="none"
									role="img"
									aria-label="Predicting"
								>
									<circle
										className="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										strokeWidth="4"
									/>
									<path
										className="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
									/>
								</svg>
							</div>
						</Card>
					)}

					{prediction && result && (
						<div className="space-y-4">
							<Card>
								<div className="text-center">
									<div
										className={`inline-block rounded-full px-6 py-3 text-lg font-bold ${
											prediction.predicted_default
												? "bg-red-100 text-red-800"
												: "bg-green-100 text-green-800"
										}`}
									>
										{prediction.predicted_default ? "Default" : "No Default"}
									</div>
								</div>
							</Card>

							<Card title="Details">
								<div className="space-y-3 text-sm">
									<div className="flex justify-between">
										<span className="text-gray-500">Default Probability</span>
										<span className="font-medium">
											{(prediction.default_probability * 100).toFixed(2)}%
										</span>
									</div>
									<div className="flex justify-between">
										<span className="text-gray-500">Confidence</span>
										<span className="font-medium">{(prediction.confidence * 100).toFixed(2)}%</span>
									</div>
									<div className="flex justify-between">
										<span className="text-gray-500">Threshold</span>
										<span className="font-medium">{result.threshold.toFixed(4)}</span>
									</div>
									<div className="flex justify-between">
										<span className="text-gray-500">Model</span>
										<span className="font-medium">{result.model_type}</span>
									</div>
								</div>
							</Card>

							<Card title="Probability Bar">
								<div className="space-y-2">
									<div className="flex justify-between text-xs text-gray-500">
										<span>0%</span>
										<span>Threshold ({(result.threshold * 100).toFixed(0)}%)</span>
										<span>100%</span>
									</div>
									<div className="relative h-4 w-full overflow-hidden rounded-full bg-gray-200">
										<div
											className={`absolute left-0 top-0 h-full rounded-full transition-all ${
												prediction.predicted_default ? "bg-red-500" : "bg-green-500"
											}`}
											style={{
												width: `${prediction.default_probability * 100}%`,
											}}
										/>
										<div
											className="absolute top-0 h-full w-0.5 bg-gray-800"
											style={{ left: `${result.threshold * 100}%` }}
										/>
									</div>
								</div>
							</Card>
						</div>
					)}

					{!loading && !prediction && (
						<Card>
							<p className="text-center text-sm text-gray-500">
								Fill in the loan application form and click &quot;Get Prediction&quot; to see
								results.
							</p>
						</Card>
					)}
				</div>
			</div>
		</div>
	);
}
