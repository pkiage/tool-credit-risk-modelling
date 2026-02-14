"use client";

import { useState } from "react";
import { CalibrationPlot } from "@/components/charts/calibration-plot";
import { ConfusionMatrixChart } from "@/components/charts/confusion-matrix";
import { ROCCurve } from "@/components/charts/roc-curve";
import { SyntheticForm } from "@/components/forms/synthetic-form";
import { TrainingForm } from "@/components/forms/training-form";
import { Card } from "@/components/ui/card";
import { Table } from "@/components/ui/table";
import { ApiClientError, api } from "@/lib/api-client";
import type {
	SyntheticConfig,
	SyntheticGenerateResponse,
	TrainingConfig,
	TrainingResult,
} from "@/lib/types";

export default function SyntheticPage() {
	const [generating, setGenerating] = useState(false);
	const [generated, setGenerated] = useState<SyntheticGenerateResponse | null>(null);
	const [training, setTraining] = useState(false);
	const [trainResult, setTrainResult] = useState<TrainingResult | null>(null);
	const [error, setError] = useState<string | null>(null);

	const handleGenerate = async (config: SyntheticConfig) => {
		setGenerating(true);
		setError(null);
		setGenerated(null);
		setTrainResult(null);

		try {
			const result = await api.generateSynthetic(config);
			setGenerated(result);
		} catch (err) {
			if (err instanceof ApiClientError) {
				setError(err.message);
			} else {
				setError("An unexpected error occurred during generation");
			}
		} finally {
			setGenerating(false);
		}
	};

	const handleTrain = async (config: TrainingConfig) => {
		if (!generated) return;
		setTraining(true);
		setError(null);
		setTrainResult(null);

		try {
			const result = await api.train({
				...config,
				dataset_id: generated.dataset_id,
			});
			setTrainResult(result);
		} catch (err) {
			if (err instanceof ApiClientError) {
				setError(err.message);
			} else {
				setError("An unexpected error occurred during training");
			}
		} finally {
			setTraining(false);
		}
	};

	const summaryStatsData = generated
		? Object.entries(generated.metadata.summary_stats).map(([feature, stats]) => ({
				feature,
				mean: stats.mean?.toFixed(4) ?? "-",
				std: stats.std?.toFixed(4) ?? "-",
				min: stats.min?.toFixed(4) ?? "-",
				max: stats.max?.toFixed(4) ?? "-",
			}))
		: [];

	const metricsData = trainResult
		? [
				{ metric: "Accuracy", value: trainResult.metrics.accuracy.toFixed(4) },
				{ metric: "Precision", value: trainResult.metrics.precision.toFixed(4) },
				{ metric: "Recall", value: trainResult.metrics.recall.toFixed(4) },
				{ metric: "F1 Score", value: trainResult.metrics.f1_score.toFixed(4) },
				{ metric: "ROC AUC", value: trainResult.metrics.roc_auc.toFixed(4) },
			]
		: [];

	const featureImportanceData = trainResult?.feature_importance
		? Object.entries(trainResult.feature_importance)
				.sort(([, a], [, b]) => b - a)
				.map(([feature, importance]) => ({
					feature,
					importance: importance.toFixed(4),
				}))
		: [];

	return (
		<div className="space-y-8">
			<div>
				<h1 className="text-2xl font-bold text-foreground">Synthetic Data Generator</h1>
				<p className="mt-1 text-foreground-secondary">
					Generate synthetic datasets and train models on them.
				</p>
			</div>

			<div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
				<div className="space-y-6">
					<Card title="Generation Config">
						<SyntheticForm onGenerate={handleGenerate} loading={generating} />
					</Card>

					{generated && (
						<Card title="Train on Synthetic Data">
							<div className="mb-4">
								<span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
									Synthetic
								</span>
								<span className="ml-2 text-sm text-foreground-secondary">
									Dataset: {generated.dataset_id.slice(0, 8)}
								</span>
							</div>
							<TrainingForm onSubmit={handleTrain} loading={training} />
						</Card>
					)}
				</div>

				<div className="space-y-6 lg:col-span-2">
					{error && (
						<div
							className="rounded-lg border border-danger bg-red-50 p-4 text-sm text-red-800 dark:bg-red-950 dark:text-red-200"
							role="alert"
							aria-live="polite"
						>
							<p className="font-semibold">Error</p>
							<p className="mt-1">{error}</p>
						</div>
					)}

					{generating && (
						<Card>
							<div className="flex items-center justify-center py-12">
								<div className="text-center">
									<svg
										className="mx-auto h-8 w-8 animate-spin text-primary"
										viewBox="0 0 24 24"
										fill="none"
										role="img"
										aria-label="Generating synthetic data"
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
									<p className="mt-4 text-sm text-foreground-secondary">
										Generating synthetic data...
									</p>
								</div>
							</div>
						</Card>
					)}

					{generated && (
						<Card title="Generated Dataset">
							<div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
								<div>
									<span className="text-foreground-muted">Dataset ID</span>
									<p className="truncate font-mono text-xs" title={generated.dataset_id}>
										{generated.dataset_id.slice(0, 8)}
									</p>
								</div>
								<div>
									<span className="text-foreground-muted">Samples</span>
									<p className="font-medium">{generated.metadata.n_samples.toLocaleString()}</p>
								</div>
								<div>
									<span className="text-foreground-muted">Features</span>
									<p className="font-medium">{generated.metadata.n_features}</p>
								</div>
								<div>
									<span className="text-foreground-muted">Actual Default Rate</span>
									<p className="font-medium">
										{(generated.metadata.default_rate_actual * 100).toFixed(1)}%
									</p>
								</div>
							</div>
						</Card>
					)}

					{generated && summaryStatsData.length > 0 && (
						<Card title="Summary Statistics">
							<Table
								columns={[
									{ key: "feature", header: "Feature" },
									{ key: "mean", header: "Mean" },
									{ key: "std", header: "Std" },
									{ key: "min", header: "Min" },
									{ key: "max", header: "Max" },
								]}
								data={summaryStatsData as Record<string, unknown>[]}
							/>
						</Card>
					)}

					{training && (
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
									<p className="mt-4 text-sm text-foreground-secondary">
										Training model on synthetic data...
									</p>
								</div>
							</div>
						</Card>
					)}

					{trainResult && (
						<>
							<Card title="Training Summary">
								<div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
									<div className="min-w-0">
										<span className="text-foreground-muted">Model ID</span>
										<p className="truncate font-mono text-xs" title={trainResult.model_id}>
											{trainResult.model_id.slice(0, 8)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Type</span>
										<p className="font-medium">{trainResult.model_type}</p>
									</div>
									<div>
										<span className="text-foreground-muted">Optimal Threshold</span>
										<p className="font-medium">{trainResult.optimal_threshold.toFixed(4)}</p>
									</div>
									<div>
										<span className="text-foreground-muted">Training Time</span>
										<p className="font-medium">{trainResult.training_time_seconds.toFixed(2)}s</p>
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
									data={trainResult.metrics.roc_curve}
									label={`${trainResult.model_type} (AUC: ${trainResult.metrics.roc_auc.toFixed(3)})`}
								/>
							</Card>

							<Card title="Confusion Matrix">
								<ConfusionMatrixChart data={trainResult.metrics.confusion_matrix} />
							</Card>

							<Card title="Threshold Analysis">
								<div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
									<div>
										<span className="text-foreground-muted">Threshold</span>
										<p className="font-medium">
											{trainResult.metrics.threshold_analysis.threshold.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Sensitivity</span>
										<p className="font-medium">
											{trainResult.metrics.threshold_analysis.sensitivity.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Specificity</span>
										<p className="font-medium">
											{trainResult.metrics.threshold_analysis.specificity.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Youden&apos;s J</span>
										<p className="font-medium">
											{trainResult.metrics.threshold_analysis.youden_j.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">Precision</span>
										<p className="font-medium">
											{trainResult.metrics.threshold_analysis.precision.toFixed(4)}
										</p>
									</div>
									<div>
										<span className="text-foreground-muted">F1 Score</span>
										<p className="font-medium">
											{trainResult.metrics.threshold_analysis.f1_score.toFixed(4)}
										</p>
									</div>
								</div>
							</Card>

							{trainResult.metrics.calibration_curve && (
								<Card title="Calibration Plot">
									<CalibrationPlot data={trainResult.metrics.calibration_curve} />
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
