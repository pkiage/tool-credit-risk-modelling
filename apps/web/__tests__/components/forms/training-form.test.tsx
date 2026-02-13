import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TrainingForm } from "@/components/forms/training-form";

describe("TrainingForm", () => {
	it("renders model type select with three options", () => {
		render(<TrainingForm onSubmit={vi.fn()} />);
		const options = screen.getAllByRole("option");
		expect(options).toHaveLength(3);
		expect(options[0]).toHaveTextContent("Logistic Regression");
		expect(options[1]).toHaveTextContent("XGBoost");
		expect(options[2]).toHaveTextContent("Random Forest");
	});

	it("renders test size slider", () => {
		render(<TrainingForm onSubmit={vi.fn()} />);
		expect(screen.getByLabelText("Test Size")).toBeInTheDocument();
	});

	it("renders CV folds slider", () => {
		render(<TrainingForm onSubmit={vi.fn()} />);
		expect(screen.getByLabelText("CV Folds")).toBeInTheDocument();
	});

	it("renders undersample checkbox", () => {
		render(<TrainingForm onSubmit={vi.fn()} />);
		expect(screen.getByLabelText("Undersample majority class")).toBeInTheDocument();
	});

	it("calls onSubmit with default config", async () => {
		const user = userEvent.setup();
		const onSubmit = vi.fn();
		render(<TrainingForm onSubmit={onSubmit} />);

		await user.click(screen.getByRole("button", { name: "Train Model" }));

		expect(onSubmit).toHaveBeenCalledWith({
			model_type: "logistic_regression",
			test_size: 0.2,
			random_state: 42,
			undersample: false,
			cv_folds: 5,
		});
	});

	it("shows loading state", () => {
		render(<TrainingForm onSubmit={vi.fn()} loading />);
		const button = screen.getByRole("button", { name: /Training Model/i });
		expect(button).toBeDisabled();
	});

	it("submits with changed model type", async () => {
		const user = userEvent.setup();
		const onSubmit = vi.fn();
		render(<TrainingForm onSubmit={onSubmit} />);

		await user.selectOptions(screen.getByLabelText("Model Type"), "xgboost");
		await user.click(screen.getByRole("button", { name: "Train Model" }));

		expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ model_type: "xgboost" }));
	});
});
