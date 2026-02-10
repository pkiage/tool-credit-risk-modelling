import Link from "next/link";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Nav } from "./nav";

export function Header() {
	return (
		<header className="border-b border-border bg-background">
			<div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
				<Link href="/" className="text-xl font-bold text-foreground">
					Credit Risk Platform
				</Link>
				<div className="flex items-center gap-4">
					<Nav />
					<ThemeToggle />
				</div>
			</div>
		</header>
	);
}
