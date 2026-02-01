"use client";

import {
	CartesianGrid,
	Legend,
	Line,
	LineChart,
	ReferenceLine,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
import type { ROCCurveData } from "@/lib/types";

interface ROCCurveProps {
	data: ROCCurveData;
	thresholdMarker?: number;
	label?: string;
	color?: string;
}

interface MultiROCCurveProps {
	curves: { data: ROCCurveData; label: string; color: string }[];
}

const COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"];

export function ROCCurve({ data, label = "Model", color = "#2563eb" }: ROCCurveProps) {
	const chartData = data.fpr.map((fpr, i) => ({
		fpr,
		tpr: data.tpr[i],
	}));

	return (
		<ResponsiveContainer width="100%" height={350}>
			<LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 25, left: 10 }}>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis
					dataKey="fpr"
					type="number"
					domain={[0, 1]}
					label={{ value: "False Positive Rate", position: "insideBottom", offset: -15 }}
				/>
				<YAxis
					domain={[0, 1]}
					label={{ value: "True Positive Rate", angle: -90, position: "insideLeft" }}
				/>
				<Tooltip
					formatter={(value: number) => value.toFixed(4)}
					labelFormatter={(fpr: number) => `FPR: ${fpr.toFixed(4)}`}
				/>
				<Legend verticalAlign="top" />
				<ReferenceLine
					segment={[
						{ x: 0, y: 0 },
						{ x: 1, y: 1 },
					]}
					stroke="#9ca3af"
					strokeDasharray="5 5"
					label="Random"
				/>
				<Line
					name={label}
					type="monotone"
					dataKey="tpr"
					stroke={color}
					dot={false}
					strokeWidth={2}
				/>
			</LineChart>
		</ResponsiveContainer>
	);
}

export function MultiROCCurve({ curves }: MultiROCCurveProps) {
	// Merge all curves into a shared dataset keyed by index
	const maxLen = Math.max(...curves.map((c) => c.data.fpr.length));
	const chartData = Array.from({ length: maxLen }, (_, i) => {
		const point: Record<string, number> = {};
		for (const curve of curves) {
			if (i < curve.data.fpr.length) {
				point[`fpr_${curve.label}`] = curve.data.fpr[i];
				point[`tpr_${curve.label}`] = curve.data.tpr[i];
			}
		}
		// Use first curve's FPR as x-axis (they'll be plotted parametrically)
		point.index = i;
		return point;
	});

	return (
		<ResponsiveContainer width="100%" height={350}>
			<LineChart margin={{ top: 5, right: 20, bottom: 25, left: 10 }}>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis
					type="number"
					domain={[0, 1]}
					label={{ value: "False Positive Rate", position: "insideBottom", offset: -15 }}
				/>
				<YAxis
					domain={[0, 1]}
					label={{ value: "True Positive Rate", angle: -90, position: "insideLeft" }}
				/>
				<Tooltip formatter={(value: number) => value.toFixed(4)} />
				<Legend verticalAlign="top" />
				<ReferenceLine
					segment={[
						{ x: 0, y: 0 },
						{ x: 1, y: 1 },
					]}
					stroke="#9ca3af"
					strokeDasharray="5 5"
				/>
				{curves.map((curve, idx) => {
					const curveData = curve.data.fpr.map((fpr, i) => ({
						x: fpr,
						y: curve.data.tpr[i],
					}));
					return (
						<Line
							key={curve.label}
							name={curve.label}
							data={curveData}
							type="monotone"
							dataKey="y"
							stroke={curve.color || COLORS[idx % COLORS.length]}
							dot={false}
							strokeWidth={2}
						/>
					);
				})}
			</LineChart>
		</ResponsiveContainer>
	);
}
