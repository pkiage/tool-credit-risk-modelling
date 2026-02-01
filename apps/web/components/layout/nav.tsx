"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
	{ href: "/train", label: "Train" },
	{ href: "/predict", label: "Predict" },
	{ href: "/compare", label: "Compare" },
];

export function Nav() {
	const pathname = usePathname();

	return (
		<nav className="flex gap-1">
			{links.map((link) => {
				const isActive = pathname === link.href;
				return (
					<Link
						key={link.href}
						href={link.href}
						className={`rounded-md px-3 py-2 text-sm font-medium transition-colors ${
							isActive
								? "bg-blue-50 text-blue-700"
								: "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
						}`}
					>
						{link.label}
					</Link>
				);
			})}
		</nav>
	);
}
