"use client";

import { useEffect, useState } from "react";
import { MetricsBar } from "@/components/charts/metrics-bar";
import { MultiROCCurve } from "@/components/charts/roc-curve";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Table } from "@/components/ui/table";
import { ApiClientError, api } from "@/lib/api-client";
import type { ModelMetadata, TrainingResult } from "@/lib/types";

const COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"];

type CompareMode = "stored" | "retrain";

export default function ComparePage() {
	const [models, setModels] = useState<ModelMetadata[]>([]);
	const [modelsLoading, setModelsLoading] = useState(true);
	const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
	const [results, setResults] = useState<Map<string, TrainingResult>>(new Map());
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [mode, setMode] = useState<CompareMode>("stored");
	const [unavailableIds, setUnavailableIds] = useState<Set<string>>(new Set());

	useEffect(() => {
		api
			.listModels()
			.then(setModels)
			.catch(() => setModels([]))
			.finally(() => setModelsLoading(false));
	}, []);

	const toggleModel = (modelId: string) => {
		setSelectedIds((prev) => {
			const next = new Set(prev);
			if (next.has(modelId)) {
				next.delete(modelId);
			} else {
				next.add(modelId);
			}
			return next;
		});
	};

	const handleCompare = async () => {
		if (selectedIds.size === 0) return;
		setLoading(true);
		setError(null);
		setUnavailableIds(new Set());

		try {
			if (mode === "stored") {
				await fetchStoredResults();
			} else {
				await retrainModels();
			}
		} catch (err) {
			if (err instanceof ApiClientError) {
				setError(err.message);
			} else {
				setError("Failed to load model comparison data");
			}
		} finally {
			setLoading(false);
		}
	};

	const fetchStoredResults = async () => {
		const promises = Array.from(selectedIds).map(async (id) => {
			try {
				const result = await api.getModelResults(id);
				return [id, result] as const;
			} catch {
				return [id, null] as const;
			}
		});

		const entries = await Promise.all(promises);
		const newResults = new Map<string, TrainingResult>();
		const missing = new Set<string>();

		for (const [id, result] of entries) {
			if (result) {
				newResults.set(id, result);
			} else {
				missing.add(id);
			}
		}

		setResults(newResults);
		setUnavailableIds(missing);

		if (missing.size > 0 && newResults.size === 0) {
			setError(
				"No stored results available for the selected models. Try using Re-train mode instead.",
			);
		}
	};

	const retrainModels = async () => {
		const promises = Array.from(selectedIds).map(async (id) => {
			const model = models.find((m) => m.model_id === id);
			if (!model) return null;

			const result = await api.train({
				model_type: model.model_type as TrainingResult["training_config"]["model_type"],
				test_size: 0.2,
				random_state: 42,
				undersample: false,
				cv_folds: 5,
			});
			return [id, result] as const;
		});

		const entries = await Promise.all(promises);
		const newResults = new Map<string, TrainingResult>();
		for (const entry of entries) {
			if (entry) {
				newResults.set(entry[0], entry[1]);
			}
		}
		setResults(newResults);
	};

	const selectedResults = Array.from(results.entries());

	const metricsBarData = selectedResults.map(([id, r]) => ({
		name: `${r.model_type} (${id.slice(0, 8)})`,
		accuracy: r.metrics.accuracy,
		precision: r.metrics.precision,
		recall: r.metrics.recall,
		f1_score: r.metrics.f1_score,
		roc_auc: r.metrics.roc_auc,
	}));

	const rocCurves = selectedResults.map(([, r], idx) => ({
		data: r.metrics.roc_curve,
		label: `${r.model_type} (AUC: ${r.metrics.roc_auc.toFixed(3)})`,
		color: COLORS[idx % COLORS.length],
	}));

	const comparisonTableData = selectedResults.map(([id, r]) => ({
		model_id: id.slice(0, 8),
		model_type: r.model_type,
		accuracy: r.metrics.accuracy.toFixed(4),
		precision: r.metrics.precision.toFixed(4),
		recall: r.metrics.recall.toFixed(4),
		f1_score: r.metrics.f1_score.toFixed(4),
		roc_auc: r.metrics.roc_auc.toFixed(4),
		threshold: r.optimal_threshold.toFixed(4),
	}));

	if (modelsLoading) {
		return (
			<div className="flex items-center justify-center py-12">
				<p className="text-gray-500">Loading models...</p>
			</div>
		);
	}

	if (models.length === 0) {
		return (
			<div className="space-y-4">
				<h1 className="text-2xl font-bold text-gray-900">Compare Models</h1>
				<Card>
					<div className="py-8 text-center">
						<p className="text-gray-500">No trained models available.</p>
						<p className="mt-2 text-sm text-gray-400">
							Train some models first, then come back to compare them.
						</p>
					</div>
				</Card>
			</div>
		);
	}

	return (
		<div className="space-y-8">
			<div>
				<h1 className="text-2xl font-bold text-gray-900">Compare Models</h1>
				<p className="mt-1 text-gray-600">Select models to compare their performance metrics.</p>
			</div>

			{error && (
				<div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
					{error}
				</div>
			)}

			<Card title="Select Models">
				<div className="space-y-2">
					{models.map((model) => (
						<label
							key={model.model_id}
							className="flex cursor-pointer items-center gap-3 rounded-md border border-gray-100 px-4 py-2 hover:bg-gray-50"
						>
							<input
								type="checkbox"
								className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
								checked={selectedIds.has(model.model_id)}
								onChange={() => toggleModel(model.model_id)}
							/>
							<div className="flex-1">
								<span className="font-medium text-gray-900">{model.model_type}</span>
								<span className="ml-2 text-sm text-gray-500">{model.model_id.slice(0, 8)}</span>
							</div>
							<div className="text-right text-sm">
								<span className="text-gray-600">AUC: {model.roc_auc.toFixed(3)}</span>
								<span className="ml-3 text-gray-400">{formatTimestamp(model.created_at)}</span>
							</div>
						</label>
					))}
				</div>

				<div className="mt-4 flex items-center gap-4">
					<div className="flex rounded-lg border border-gray-200">
						<button
							type="button"
							className={`rounded-l-lg px-3 py-1.5 text-sm font-medium transition-colors ${
								mode === "stored"
									? "bg-blue-600 text-white"
									: "bg-white text-gray-700 hover:bg-gray-50"
							}`}
							onClick={() => setMode("stored")}
						>
							Stored Results
						</button>
						<button
							type="button"
							className={`rounded-r-lg border-l border-gray-200 px-3 py-1.5 text-sm font-medium transition-colors ${
								mode === "retrain"
									? "bg-blue-600 text-white"
									: "bg-white text-gray-700 hover:bg-gray-50"
							}`}
							onClick={() => setMode("retrain")}
						>
							Re-train
						</button>
					</div>

					<Button onClick={handleCompare} loading={loading} disabled={selectedIds.size === 0}>
						{loading
							? "Comparing..."
							: `Compare ${selectedIds.size} Model${selectedIds.size !== 1 ? "s" : ""}`}
					</Button>
				</div>

				{mode === "stored" && (
					<p className="mt-2 text-xs text-gray-400">
						Uses metrics from original training. Results may not be available for older models.
					</p>
				)}
				{mode === "retrain" && (
					<p className="mt-2 text-xs text-gray-400">
						Re-trains each model type with default config. Creates new models with fresh metrics.
					</p>
				)}
			</Card>

			{unavailableIds.size > 0 && (
				<div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
					Stored results unavailable for{" "}
					{Array.from(unavailableIds)
						.map((id) => id.slice(0, 8))
						.join(", ")}
					. These models were trained before results storage was enabled. Use Re-train mode to
					compare them.
				</div>
			)}

			{selectedResults.length > 0 && (
				<>
					<Card title="Metrics Comparison">
						<Table
							columns={[
								{ key: "model_id", header: "Model ID" },
								{ key: "model_type", header: "Type" },
								{ key: "accuracy", header: "Accuracy" },
								{ key: "precision", header: "Precision" },
								{ key: "recall", header: "Recall" },
								{ key: "f1_score", header: "F1" },
								{ key: "roc_auc", header: "AUC" },
								{ key: "threshold", header: "Threshold" },
							]}
							data={comparisonTableData as Record<string, unknown>[]}
						/>
					</Card>

					<Card title="Metrics Bar Chart">
						<MetricsBar models={metricsBarData} />
					</Card>

					{rocCurves.length > 0 && (
						<Card title="ROC Curves">
							<MultiROCCurve curves={rocCurves} />
						</Card>
					)}
				</>
			)}
		</div>
	);
}

function formatTimestamp(iso: string): string {
	try {
		const date = new Date(iso);
		return date.toLocaleString(undefined, {
			month: "short",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		});
	} catch {
		return iso;
	}
}
