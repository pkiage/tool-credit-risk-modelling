import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PredictionForm } from "@/components/forms/prediction-form";
import type { ModelMetadata } from "@/lib/types";
import * as validation from "@/lib/validation";

const mockModels: ModelMetadata[] = [
	{
		model_id: "model-001",
		model_type: "logistic_regression",
		threshold: 0.5,
		roc_auc: 0.85,
		accuracy: 0.82,
		created_at: "2025-01-01T00:00:00Z",
	},
	{
		model_id: "model-002",
		model_type: "xgboost",
		threshold: 0.45,
		roc_auc: 0.9,
		accuracy: 0.88,
		created_at: "2025-01-02T00:00:00Z",
	},
];

describe("PredictionForm", () => {
	it("shows warning when no models available", () => {
		render(<PredictionForm models={[]} onSubmit={vi.fn()} />);
		expect(screen.getByText(/No trained models available/)).toBeInTheDocument();
	});

	it("renders model select with models", () => {
		render(<PredictionForm models={mockModels} onSubmit={vi.fn()} />);
		const select = screen.getByLabelText("Select Model");
		expect(select).toBeInTheDocument();

		const options = select.querySelectorAll("option");
		expect(options).toHaveLength(2);
		expect(options[0].textContent).toContain("logistic_regression");
		expect(options[1].textContent).toContain("xgboost");
	});

	it("renders all loan fields", () => {
		render(<PredictionForm models={mockModels} onSubmit={vi.fn()} />);
		expect(screen.getByLabelText("Age")).toBeInTheDocument();
		expect(screen.getByLabelText("Annual Income")).toBeInTheDocument();
		expect(screen.getByLabelText("Loan Amount")).toBeInTheDocument();
	});

	it("shows submit button", () => {
		render(<PredictionForm models={mockModels} onSubmit={vi.fn()} />);
		expect(screen.getByRole("button", { name: "Get Prediction" })).toBeInTheDocument();
	});

	it("shows loading state", () => {
		render(<PredictionForm models={mockModels} onSubmit={vi.fn()} loading />);
		expect(screen.getByRole("button", { name: /Predicting/i })).toBeDisabled();
	});

	it("calls onSubmit with valid data", async () => {
		const user = userEvent.setup();
		const onSubmit = vi.fn();
		render(<PredictionForm models={mockModels} onSubmit={onSubmit} />);

		await user.click(screen.getByRole("button", { name: "Get Prediction" }));

		expect(onSubmit).toHaveBeenCalledWith(
			"model-001",
			expect.objectContaining({
				person_age: 30,
				person_income: 50000,
			}),
		);
	});

	it("displays validation errors and blocks submit", async () => {
		const user = userEvent.setup();
		const onSubmit = vi.fn();

		// Mock validation to return errors (avoids jsdom number input limitations)
		vi.spyOn(validation, "validateLoanApplication").mockReturnValueOnce({
			person_age: "Age must be a whole number between 18 and 120",
		});

		render(<PredictionForm models={mockModels} onSubmit={onSubmit} />);

		await user.click(screen.getByRole("button", { name: "Get Prediction" }));

		expect(onSubmit).not.toHaveBeenCalled();
		expect(screen.getByText(/Age must be/)).toBeInTheDocument();

		vi.restoreAllMocks();
	});
});
