import type { SelectHTMLAttributes } from "react";

interface SelectOption {
	value: string;
	label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
	label: string;
	options: SelectOption[];
	error?: string;
}

export function Select({
	label,
	options,
	error,
	id,
	className = "",
	...props
}: SelectProps) {
	const selectId = id || label.toLowerCase().replace(/\s+/g, "-");

	return (
		<div className="space-y-1">
			<label htmlFor={selectId} className="block text-sm font-medium text-gray-700">
				{label}
			</label>
			<select
				id={selectId}
				className={`block w-full rounded-md border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
					error
						? "border-red-300 focus:border-red-500 focus:ring-red-500"
						: "border-gray-300 focus:border-blue-500"
				} ${className}`}
				{...props}
			>
				{options.map((opt) => (
					<option key={opt.value} value={opt.value}>
						{opt.label}
					</option>
				))}
			</select>
			{error && <p className="text-sm text-red-600">{error}</p>}
		</div>
	);
}
