import type { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: ButtonVariant;
	loading?: boolean;
}

const variantClasses: Record<ButtonVariant, string> = {
	primary: "bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300",
	secondary:
		"bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 disabled:bg-gray-100",
	danger: "bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300",
};

export function Button({
	variant = "primary",
	loading = false,
	children,
	disabled,
	className = "",
	...props
}: ButtonProps) {
	return (
		<button
			className={`inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed ${variantClasses[variant]} ${className}`}
			disabled={disabled || loading}
			{...props}
		>
			{loading && (
				<svg
					className="mr-2 h-4 w-4 animate-spin"
					viewBox="0 0 24 24"
					fill="none"
					role="img"
					aria-label="Loading"
				>
					<circle
						className="opacity-25"
						cx="12"
						cy="12"
						r="10"
						stroke="currentColor"
						strokeWidth="4"
					/>
					<path
						className="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
					/>
				</svg>
			)}
			{children}
		</button>
	);
}
