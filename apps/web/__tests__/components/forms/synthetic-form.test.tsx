import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SyntheticForm } from "@/components/forms/synthetic-form";

describe("SyntheticForm", () => {
	it("renders preset select with options", () => {
		render(<SyntheticForm onGenerate={vi.fn()} loading={false} />);
		const options = screen.getAllByRole("option");
		expect(options.length).toBeGreaterThanOrEqual(5);
		expect(options[0]).toHaveTextContent("Custom");
		expect(options[1]).toHaveTextContent("Stress Test");
	});

	it("renders number of samples slider", () => {
		render(<SyntheticForm onGenerate={vi.fn()} loading={false} />);
		expect(screen.getByLabelText("Number of Samples")).toBeInTheDocument();
	});

	it("renders default rate slider", () => {
		render(<SyntheticForm onGenerate={vi.fn()} loading={false} />);
		expect(screen.getByLabelText("Default Rate")).toBeInTheDocument();
	});

	it("renders random seed input", () => {
		render(<SyntheticForm onGenerate={vi.fn()} loading={false} />);
		expect(screen.getByLabelText("Random Seed")).toBeInTheDocument();
	});

	it("calls onGenerate with default config on submit", () => {
		const onGenerate = vi.fn();
		render(<SyntheticForm onGenerate={onGenerate} loading={false} />);

		const button = screen.getByRole("button", { name: "Generate Synthetic Data" });
		const form = button.closest("form") as HTMLFormElement;
		expect(form).not.toBeNull();
		fireEvent.submit(form);

		expect(onGenerate).toHaveBeenCalledWith({
			n_samples: 5000,
			default_rate: 0.22,
			distributions: [],
			random_seed: 42,
		});
	});

	it("shows loading state", () => {
		render(<SyntheticForm onGenerate={vi.fn()} loading />);
		const button = screen.getByRole("button", { name: /Generating/i });
		expect(button).toBeDisabled();
	});

	it("updates fields when preset is selected", async () => {
		const user = userEvent.setup();
		render(<SyntheticForm onGenerate={vi.fn()} loading={false} />);

		await user.selectOptions(screen.getByLabelText("Preset"), "Low Default");

		const defaultRateSlider = screen.getByLabelText("Default Rate");
		expect(defaultRateSlider).toHaveValue("0.05");
	});
});
