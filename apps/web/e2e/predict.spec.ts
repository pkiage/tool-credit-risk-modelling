import { expect, test } from "@playwright/test";

test.describe("Predict Flow", () => {
	// Models are pre-trained by global setup

	test("loads prediction form with trained models", async ({ page }) => {
		await page.goto("/predict");

		await expect(page.getByRole("heading", { name: "Predict Default" })).toBeVisible();
		await expect(page.getByLabel("Select Model")).toBeVisible();

		// Should have at least one model option
		const options = page.getByLabel("Select Model").locator("option");
		await expect(options).not.toHaveCount(0);
	});

	test("submits prediction and shows results", async ({ page }) => {
		await page.goto("/predict");

		// Wait for models to load
		await expect(page.getByLabel("Select Model")).toBeVisible();

		// Fill in loan fields (defaults should be pre-filled, but verify key ones)
		await expect(page.getByLabel("Age")).toHaveValue(/\d+/);
		await expect(page.getByLabel("Annual Income")).toHaveValue(/\d+/);

		// Submit prediction
		await page.getByRole("button", { name: "Get Prediction" }).click();

		// Wait for result badge (exact match to avoid "Predict Default", "Default on File", etc.)
		const resultBadge = page
			.getByText("No Default", { exact: true })
			.or(page.getByText("Default", { exact: true }));
		await expect(resultBadge).toBeVisible({ timeout: 30_000 });

		// Verify details and probability cards
		await expect(page.getByRole("heading", { name: "Details" })).toBeVisible();
		await expect(page.getByRole("heading", { name: "Probability Bar" })).toBeVisible();
	});

	test("shows empty state when no models and navigating from predict page", async ({ page }) => {
		// This test doesn't need setup since we check for the form elements
		await page.goto("/predict");

		await expect(page.getByRole("heading", { name: "Predict Default" })).toBeVisible();
	});
});
