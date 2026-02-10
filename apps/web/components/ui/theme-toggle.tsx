"use client";

import { useTheme } from "@/lib/theme-provider";

export function ThemeToggle() {
	const { theme, setTheme } = useTheme();

	return (
		<button
			type="button"
			onClick={() => {
				const newTheme = theme === "light" ? "dark" : theme === "dark" ? "system" : "light";
				setTheme(newTheme);
			}}
			className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-foreground hover:bg-surface-elevated focus:outline-none focus:ring-2 focus:ring-focus-ring focus:ring-offset-2"
			aria-label={`Switch theme (current: ${theme})`}
		>
			{theme === "light" && (
				<svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
					/>
				</svg>
			)}
			{theme === "dark" && (
				<svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
					/>
				</svg>
			)}
			{theme === "system" && (
				<svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2}
						d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
					/>
				</svg>
			)}
		</button>
	);
}
