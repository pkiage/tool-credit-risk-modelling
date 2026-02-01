import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
	label: string;
	error?: string;
}

export function Input({ label, error, id, className = "", ...props }: InputProps) {
	const inputId = id || label.toLowerCase().replace(/\s+/g, "-");

	return (
		<div className="space-y-1">
			<label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
				{label}
			</label>
			<input
				id={inputId}
				className={`block w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
					error
						? "border-red-300 focus:border-red-500 focus:ring-red-500"
						: "border-gray-300 focus:border-blue-500"
				} ${className}`}
				{...props}
			/>
			{error && <p className="text-sm text-red-600">{error}</p>}
		</div>
	);
}
