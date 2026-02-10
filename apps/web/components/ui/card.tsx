import type { ReactNode } from "react";

interface CardProps {
	title?: string;
	children: ReactNode;
	className?: string;
}

export function Card({ title, children, className = "" }: CardProps) {
	return (
		<div className={`rounded-lg border border-border bg-background shadow-sm ${className}`}>
			{title && (
				<div className="border-b border-border px-6 py-4">
					<h3 className="text-lg font-semibold text-foreground">{title}</h3>
				</div>
			)}
			<div className="px-6 py-4">{children}</div>
		</div>
	);
}
