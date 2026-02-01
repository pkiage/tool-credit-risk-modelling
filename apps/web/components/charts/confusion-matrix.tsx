"use client";

import type { ConfusionMatrix as ConfusionMatrixType } from "@/lib/types";

interface ConfusionMatrixProps {
	data: ConfusionMatrixType;
}

export function ConfusionMatrixChart({ data }: ConfusionMatrixProps) {
	const total = data.true_negatives + data.false_positives + data.false_negatives + data.true_positives;

	const cells = [
		{ label: "True Neg", value: data.true_negatives, row: "Actual: No Default", col: "Pred: No Default", color: "bg-green-100 text-green-800" },
		{ label: "False Pos", value: data.false_positives, row: "Actual: No Default", col: "Pred: Default", color: "bg-red-100 text-red-800" },
		{ label: "False Neg", value: data.false_negatives, row: "Actual: Default", col: "Pred: No Default", color: "bg-orange-100 text-orange-800" },
		{ label: "True Pos", value: data.true_positives, row: "Actual: Default", col: "Pred: Default", color: "bg-blue-100 text-blue-800" },
	];

	return (
		<div className="space-y-2">
			<div className="grid grid-cols-3 gap-1 text-center text-sm">
				<div />
				<div className="font-medium text-gray-600">Pred: No Default</div>
				<div className="font-medium text-gray-600">Pred: Default</div>

				<div className="flex items-center justify-center font-medium text-gray-600">
					Actual: No Default
				</div>
				{cells.slice(0, 2).map((cell) => (
					<div
						key={cell.label}
						className={`rounded-lg p-4 ${cell.color}`}
					>
						<div className="text-2xl font-bold">{cell.value}</div>
						<div className="text-xs">{cell.label}</div>
						<div className="text-xs opacity-70">
							{total > 0 ? ((cell.value / total) * 100).toFixed(1) : 0}%
						</div>
					</div>
				))}

				<div className="flex items-center justify-center font-medium text-gray-600">
					Actual: Default
				</div>
				{cells.slice(2, 4).map((cell) => (
					<div
						key={cell.label}
						className={`rounded-lg p-4 ${cell.color}`}
					>
						<div className="text-2xl font-bold">{cell.value}</div>
						<div className="text-xs">{cell.label}</div>
						<div className="text-xs opacity-70">
							{total > 0 ? ((cell.value / total) * 100).toFixed(1) : 0}%
						</div>
					</div>
				))}
			</div>
		</div>
	);
}
