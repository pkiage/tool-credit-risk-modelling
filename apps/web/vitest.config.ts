import { resolve } from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
	plugins: [react()],
	resolve: {
		alias: {
			"@": resolve(__dirname, "."),
		},
	},
	test: {
		environment: "jsdom",
		setupFiles: ["./vitest.setup.ts"],
		include: ["__tests__/**/*.test.{ts,tsx}"],
		globals: true,
	},
});
