import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
	label: string;
	error?: string;
}

export function Input({ label, error, id, className = "", ...props }: InputProps) {
	const inputId = id || label.toLowerCase().replace(/\s+/g, "-");

	return (
		<div className="space-y-1">
			<label htmlFor={inputId} className="block text-sm font-medium text-foreground-secondary">
				{label}
			</label>
			<input
				id={inputId}
				className={`block w-full rounded-md border bg-background text-foreground px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 ${
					error
						? "border-danger focus:border-danger focus:ring-danger"
						: "border-border focus:border-primary focus:ring-focus-ring"
				} ${className}`}
				{...props}
			/>
			{error && <p className="text-sm text-danger">{error}</p>}
		</div>
	);
}
