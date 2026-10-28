import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Modal } from "@/components/ui/Modal";

describe("Modal", () => {
	it("muestra título y contenido, y enfoca el panel", () => {
		render(
			<Modal title="Detalle" onClose={() => {}}>
				<p>contenido</p>
			</Modal>,
		);

		expect(screen.getByRole("dialog", { name: "Detalle" })).toHaveFocus();
		expect(screen.getByText("contenido")).toBeInTheDocument();
	});

	it("cierra con Escape, con el backdrop y con el botón, no con click adentro", () => {
		const onClose = vi.fn();
		render(
			<Modal title="Detalle" onClose={onClose}>
				<p>contenido</p>
			</Modal>,
		);

		fireEvent.click(screen.getByText("contenido"));
		expect(onClose).not.toHaveBeenCalled();

		fireEvent.keyDown(document, { key: "Escape" });
		expect(onClose).toHaveBeenCalledTimes(1);

		fireEvent.click(screen.getByTestId("modal-backdrop"));
		expect(onClose).toHaveBeenCalledTimes(2);

		fireEvent.click(screen.getByRole("button", { name: "Cerrar detalle" }));
		expect(onClose).toHaveBeenCalledTimes(3);
	});
});
