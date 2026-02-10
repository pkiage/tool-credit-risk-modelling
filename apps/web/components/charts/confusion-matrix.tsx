"use client";

import type { ConfusionMatrix as ConfusionMatrixType } from "@/lib/types";

interface ConfusionMatrixProps {
	data: ConfusionMatrixType;
}

export function ConfusionMatrixChart({ data }: ConfusionMatrixProps) {
	const total =
		data.true_negatives + data.false_positives + data.false_negatives + data.true_positives;

	const cells = [
		{
			label: "True Neg",
			value: data.true_negatives,
			row: "Actual: No Default",
			col: "Pred: No Default",
			color: "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200",
		},
		{
			label: "False Pos",
			value: data.false_positives,
			row: "Actual: No Default",
			col: "Pred: Default",
			color: "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200",
		},
		{
			label: "False Neg",
			value: data.false_negatives,
			row: "Actual: Default",
			col: "Pred: No Default",
			color: "bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200",
		},
		{
			label: "True Pos",
			value: data.true_positives,
			row: "Actual: Default",
			col: "Pred: Default",
			color: "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200",
		},
	];

	return (
		<section className="space-y-2" aria-label="Confusion matrix showing model prediction accuracy">
			<div className="grid grid-cols-3 gap-1 text-center text-sm">
				<div />
				<div className="font-medium text-foreground-secondary">Pred: No Default</div>
				<div className="font-medium text-foreground-secondary">Pred: Default</div>

				<div className="flex items-center justify-center font-medium text-foreground-secondary">
					Actual: No Default
				</div>
				{cells.slice(0, 2).map((cell) => (
					<div
						key={cell.label}
						className={`rounded-lg p-4 ${cell.color}`}
						title={`${cell.label}: ${cell.value} cases (${total > 0 ? ((cell.value / total) * 100).toFixed(1) : 0}%)`}
					>
						<div className="text-2xl font-bold">{cell.value}</div>
						<div className="text-xs font-medium">{cell.label}</div>
						<div className="text-xs opacity-70">
							{total > 0 ? ((cell.value / total) * 100).toFixed(1) : 0}%
						</div>
					</div>
				))}

				<div className="flex items-center justify-center font-medium text-foreground-secondary">
					Actual: Default
				</div>
				{cells.slice(2, 4).map((cell) => (
					<div
						key={cell.label}
						className={`rounded-lg p-4 ${cell.color}`}
						title={`${cell.label}: ${cell.value} cases (${total > 0 ? ((cell.value / total) * 100).toFixed(1) : 0}%)`}
					>
						<div className="text-2xl font-bold">{cell.value}</div>
						<div className="text-xs font-medium">{cell.label}</div>
						<div className="text-xs opacity-70">
							{total > 0 ? ((cell.value / total) * 100).toFixed(1) : 0}%
						</div>
					</div>
				))}
			</div>
		</section>
	);
}
