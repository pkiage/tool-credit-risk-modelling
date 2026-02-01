import type { ReactNode } from "react";

interface CardProps {
	title?: string;
	children: ReactNode;
	className?: string;
}

export function Card({ title, children, className = "" }: CardProps) {
	return (
		<div
			className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`}
		>
			{title && (
				<div className="border-b border-gray-200 px-6 py-4">
					<h3 className="text-lg font-semibold text-gray-900">{title}</h3>
				</div>
			)}
			<div className="px-6 py-4">{children}</div>
		</div>
	);
}
