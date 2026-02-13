import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

/**
 * Wait for the API to be available by checking the home page status indicator.
 */
export async function waitForApiHealth(page: Page) {
	await page.goto("/");
	await expect(page.getByText("API: Connected")).toBeVisible({ timeout: 30_000 });
}

/**
 * Train a model and return its model ID from the training summary.
 */
export async function trainModel(
	page: Page,
	modelType: "logistic_regression" | "xgboost" | "random_forest" = "logistic_regression",
) {
	await page.goto("/train");

	// Select model type
	await page.getByLabel("Model Type").selectOption(modelType);

	// Click train
	await page.getByRole("button", { name: "Train Model" }).click();

	// Wait for training to complete (can take up to 60s)
	await expect(page.getByText("Training Summary")).toBeVisible({ timeout: 120_000 });

	// Return the model ID from the summary
	return page;
}
