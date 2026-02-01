"use client";

import {
	Bar,
	BarChart,
	CartesianGrid,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

interface MetricsBarProps {
	models: {
		name: string;
		accuracy: number;
		precision: number;
		recall: number;
		f1_score: number;
		roc_auc: number;
	}[];
}

const COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"];

export function MetricsBar({ models }: MetricsBarProps) {
	const metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc"] as const;
	const metricLabels: Record<string, string> = {
		accuracy: "Accuracy",
		precision: "Precision",
		recall: "Recall",
		f1_score: "F1 Score",
		roc_auc: "ROC AUC",
	};

	const chartData = metrics.map((metric) => {
		const point: Record<string, string | number> = { metric: metricLabels[metric] };
		for (const model of models) {
			point[model.name] = Number(model[metric].toFixed(4));
		}
		return point;
	});

	return (
		<ResponsiveContainer width="100%" height={350}>
			<BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis dataKey="metric" />
				<YAxis domain={[0, 1]} />
				<Tooltip formatter={(value: number) => value.toFixed(4)} />
				<Legend />
				{models.map((model, idx) => (
					<Bar
						key={model.name}
						dataKey={model.name}
						fill={COLORS[idx % COLORS.length]}
					/>
				))}
			</BarChart>
		</ResponsiveContainer>
	);
}
