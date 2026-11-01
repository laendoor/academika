import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Tabs } from "@/components/ui/Tabs";

function renderTabs() {
	render(
		<Tabs
			items={[
				{ label: "Primero", content: <p>uno</p> },
				{ label: "Segundo", content: <p>dos</p> },
				{ label: "Tercero", content: <p>tres</p> },
			]}
		/>,
	);
	return screen.getAllByRole("tab");
}

describe("Tabs", () => {
	it("expone tablist, tab y tabpanel con aria-selected", () => {
		renderTabs();

		expect(screen.getByRole("tablist")).toBeInTheDocument();
		expect(screen.getByRole("tabpanel")).toHaveTextContent("uno");
		expect(screen.getByRole("tab", { name: "Primero" })).toHaveAttribute(
			"aria-selected",
			"true",
		);
		expect(screen.getByRole("tab", { name: "Segundo" })).toHaveAttribute(
			"aria-selected",
			"false",
		);
	});

	// Radix mueve el foco en un setTimeout, así que el cambio llega después del evento.
	it("las flechas mueven la selección, el foco y el panel", async () => {
		const [first] = renderTabs();
		first.focus();

		fireEvent.keyDown(first, { key: "ArrowRight" });

		const second = screen.getByRole("tab", { name: "Segundo" });
		await waitFor(() => expect(second).toHaveFocus());
		expect(second).toHaveAttribute("aria-selected", "true");
		expect(screen.getByRole("tabpanel")).toHaveTextContent("dos");
	});

	it("la flecha izquierda da la vuelta al último tab", async () => {
		const [first] = renderTabs();
		first.focus();

		fireEvent.keyDown(first, { key: "ArrowLeft" });

		const last = screen.getByRole("tab", { name: "Tercero" });
		await waitFor(() => expect(last).toHaveFocus());
		expect(last).toHaveAttribute("aria-selected", "true");
	});

	it("el click elige el tab", () => {
		renderTabs();

		fireEvent.mouseDown(screen.getByRole("tab", { name: "Tercero" }));

		expect(screen.getByRole("tabpanel")).toHaveTextContent("tres");
	});
});
