import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Input } from "@/components/ui/input";

describe("Input", () => {
	it("renders with label", () => {
		render(<Input label="Age" />);
		expect(screen.getByLabelText("Age")).toBeInTheDocument();
	});

	it("generates id from label when not provided", () => {
		render(<Input label="Person Age" />);
		expect(screen.getByLabelText("Person Age")).toHaveAttribute("id", "person-age");
	});

	it("uses provided id", () => {
		render(<Input label="Age" id="custom-id" />);
		expect(screen.getByLabelText("Age")).toHaveAttribute("id", "custom-id");
	});

	it("shows error message", () => {
		render(<Input label="Age" error="Age is required" />);
		expect(screen.getByText("Age is required")).toBeInTheDocument();
	});

	it("applies error styling when error is present", () => {
		render(<Input label="Age" error="Invalid" />);
		const input = screen.getByLabelText("Age");
		expect(input.className).toContain("border-danger");
	});

	it("calls onChange when typing", async () => {
		const user = userEvent.setup();
		const onChange = vi.fn();
		render(<Input label="Name" onChange={onChange} />);

		await user.type(screen.getByLabelText("Name"), "test");
		expect(onChange).toHaveBeenCalled();
	});

	it("forwards additional props", () => {
		render(<Input label="Amount" type="number" min={0} placeholder="Enter amount" />);
		const input = screen.getByLabelText("Amount");
		expect(input).toHaveAttribute("type", "number");
		expect(input).toHaveAttribute("placeholder", "Enter amount");
	});
});
