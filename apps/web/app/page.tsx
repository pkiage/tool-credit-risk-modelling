"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api-client";
import type { ModelMetadata } from "@/lib/types";

export default function Home() {
	const [healthy, setHealthy] = useState<boolean | null>(null);
	const [models, setModels] = useState<ModelMetadata[]>([]);

	useEffect(() => {
		api.health()
			.then(() => setHealthy(true))
			.catch(() => setHealthy(false));

		api.listModels()
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
				<h1 className="text-3xl font-bold text-gray-900">Credit Risk Platform</h1>
				<p className="mt-2 text-gray-600">
					Train, evaluate, and deploy credit risk models.
				</p>
			</div>

			<div className="flex items-center gap-2">
				<span
					className={`inline-block h-3 w-3 rounded-full ${
						healthy === null
							? "bg-gray-300"
							: healthy
								? "bg-green-500"
								: "bg-red-500"
					}`}
				/>
				<span className="text-sm text-gray-600">
					API:{" "}
					{healthy === null
						? "Checking..."
						: healthy
							? "Connected"
							: "Unavailable"}
				</span>
				{models.length > 0 && (
					<span className="ml-4 text-sm text-gray-600">
						{models.length} model{models.length !== 1 ? "s" : ""} trained
					</span>
				)}
			</div>

			<div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
				{pages.map((page) => (
					<Link key={page.href} href={page.href}>
						<Card className="h-full transition-shadow hover:shadow-md">
							<h2 className="text-lg font-semibold text-gray-900">{page.title}</h2>
							<p className="mt-2 text-sm text-gray-600">{page.description}</p>
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
								className="flex items-center justify-between rounded-md border border-gray-100 px-4 py-2"
							>
								<div>
									<span className="font-medium text-gray-900">{model.model_type}</span>
									<span className="ml-2 text-sm text-gray-500">{model.model_id}</span>
								</div>
								<div className="text-sm text-gray-600">
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
