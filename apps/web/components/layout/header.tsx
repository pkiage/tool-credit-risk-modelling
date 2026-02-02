import Link from "next/link";
import { LogoutButton } from "../logout-button";
import { Nav } from "./nav";

export function Header() {
	return (
		<header className="border-b border-gray-200 bg-white">
			<div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
				<Link href="/" className="text-xl font-bold text-gray-900">
					Credit Risk Platform
				</Link>
				<div className="flex items-center gap-4">
					<Nav />
					<LogoutButton />
				</div>
			</div>
		</header>
	);
}
