"use client";

import {
	CartesianGrid,
	Legend,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
// import type { DataType } from "@/lib/types";

// --- 1. Props Interface ---

interface ChartNameProps {
	data: {
		xValues: number[];
		yValues: number[];
	};
	label?: string;
	color?: string;
}

// --- 2. Color Palette (for multi-series) ---

// const COLORS = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"];

// --- 3. Component ---

export function ChartName({
	data,
	label = "Series",
	color = "#2563eb",
}: ChartNameProps) {
	// Transform parallel arrays into Recharts point objects
	const chartData = data.xValues.map((x, i) => ({
		x,
		y: data.yValues[i],
	}));

	return (
		<ResponsiveContainer width="100%" height={350}>
			<LineChart
				data={chartData}
				margin={{ top: 5, right: 20, bottom: 25, left: 10 }}
			>
				<CartesianGrid strokeDasharray="3 3" />
				<XAxis
					dataKey="x"
					type="number"
					domain={[0, 1]}
					label={{
						value: "X Axis Label",
						position: "insideBottom",
						offset: -15,
					}}
				/>
				<YAxis
					domain={[0, 1]}
					label={{
						value: "Y Axis Label",
						angle: -90,
						position: "insideLeft",
					}}
				/>
				<Tooltip
					formatter={(value: number | undefined) =>
						value?.toFixed(4) ?? ""
					}
				/>
				<Legend verticalAlign="top" />
				<Line
					name={label}
					type="monotone"
					dataKey="y"
					stroke={color}
					dot={false}
					strokeWidth={2}
				/>
			</LineChart>
		</ResponsiveContainer>
	);
}

// --- Multi-series variant ---

// interface MultiChartNameProps {
// 	series: { data: DataType; label: string; color: string }[];
// }
//
// export function MultiChartName({ series }: MultiChartNameProps) {
// 	return (
// 		<ResponsiveContainer width="100%" height={350}>
// 			<LineChart margin={{ top: 5, right: 20, bottom: 25, left: 10 }}>
// 				<CartesianGrid strokeDasharray="3 3" />
// 				<XAxis type="number" domain={[0, 1]}
// 					label={{ value: "X Axis Label", position: "insideBottom", offset: -15 }}
// 				/>
// 				<YAxis domain={[0, 1]}
// 					label={{ value: "Y Axis Label", angle: -90, position: "insideLeft" }}
// 				/>
// 				<Tooltip formatter={(value: number | undefined) => value?.toFixed(4) ?? ""} />
// 				<Legend verticalAlign="top" />
// 				{series.map((s, idx) => {
// 					const points = s.data.xValues.map((x, i) => ({
// 						x,
// 						y: s.data.yValues[i],
// 					}));
// 					return (
// 						<Line
// 							key={s.label}
// 							name={s.label}
// 							data={points}
// 							type="monotone"
// 							dataKey="y"
// 							stroke={s.color || COLORS[idx % COLORS.length]}
// 							dot={false}
// 							strokeWidth={2}
// 						/>
// 					);
// 				})}
// 			</LineChart>
// 		</ResponsiveContainer>
// 	);
// }

// --- BarChart variant ---

// interface MetricsBarProps {
// 	items: { name: string; [metric: string]: string | number }[];
// }
//
// export function MetricsBarChart({ items }: MetricsBarProps) {
// 	return (
// 		<ResponsiveContainer width="100%" height={350}>
// 			<BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
// 				<CartesianGrid strokeDasharray="3 3" />
// 				<XAxis dataKey="category" />
// 				<YAxis domain={[0, 1]} />
// 				<Tooltip formatter={(value: number | undefined) => value?.toFixed(4) ?? ""} />
// 				<Legend />
// 				{items.map((item, idx) => (
// 					<Bar key={item.name} dataKey={item.name} fill={COLORS[idx % COLORS.length]} />
// 				))}
// 			</BarChart>
// 		</ResponsiveContainer>
// 	);
// }
