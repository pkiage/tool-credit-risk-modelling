import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Card } from "@/components/ui/card";

describe("Card", () => {
	it("renders children", () => {
		render(<Card>Card content</Card>);
		expect(screen.getByText("Card content")).toBeInTheDocument();
	});

	it("renders title when provided", () => {
		render(<Card title="My Card">Content</Card>);
		expect(screen.getByText("My Card")).toBeInTheDocument();
	});

	it("does not render title section when no title", () => {
		const { container } = render(<Card>Content</Card>);
		expect(container.querySelector(".border-b")).toBeNull();
	});

	it("applies custom className", () => {
		const { container } = render(<Card className="custom-class">Content</Card>);
		expect(container.firstElementChild?.className).toContain("custom-class");
	});
});
