import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";

import { Modal } from "@/components/ui/Modal";

function Harness() {
	const [open, setOpen] = useState(false);
	return (
		<>
			<button type="button" onClick={() => setOpen(true)}>
				Abrir
			</button>
			{open && (
				<Modal title="Detalle" onClose={() => setOpen(false)}>
					<p>contenido</p>
				</Modal>
			)}
		</>
	);
}

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

	it("atrapa el foco adentro y lo devuelve al abridor al cerrar", async () => {
		render(<Harness />);

		const trigger = screen.getByRole("button", { name: "Abrir" });
		trigger.focus();
		fireEvent.click(trigger);

		const panel = screen.getByRole("dialog", { name: "Detalle" });
		expect(panel).toHaveFocus();

		fireEvent.keyDown(document, { key: "Tab" });
		expect(panel.contains(document.activeElement)).toBe(true);

		fireEvent.keyDown(document, { key: "Escape" });
		expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
		await waitFor(() => expect(trigger).toHaveFocus());
	});
});
