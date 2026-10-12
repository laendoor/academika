import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ImportDetailModal } from "@/components/admin/ImportDetailModal";
import type { SourceItem } from "@/lib/api/sources";

function makeItem(overrides: Partial<SourceItem> = {}): SourceItem {
	return {
		id: "s1",
		created_at: "2026-10-12T14:32:08",
		status: "ok",
		details: {
			sheet_type: "historial_cursadas",
			files: ["historia.csv"],
			processed: 181,
			skipped: 30,
			error: null,
			preview: ["h1;h2", "1;x"],
			preview_truncated: false,
			skipped_sample: ["import_x: missing refs — skipping doc_id=1"],
			skipped_sample_truncated: true,
		},
		...overrides,
	};
}

function renderModal(item: SourceItem = makeItem()) {
	const onClose = vi.fn();
	render(
		<ImportDetailModal
			item={item}
			subtitle="historia.csv — 2026-10-12 14:32:08 — Historial de cursadas"
			onClose={onClose}
		/>,
	);
	return onClose;
}

describe("ImportDetailModal", () => {
	it("muestra resumen, muestra y no procesadas con motivo", () => {
		renderModal();
		expect(screen.getByRole("dialog")).toBeInTheDocument();
		expect(screen.getByText(/procesadas:/)).toBeInTheDocument();
		expect(screen.getByText(/h1;h2/)).toBeInTheDocument();
		expect(screen.getByText(/No procesadas/)).toBeInTheDocument();
		expect(
			screen.getByText(/missing refs — skipping doc_id=1/),
		).toBeInTheDocument();
		expect(screen.getByText(/mostrando 1 de 30/)).toBeInTheDocument();
	});

	it("error va en bloque propio y sin muestra hay fallback", () => {
		renderModal(
			makeItem({
				status: "error",
				details: {
					...makeItem().details,
					error: "encoding inválido",
					preview: null,
					skipped: 0,
					skipped_sample: [],
				},
			}),
		);
		const blocks = screen.getAllByText("encoding inválido");
		expect(blocks[blocks.length - 1].tagName).toBe("PRE");
		expect(
			screen.getByText("sin muestra (importación anterior)"),
		).toBeInTheDocument();
		expect(screen.queryByText("No procesadas")).not.toBeInTheDocument();
	});

	it("sin flag (fila vieja) deduce el recorte por conteo", () => {
		renderModal(
			makeItem({
				details: {
					...makeItem().details,
					skipped: 16,
					skipped_sample: ["a", "b", "c", "d", "e"],
					skipped_sample_truncated: undefined,
				},
			}),
		);
		expect(screen.getByText(/mostrando 5 de 16/)).toBeInTheDocument();
	});

	it("cierra con Escape, backdrop y botón", () => {
		const onClose = renderModal();
		fireEvent.keyDown(document, { key: "Escape" });
		expect(onClose).toHaveBeenCalledTimes(1);

		fireEvent.click(screen.getByTestId("import-modal-backdrop"));
		expect(onClose).toHaveBeenCalledTimes(2);

		fireEvent.click(screen.getByRole("button", { name: "Cerrar detalle" }));
		expect(onClose).toHaveBeenCalledTimes(3);
	});
});
