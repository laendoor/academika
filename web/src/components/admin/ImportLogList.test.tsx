import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import {
	formatIsoLocal,
	ImportLogList,
	parseDate,
	resubmittedIds,
} from "@/components/admin/ImportLogList";
import type { SourceItem } from "@/lib/api/sources";

function makeSource(overrides: Partial<SourceItem> = {}): SourceItem {
	return {
		id: "s1",
		created_at: "2026-10-12T14:32:08",
		status: "ok",
		details: {
			sheet_type: "alumnos",
			files: ["alumnos.csv"],
			processed: 1240,
			skipped: 3,
			error: null,
			file_hash: "abc",
			uploader_email: "lean@unq.edu.ar",
			skipped_sample: [],
		},
		...overrides,
	};
}

describe("formatIsoLocal", () => {
	it("formatea ISO localsortable", () => {
		expect(formatIsoLocal("2026-10-12T14:32:08")).toBe("2026-10-12 14:32:08");
	});

	it("tolera el str() de Python del payload WS", () => {
		expect(formatIsoLocal("2026-10-12 14:32:08.123456+00:00")).toMatch(
			/^2026-10-12 \d{2}:\d{2}:\d{2}$/,
		);
	});

	it("fecha inválida no revienta: devuelve el crudo", () => {
		expect(parseDate("no-es-fecha")).toBeNull();
		expect(formatIsoLocal("no-es-fecha")).toBe("no-es-fecha");
	});

	it("recorta microsegundos a millis (Safari)", () => {
		expect(
			parseDate("2026-10-12T18:05:00.123456+00:00")?.getMilliseconds(),
		).toBe(123);
	});
});

describe("resubmittedIds", () => {
	it("marca la fila nueva cuando el hash ya apareció en una más vieja", () => {
		const items = [makeSource({ id: "nueva" }), makeSource({ id: "vieja" })];
		expect(resubmittedIds(items)).toEqual(new Set(["nueva"]));
	});

	it("ignora filas sin hash", () => {
		const items = [
			makeSource({
				id: "a",
				details: { ...makeSource().details, file_hash: null },
			}),
			makeSource({
				id: "b",
				details: { ...makeSource().details, file_hash: null },
			}),
		];
		expect(resubmittedIds(items)).toEqual(new Set());
	});
});

describe("ImportLogList", () => {
	it("lista plana con fecha ISO, archivo, tipo, conteos y usuario", () => {
		render(
			<ImportLogList
				items={[
					makeSource({ id: "1", created_at: "2026-10-12T14:32:08" }),
					makeSource({ id: "2", created_at: "2026-10-11T18:20:01" }),
				]}
			/>,
		);

		expect(screen.queryByRole("heading")).not.toBeInTheDocument();
		expect(screen.getByText("2026-10-12 14:32:08")).toBeInTheDocument();
		expect(screen.getAllByText("alumnos.csv")).toHaveLength(2);
		expect(screen.getAllByText("Alumnos")).toHaveLength(2);
		expect(screen.getAllByText("por lean", { exact: false })).toHaveLength(2);
	});

	it("muestra el error en vez de conteos y unifica el icono de re-subida", () => {
		const { container } = render(
			<ImportLogList
				items={[
					makeSource({ id: "nueva", created_at: "2026-10-12T14:32:08" }),
					makeSource({
						id: "vieja",
						created_at: "2026-10-12T11:05:44",
						status: "error",
						details: {
							sheet_type: null,
							files: ["raro.csv"],
							processed: 0,
							skipped: 0,
							error: "tipo desconocido",
							file_hash: "abc",
							uploader_email: null,
						},
					}),
				]}
			/>,
		);

		expect(screen.getByText("· error: tipo desconocido")).toBeInTheDocument();
		const tips = [...container.querySelectorAll('[role="tooltip"]')].map(
			(el) => el.textContent,
		);
		expect(tips.some((t) => t?.includes("Re-subida"))).toBe(true);
		expect(tips.some((t) => t?.includes("tipo desconocido"))).toBe(true);
		expect(screen.getByText("por —", { exact: false })).toBeInTheDocument();
	});

	it("tooltip de ok explica conteos", () => {
		const { container } = render(
			<ImportLogList items={[makeSource({ id: "1" })]} />,
		);
		const tip = container.querySelector('[role="tooltip"]')?.textContent;
		expect(tip).toContain("OK");
		expect(tip).toContain("omitidas");
	});

	it("fila con fecha del WS (formato Python) se renderiza sin reventar", () => {
		render(
			<ImportLogList
				items={[
					makeSource({
						id: "1",
						created_at: "2026-10-12 14:32:08.123456+00:00",
					}),
				]}
			/>,
		);
		expect(
			screen.getByText(/^2026-10-12 \d{2}:\d{2}:\d{2}$/),
		).toBeInTheDocument();
	});
});

describe("ImportLogList modal", () => {
	function openRow(item: SourceItem) {
		render(<ImportLogList items={[item]} />);
		fireEvent.click(screen.getByRole("button", { name: /alumnos.csv/ }));
	}

	it("abre el modal con el contenido directo", () => {
		openRow(
			makeSource({
				id: "1",
				details: {
					...makeSource().details,
					preview: ["h1;h2", "1;x"],
					preview_truncated: true,
				},
			}),
		);
		expect(screen.getByRole("dialog")).toBeInTheDocument();
		expect(screen.getByText(/h1;h2/)).toBeInTheDocument();
		expect(screen.getByText(/muestra truncada/)).toBeInTheDocument();
	});

	it("cierra con Escape y con el botón", () => {
		openRow(makeSource({ id: "1" }));
		expect(screen.getByRole("dialog")).toBeInTheDocument();
		fireEvent.keyDown(document, { key: "Escape" });
		expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

		fireEvent.click(screen.getByRole("button", { name: /alumnos.csv/ }));
		fireEvent.click(screen.getByRole("button", { name: "Cerrar detalle" }));
		expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
	});
});
