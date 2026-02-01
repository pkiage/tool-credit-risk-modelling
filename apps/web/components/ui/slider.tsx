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
				<label htmlFor={sliderId} className="block text-sm font-medium text-gray-700">
					{label}
				</label>
				{displayValue && (
					<span className="text-sm font-medium text-blue-600">{displayValue}</span>
				)}
			</div>
			<input
				id={sliderId}
				type="range"
				className={`w-full accent-blue-600 ${className}`}
				{...props}
			/>
		</div>
	);
}
