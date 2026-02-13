import { expect, test } from "@playwright/test";

test.describe("Home Page", () => {
	test("displays page title and API status", async ({ page }) => {
		await page.goto("/");

		await expect(page.getByRole("heading", { name: "Credit Risk Platform" })).toBeVisible();
		await expect(page.getByText("API: Connected")).toBeVisible({ timeout: 30_000 });
	});

	test("has navigation links to train, predict, and compare", async ({ page }) => {
		await page.goto("/");

		await expect(page.getByRole("link", { name: /Train/i })).toBeVisible();
		await expect(page.getByRole("link", { name: /Predict/i })).toBeVisible();
		await expect(page.getByRole("link", { name: /Compare/i })).toBeVisible();
	});

	test("can navigate to train page", async ({ page }) => {
		await page.goto("/");

		// Use the card link, not the nav link
		await page.getByRole("heading", { name: "Train" }).click();
		await expect(page).toHaveURL(/\/train/);
		await expect(page.getByRole("heading", { name: "Train Model" })).toBeVisible();
	});
});
