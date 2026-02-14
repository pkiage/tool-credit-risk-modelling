import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Select } from "@/components/ui/select";

const options = [
	{ value: "a", label: "Option A" },
	{ value: "b", label: "Option B" },
	{ value: "c", label: "Option C" },
];

describe("Select", () => {
	it("renders with label", () => {
		render(<Select label="Choose" options={options} />);
		expect(screen.getByLabelText("Choose")).toBeInTheDocument();
	});

	it("renders all options", () => {
		render(<Select label="Choose" options={options} />);
		expect(screen.getAllByRole("option")).toHaveLength(3);
	});

	it("generates id from label", () => {
		render(<Select label="Model Type" options={options} />);
		expect(screen.getByLabelText("Model Type")).toHaveAttribute("id", "model-type");
	});

	it("shows error message", () => {
		render(<Select label="Choose" options={options} error="Required" />);
		expect(screen.getByText("Required")).toBeInTheDocument();
	});

	it("applies error styling", () => {
		render(<Select label="Choose" options={options} error="Required" />);
		const select = screen.getByLabelText("Choose");
		expect(select.className).toContain("border-danger");
	});

	it("calls onChange when selection changes", async () => {
		const user = userEvent.setup();
		const onChange = vi.fn();
		render(<Select label="Choose" options={options} onChange={onChange} />);

		await user.selectOptions(screen.getByLabelText("Choose"), "b");
		expect(onChange).toHaveBeenCalled();
	});

	it("sets correct option values", () => {
		render(<Select label="Choose" options={options} />);
		const optionElements = screen.getAllByRole("option");
		expect(optionElements[0]).toHaveValue("a");
		expect(optionElements[1]).toHaveValue("b");
		expect(optionElements[2]).toHaveValue("c");
	});
});
