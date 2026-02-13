import { defineConfig } from "@playwright/test";

export default defineConfig({
	testDir: "./e2e",
	fullyParallel: false,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: 1,
	reporter: "html",
	timeout: 120_000,
	use: {
		baseURL: "http://localhost:3000",
		trace: "on-first-retry",
	},
	projects: [
		{
			name: "chromium",
			use: { browserName: "chromium" },
		},
	],
	webServer: [
		{
			command: "uv run uvicorn apps.api.main:app --host 0.0.0.0 --port 8000",
			cwd: "../..",
			url: "http://localhost:8000/health",
			reuseExistingServer: !process.env.CI,
			timeout: 30_000,
		},
		{
			command: "npm run dev",
			url: "http://localhost:3000",
			reuseExistingServer: !process.env.CI,
			timeout: 30_000,
		},
	],
});
