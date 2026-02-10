import type { InputHTMLAttributes } from "react";

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
	label: string;
	displayValue?: string;
}

export function Slider({ label, displayValue, id, className = "", ...props }: SliderProps) {
	const sliderId = id || label.toLowerCase().replace(/\s+/g, "-");

	return (
		<div className="space-y-1">
			<div className="flex items-center justify-between">
				<label htmlFor={sliderId} className="block text-sm font-medium text-foreground-secondary">
					{label}
				</label>
				{displayValue && <span className="text-sm font-medium text-primary">{displayValue}</span>}
			</div>
			<input
				id={sliderId}
				type="range"
				className={`w-full accent-primary ${className}`}
				{...props}
			/>
		</div>
	);
}
