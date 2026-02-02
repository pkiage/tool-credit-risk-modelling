"use client";

import { useRouter } from "next/navigation";

export function LogoutButton() {
	const router = useRouter();

	const handleLogout = () => {
		// biome-ignore lint/suspicious/noDocumentCookie: cookie-based auth requires direct cookie access
		document.cookie = "api_key=; path=/; max-age=0";
		router.push("/login");
	};

	return (
		<button
			type="button"
			onClick={handleLogout}
			className="text-sm text-gray-500 hover:text-gray-700"
		>
			Logout
		</button>
	);
}
