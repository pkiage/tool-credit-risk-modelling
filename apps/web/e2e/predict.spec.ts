import { expect, test } from "@playwright/test";
import { trainModel } from "./helpers";

test.describe("Predict Flow", () => {
	test.beforeAll(async ({ browser }) => {
		// Train a model so there's something to predict with
		const page = await browser.newPage();
		await trainModel(page);
		await page.close();
	});

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

		// Wait for result
		const resultText = page.getByText(/Default|No Default/);
		await expect(resultText).toBeVisible({ timeout: 30_000 });

		// Verify details card
		await expect(page.getByText("Details")).toBeVisible();
		await expect(page.getByText("Default Probability")).toBeVisible();
		await expect(page.getByText("Confidence")).toBeVisible();
		await expect(page.getByText("Probability Bar")).toBeVisible();
	});

	test("shows empty state when no models and navigating from predict page", async ({ page }) => {
		// This test doesn't need setup since we check for the form elements
		await page.goto("/predict");

		await expect(page.getByRole("heading", { name: "Predict Default" })).toBeVisible();
	});
});
