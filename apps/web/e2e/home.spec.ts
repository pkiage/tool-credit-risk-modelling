import { expect, test } from "@playwright/test";

test.describe("Home Page", () => {
	test("displays page title and API status", async ({ page }) => {
		await page.goto("/");

		await expect(page.getByRole("heading", { name: "Credit Risk Platform" })).toBeVisible();
		await expect(page.getByText("API: Connected")).toBeVisible({ timeout: 30_000 });
	});

	test("has navigation links to train, predict, and compare", async ({ page }) => {
		await page.goto("/");

		const nav = page.locator("nav");
		await expect(nav.getByRole("link", { name: "Train" })).toBeVisible();
		await expect(nav.getByRole("link", { name: "Predict" })).toBeVisible();
		await expect(nav.getByRole("link", { name: "Compare" })).toBeVisible();
	});

	test("can navigate to train page", async ({ page }) => {
		await page.goto("/");

		// Use the card link, not the nav link
		await page.getByRole("heading", { name: "Train" }).click();
		await expect(page).toHaveURL(/\/train/);
		await expect(page.getByRole("heading", { name: "Train Model" })).toBeVisible();
	});
});
