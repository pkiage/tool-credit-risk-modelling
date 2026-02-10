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
								? "bg-primary/10 text-primary"
								: "text-foreground-secondary hover:bg-surface hover:text-foreground"
						}`}
					>
						{link.label}
					</Link>
				);
			})}
		</nav>
	);
}
