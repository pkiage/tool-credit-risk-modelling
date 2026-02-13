"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api-client";
import type { ModelMetadata } from "@/lib/types";

export default function Home() {
	const [healthy, setHealthy] = useState<boolean | null>(null);
	const [models, setModels] = useState<ModelMetadata[]>([]);

	useEffect(() => {
		api
			.health()
			.then(() => setHealthy(true))
			.catch(() => setHealthy(false));

		api
			.listModels()
			.then(setModels)
			.catch(() => setModels([]));
	}, []);

	const pages = [
		{
			href: "/train",
			title: "Train",
			description: "Train credit risk models with different algorithms and configurations.",
		},
		{
			href: "/predict",
			title: "Predict",
			description: "Submit loan applications and get default predictions from trained models.",
		},
		{
			href: "/compare",
			title: "Compare",
			description: "Compare performance metrics across multiple trained models.",
		},
	];

	return (
		<div className="space-y-8">
			<div>
				<h1 className="text-3xl font-bold text-foreground">Credit Risk Platform</h1>
				<p className="mt-2 text-foreground-secondary">
					Train, evaluate, and deploy credit risk models.
				</p>
			</div>

			<div className="flex items-center gap-2">
				<span
					className={`inline-block h-3 w-3 rounded-full ${
						healthy === null ? "bg-foreground-muted" : healthy ? "bg-green-500" : "bg-red-500"
					}`}
				/>
				<span className="text-sm text-foreground-secondary">
					API: {healthy === null ? "Checking..." : healthy ? "Connected" : "Unavailable"}
				</span>
				{models.length > 0 && (
					<span className="ml-4 text-sm text-foreground-secondary">
						{models.length} model{models.length !== 1 ? "s" : ""} trained
					</span>
				)}
			</div>

			<div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
				{pages.map((page) => (
					<Link key={page.href} href={page.href}>
						<Card className="h-full transition-shadow hover:shadow-md">
							<h2 className="text-lg font-semibold text-foreground">{page.title}</h2>
							<p className="mt-2 text-sm text-foreground-secondary">{page.description}</p>
						</Card>
					</Link>
				))}
			</div>

			{models.length > 0 && (
				<Card title="Trained Models">
					<div className="space-y-2">
						{models.map((model) => (
							<div
								key={model.model_id}
								className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border px-4 py-2"
							>
								<div className="min-w-0">
									<span className="font-medium text-foreground">{model.model_type}</span>
									<span className="ml-2 text-sm text-foreground-muted" title={model.model_id}>
										{model.model_id.slice(0, 8)}
									</span>
								</div>
								<div className="text-sm text-foreground-secondary">
									AUC: {model.roc_auc.toFixed(3)} | Acc: {model.accuracy.toFixed(3)}
								</div>
							</div>
						))}
					</div>
				</Card>
			)}
		</div>
	);
}
