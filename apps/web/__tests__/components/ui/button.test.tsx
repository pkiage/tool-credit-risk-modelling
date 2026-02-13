import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Button } from "@/components/ui/button";

describe("Button", () => {
	it("renders children", () => {
		render(<Button>Click me</Button>);
		expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
	});

	it("calls onClick when clicked", async () => {
		const user = userEvent.setup();
		const onClick = vi.fn();
		render(<Button onClick={onClick}>Click</Button>);

		await user.click(screen.getByRole("button"));
		expect(onClick).toHaveBeenCalledOnce();
	});

	it("shows loading spinner when loading", () => {
		render(<Button loading>Submit</Button>);
		const button = screen.getByRole("button");
		expect(button).toBeDisabled();
		expect(button.querySelector("svg")).toBeInTheDocument();
	});

	it("is disabled when disabled prop is set", () => {
		render(<Button disabled>Disabled</Button>);
		expect(screen.getByRole("button")).toBeDisabled();
	});

	it("applies primary variant by default", () => {
		render(<Button>Primary</Button>);
		const button = screen.getByRole("button");
		expect(button.className).toContain("bg-primary");
	});

	it("applies secondary variant", () => {
		render(<Button variant="secondary">Secondary</Button>);
		const button = screen.getByRole("button");
		expect(button.className).toContain("bg-surface-elevated");
	});

	it("applies danger variant", () => {
		render(<Button variant="danger">Delete</Button>);
		const button = screen.getByRole("button");
		expect(button.className).toContain("bg-danger");
	});

	it("has type=button by default", () => {
		render(<Button>Click</Button>);
		expect(screen.getByRole("button")).toHaveAttribute("type", "button");
	});
});
