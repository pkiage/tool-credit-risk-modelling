import type { FullConfig } from "@playwright/test";

const API_BASE = "http://localhost:8000";

/**
 * Global setup: train one logistic_regression and one random_forest model
 * so all E2E specs can use them without redundant training.
 */
async function globalSetup(_config: FullConfig) {
	// Wait for API to be healthy
	const maxWait = 30_000;
	const start = Date.now();
	while (Date.now() - start < maxWait) {
		try {
			const res = await fetch(`${API_BASE}/health`);
			if (res.ok) break;
		} catch {
			// server not ready yet
		}
		await new Promise((r) => setTimeout(r, 500));
	}

	// Train two models for compare/predict specs
	for (const modelType of ["logistic_regression", "random_forest"]) {
		const res = await fetch(`${API_BASE}/train/`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				model_type: modelType,
				test_size: 0.2,
				random_state: 42,
				undersample: false,
				cv_folds: 5,
			}),
		});
		if (!res.ok) {
			throw new Error(`Failed to train ${modelType}: ${res.status} ${await res.text()}`);
		}
	}
}

export default globalSetup;
