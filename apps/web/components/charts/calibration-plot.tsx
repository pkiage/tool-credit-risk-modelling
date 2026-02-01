"use client";

import {
	CartesianGrid,
	Line,
	LineChart,
	ReferenceLine,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
import type { CalibrationCurve } from "@/lib/types";

interface CalibrationPlotProps {
	data: CalibrationCurve;
}

export function CalibrationPlot({ data }: CalibrationPlotProps) {
	const chartData = data.prob_pred.map((pred, i) => ({
		predicted: pred,
		actual: data.prob_true[i],
	}));

	return (
		<ResponsiveContainer width="100%" height={350}>
			<LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 25, left: 10 }}>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis
					dataKey="predicted"
					type="number"
					domain={[0, 1]}
					label={{ value: "Mean Predicted Probability", position: "insideBottom", offset: -15 }}
				/>
				<YAxis
					domain={[0, 1]}
					label={{ value: "Fraction of Positives", angle: -90, position: "insideLeft" }}
				/>
				<Tooltip formatter={(value: number) => value.toFixed(4)} />
				<ReferenceLine
					segment={[
						{ x: 0, y: 0 },
						{ x: 1, y: 1 },
					]}
					stroke="#9ca3af"
					strokeDasharray="5 5"
					label="Perfect Calibration"
				/>
				<Line
					name="Calibration"
					type="monotone"
					dataKey="actual"
					stroke="#2563eb"
					strokeWidth={2}
					dot={{ r: 4 }}
				/>
			</LineChart>
		</ResponsiveContainer>
	);
}
