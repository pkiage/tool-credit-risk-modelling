"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Table } from "@/components/ui/table";
import { TrainingForm } from "@/components/forms/training-form";
import { ROCCurve } from "@/components/charts/roc-curve";
import { ConfusionMatrixChart } from "@/components/charts/confusion-matrix";
import { CalibrationPlot } from "@/components/charts/calibration-plot";
import { api, ApiClientError } from "@/lib/api-client";
import type { TrainingConfig, TrainingResult } from "@/lib/types";

export default function TrainPage() {
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState<TrainingResult | null>(null);
	const [error, setError] = useState<string | null>(null);

	const handleTrain = async (config: TrainingConfig) => {
		setLoading(true);
		setError(null);
		setResult(null);

		try {
			const trainingResult = await api.train(config);
			setResult(trainingResult);
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

	const metricsData = result
		? [
				{
					metric: "Accuracy",
					value: result.metrics.accuracy.toFixed(4),
				},
				{
					metric: "Precision",
					value: result.metrics.precision.toFixed(4),
				},
				{
					metric: "Recall",
					value: result.metrics.recall.toFixed(4),
				},
				{
					metric: "F1 Score",
					value: result.metrics.f1_score.toFixed(4),
				},
				{
					metric: "ROC AUC",
					value: result.metrics.roc_auc.toFixed(4),
				},
			]
		: [];

	const featureImportanceData = result?.feature_importance
		? Object.entries(result.feature_importance)
				.sort(([, a], [, b]) => b - a)
				.map(([feature, importance]) => ({
					feature,
					importance: importance.toFixed(4),
				}))
		: [];

	return (
		<div className="space-y-8">
			<div>
				<h1 className="text-2xl font-bold text-gray-900">Train Model</h1>
				<p className="mt-1 text-gray-600">
					Configure and train a credit risk model.
				</p>
			</div>

			<div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
				<div>
					<Card title="Configuration">
						<TrainingForm onSubmit={handleTrain} loading={loading} />
					</Card>
				</div>

				<div className="space-y-6 lg:col-span-2">
					{error && (
						<div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
							{error}
						</div>
					)}

					{loading && (
						<Card>
							<div className="flex items-center justify-center py-12">
								<div className="text-center">
									<svg
										className="mx-auto h-8 w-8 animate-spin text-blue-600"
										viewBox="0 0 24 24"
										fill="none"
										role="img"
										aria-label="Training in progress"
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
									<p className="mt-4 text-sm text-gray-600">Training model...</p>
								</div>
							</div>
						</Card>
					)}

					{result && (
						<>
							<Card title="Training Summary">
								<div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
									<div>
										<span className="text-gray-500">Model ID</span>
										<p className="font-mono text-xs">{result.model_id}</p>
									</div>
									<div>
										<span className="text-gray-500">Type</span>
										<p className="font-medium">{result.model_type}</p>
									</div>
									<div>
										<span className="text-gray-500">Optimal Threshold</span>
										<p className="font-medium">{result.optimal_threshold.toFixed(4)}</p>
									</div>
									<div>
										<span className="text-gray-500">Training Time</span>
										<p className="font-medium">{result.training_time_seconds.toFixed(2)}s</p>
									</div>
								</div>
							</Card>

							<Card title="Metrics">
								<Table
									columns={[
										{ key: "metric", header: "Metric" },
										{ key: "value", header: "Value" },
									]}
									data={metricsData as Record<string, unknown>[]}
								/>
							</Card>

							<Card title="ROC Curve">
								<ROCCurve
									data={result.metrics.roc_curve}
									label={`${result.model_type} (AUC: ${result.metrics.roc_auc.toFixed(3)})`}
								/>
							</Card>

							<Card title="Confusion Matrix">
								<ConfusionMatrixChart data={result.metrics.confusion_matrix} />
							</Card>

							<Card title="Threshold Analysis">
								<div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
									<div>
										<span className="text-gray-500">Threshold</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.threshold.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-gray-500">Sensitivity</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.sensitivity.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-gray-500">Specificity</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.specificity.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-gray-500">Youden&apos;s J</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.youden_j.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-gray-500">Precision</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.precision.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-gray-500">F1 Score</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.f1_score.toFixed(4)}
										</p>
									</div>
								</div>
							</Card>

							{result.metrics.calibration_curve && (
								<Card title="Calibration Plot">
									<CalibrationPlot data={result.metrics.calibration_curve} />
								</Card>
							)}

							{featureImportanceData.length > 0 && (
								<Card title="Feature Importance">
									<Table
										columns={[
											{ key: "feature", header: "Feature" },
											{ key: "importance", header: "Importance" },
										]}
										data={featureImportanceData as Record<string, unknown>[]}
									/>
								</Card>
							)}
						</>
					)}
				</div>
			</div>
		</div>
	);
}
