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

export function Select({ label, options, error, id, className = "", ...props }: SelectProps) {
	const selectId = id || label.toLowerCase().replace(/\s+/g, "-");

	return (
		<div className="space-y-1">
			<label htmlFor={selectId} className="block text-sm font-medium text-foreground-secondary">
				{label}
			</label>
			<select
				id={selectId}
				className={`block w-full rounded-md border bg-background text-foreground px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 ${
					error
						? "border-danger focus:border-danger focus:ring-danger"
						: "border-border focus:border-primary focus:ring-focus-ring"
				} ${className}`}
				{...props}
			>
				{options.map((opt) => (
					<option key={opt.value} value={opt.value}>
						{opt.label}
					</option>
				))}
			</select>
			{error && <p className="text-sm text-danger">{error}</p>}
		</div>
	);
}
