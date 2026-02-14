"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import type { SyntheticConfig } from "@/lib/types";

const PRESETS: Record<string, Partial<SyntheticConfig>> = {
	"Stress Test": { n_samples: 5000, default_rate: 0.5 },
	"Low Default": { n_samples: 5000, default_rate: 0.05 },
	"Large Sample": { n_samples: 50000, default_rate: 0.22 },
	Balanced: { n_samples: 5000, default_rate: 0.5 },
};

const presetOptions = [
	{ value: "Custom", label: "Custom" },
	...Object.keys(PRESETS).map((name) => ({ value: name, label: name })),
];

interface SyntheticFormProps {
	onGenerate: (config: SyntheticConfig) => void;
	loading: boolean;
}

export function SyntheticForm({ onGenerate, loading }: SyntheticFormProps) {
	const [selectedPreset, setSelectedPreset] = useState("Custom");
	const [nSamples, setNSamples] = useState(5000);
	const [defaultRate, setDefaultRate] = useState(0.22);
	const [randomSeed, setRandomSeed] = useState(42);

	const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
		const preset = e.target.value;
		setSelectedPreset(preset);
		if (preset !== "Custom" && PRESETS[preset]) {
			const p = PRESETS[preset];
			if (p.n_samples !== undefined) setNSamples(p.n_samples);
			if (p.default_rate !== undefined) setDefaultRate(p.default_rate);
		}
	};

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		onGenerate({
			n_samples: nSamples,
			default_rate: defaultRate,
			distributions: [],
			random_seed: randomSeed,
		});
	};

	return (
		<form onSubmit={handleSubmit} className="space-y-6">
			<Select
				label="Preset"
				options={presetOptions}
				value={selectedPreset}
				onChange={handlePresetChange}
			/>

			<Slider
				label="Number of Samples"
				min={100}
				max={50000}
				step={100}
				value={nSamples}
				displayValue={nSamples.toLocaleString()}
				onChange={(e) => {
					setNSamples(Number(e.target.value));
					setSelectedPreset("Custom");
				}}
			/>

			<Slider
				label="Default Rate"
				min={0.01}
				max={0.99}
				step={0.01}
				value={defaultRate}
				displayValue={`${(defaultRate * 100).toFixed(0)}%`}
				onChange={(e) => {
					setDefaultRate(Number(e.target.value));
					setSelectedPreset("Custom");
				}}
			/>

			<div className="space-y-1">
				<label
					htmlFor="random-seed"
					className="block text-sm font-medium text-foreground-secondary"
				>
					Random Seed
				</label>
				<input
					id="random-seed"
					type="number"
					className="block w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-focus-ring"
					value={randomSeed}
					onChange={(e) => setRandomSeed(Number(e.target.value))}
				/>
			</div>

			<Button type="submit" loading={loading} className="w-full">
				{loading ? "Generating..." : "Generate Synthetic Data"}
			</Button>
		</form>
	);
}
