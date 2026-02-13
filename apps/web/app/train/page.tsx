"use client";

import { useState } from "react";
import { CalibrationPlot } from "@/components/charts/calibration-plot";
import { ConfusionMatrixChart } from "@/components/charts/confusion-matrix";
import { ROCCurve } from "@/components/charts/roc-curve";
import { TrainingForm } from "@/components/forms/training-form";
import { Card } from "@/components/ui/card";
import { Table } from "@/components/ui/table";
import { ApiClientError, api } from "@/lib/api-client";
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
				<h1 className="text-2xl font-bold text-foreground">Train Model</h1>
				<p className="mt-1 text-foreground-secondary">Configure and train a credit risk model.</p>
			</div>

			<div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
				<div>
					<Card title="Configuration">
						<TrainingForm onSubmit={handleTrain} loading={loading} />
					</Card>
				</div>

				<div className="space-y-6 lg:col-span-2">
					{error && (
						<div
							className="rounded-lg border border-danger bg-red-50 dark:bg-red-950 p-4 text-sm text-red-800 dark:text-red-200"
							role="alert"
							aria-live="polite"
						>
							<p className="font-semibold">Training Failed</p>
							<p className="mt-1">{error}</p>
							<p className="mt-2 text-xs opacity-75">
								API URL: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
							</p>
						</div>
					)}

					{loading && (
						<Card>
							<div className="flex items-center justify-center py-12">
								<div className="text-center">
									<svg
										className="mx-auto h-8 w-8 animate-spin text-primary"
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
									<p className="mt-4 text-sm text-foreground-secondary">Training model...</p>
								</div>
							</div>
						</Card>
					)}

					{result && (
						<>
							<Card title="Training Summary">
								<div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
									<div className="min-w-0">
										<span className="text-foreground-muted">Model ID</span>
										<p className="truncate font-mono text-xs" title={result.model_id}>
											{result.model_id.slice(0, 8)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Type</span>
										<p className="font-medium">{result.model_type}</p>
									</div>
									<div>
										<span className="text-foreground-muted">Optimal Threshold</span>
										<p className="font-medium">{result.optimal_threshold.toFixed(4)}</p>
									</div>
									<div>
										<span className="text-foreground-muted">Training Time</span>
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
										<span className="text-foreground-muted">Threshold</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.threshold.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Sensitivity</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.sensitivity.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Specificity</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.specificity.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Youden&apos;s J</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.youden_j.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Precision</span>
										<p className="font-medium">
											{result.metrics.threshold_analysis.precision.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">F1 Score</span>
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
