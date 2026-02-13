import { expect, test } from "@playwright/test";

test.describe("Train Flow", () => {
	test("trains a logistic regression model and displays results", async ({ page }) => {
		await page.goto("/train");

		// Verify configuration form
		await expect(page.getByLabel("Model Type")).toBeVisible();
		await expect(page.getByLabel("Test Size")).toBeVisible();
		await expect(page.getByLabel("CV Folds")).toBeVisible();

		// Select model type and train
		await page.getByLabel("Model Type").selectOption("logistic_regression");
		await page.getByRole("button", { name: "Train Model" }).click();

		// Should show loading state
		await expect(page.getByText("Training model...")).toBeVisible();

		// Wait for training to complete
		await expect(page.getByText("Training Summary")).toBeVisible({ timeout: 120_000 });

		// Verify results are displayed
		await expect(page.getByText("Metrics")).toBeVisible();
		await expect(page.getByText("ROC Curve")).toBeVisible();
		await expect(page.getByText("Confusion Matrix")).toBeVisible();
		await expect(page.getByText("Threshold Analysis")).toBeVisible();
	});

	test("trains an xgboost model", async ({ page }) => {
		await page.goto("/train");

		await page.getByLabel("Model Type").selectOption("xgboost");
		await page.getByRole("button", { name: "Train Model" }).click();

		await expect(page.getByText("Training Summary")).toBeVisible({ timeout: 120_000 });

		// XGBoost should show feature importance
		await expect(page.getByText("Feature Importance")).toBeVisible();
	});
});
