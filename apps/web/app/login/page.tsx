"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function LoginPage() {
	const [apiKey, setApiKey] = useState("");
	const [error, setError] = useState("");
	const [loading, setLoading] = useState(false);
	const router = useRouter();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError("");

		try {
			const res = await fetch(
				`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/verify`,
				{
					method: "POST",
					headers: {
						Authorization: `Bearer ${apiKey}`,
					},
				},
			);

			if (!res.ok) {
				throw new Error("Invalid API key");
			}

			// biome-ignore lint/suspicious/noDocumentCookie: cookie-based auth requires direct cookie access
			document.cookie = `api_key=${apiKey}; path=/; max-age=86400`;
			router.push("/");
		} catch {
			setError("Invalid API key. Please try again.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="flex min-h-screen items-center justify-center">
			<form onSubmit={handleSubmit} className="w-full max-w-md p-8">
				<h1 className="mb-6 font-bold text-2xl">Login</h1>

				<input
					type="password"
					value={apiKey}
					onChange={(e) => setApiKey(e.target.value)}
					placeholder="Enter API Key"
					className="mb-4 w-full rounded border p-3"
				/>

				{error && <p className="mb-4 text-red-500">{error}</p>}

				<button
					type="submit"
					disabled={loading}
					className="w-full rounded bg-blue-500 p-3 text-white disabled:opacity-50"
				>
					{loading ? "Verifying..." : "Login"}
				</button>
			</form>
		</div>
	);
}
