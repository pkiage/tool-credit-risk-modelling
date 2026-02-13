import { expect, test } from "@playwright/test";
import { trainModel } from "./helpers";

test.describe("Compare Flow", () => {
	test.beforeAll(async ({ browser }) => {
		// Train two models for comparison
		const page = await browser.newPage();
		await trainModel(page, "logistic_regression");
		await trainModel(page, "random_forest");
		await page.close();
	});

	test("loads compare page with model checkboxes", async ({ page }) => {
		await page.goto("/compare");

		await expect(page.getByRole("heading", { name: "Compare Models" })).toBeVisible();
		await expect(page.getByText("Select Models")).toBeVisible();

		// Should have at least 2 model checkboxes
		const checkboxes = page.getByRole("checkbox");
		const count = await checkboxes.count();
		expect(count).toBeGreaterThanOrEqual(2);
	});

	test("selects models and compares with stored results", async ({ page }) => {
		await page.goto("/compare");

		// Wait for models to load
		await expect(page.getByText("Select Models")).toBeVisible();

		// Select first two models
		const checkboxes = page.getByRole("checkbox");
		await checkboxes.nth(0).check();
		await checkboxes.nth(1).check();

		// Ensure "Stored Results" mode is active (default)
		await expect(page.getByRole("button", { name: "Stored Results" })).toBeVisible();

		// Click compare
		await page.getByRole("button", { name: /Compare \d+ Models?/ }).click();

		// Wait for results (stored results should be fast, but re-train can be slow)
		// Either we get metrics comparison or a warning about unavailable results
		const metricsOrWarning = page
			.getByText("Metrics Comparison")
			.or(page.getByText(/stored results unavailable/i))
			.or(page.getByText(/Re-train mode/i));

		await expect(metricsOrWarning).toBeVisible({ timeout: 30_000 });
	});

	test("can switch to re-train mode", async ({ page }) => {
		await page.goto("/compare");

		// Wait for models to load
		await expect(page.getByText("Select Models")).toBeVisible();

		// Click re-train button
		await page.getByRole("button", { name: "Re-train" }).click();

		// Verify info text changes
		await expect(page.getByText(/Re-trains each model type/)).toBeVisible();
	});

	test("compare button shows correct count", async ({ page }) => {
		await page.goto("/compare");
		await expect(page.getByText("Select Models")).toBeVisible();

		// Initially 0 selected
		await expect(page.getByRole("button", { name: "Compare 0 Models" })).toBeVisible();

		// Select one
		const checkboxes = page.getByRole("checkbox");
		await checkboxes.nth(0).check();
		await expect(page.getByRole("button", { name: "Compare 1 Model" })).toBeVisible();

		// Select another
		await checkboxes.nth(1).check();
		await expect(page.getByRole("button", { name: "Compare 2 Models" })).toBeVisible();

		// Deselect one
		await checkboxes.nth(0).uncheck();
		await expect(page.getByRole("button", { name: "Compare 1 Model" })).toBeVisible();
	});
});
