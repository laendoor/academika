import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import {
	formatDayHeader,
	groupByDay,
	ImportLogList,
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
		},
		...overrides,
	};
}

const NOON = new Date(2026, 9, 12, 20, 0, 0);

describe("formatDayHeader", () => {
	it("etiqueta hoy y ayer en español", () => {
		expect(formatDayHeader("2026-10-12T14:32:08", NOON)).toMatch(/^Hoy · /);
		expect(formatDayHeader("2026-10-11T18:20:01", NOON)).toMatch(/^Ayer · /);
	});

	it("días viejos van sin etiqueta relativa", () => {
		const header = formatDayHeader("2026-10-10T09:00:00", NOON);
		expect(header).not.toMatch(/Hoy|Ayer/);
		expect(header).toContain("octubre");
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
	it("agrupa por día y muestra archivo, tipo, conteos y usuario", () => {
		render(
			<ImportLogList
				items={[
					makeSource({ id: "1", created_at: "2026-10-12T14:32:08" }),
					makeSource({ id: "2", created_at: "2026-10-11T18:20:01" }),
				]}
			/>,
		);

		expect(screen.getAllByRole("heading").length).toBe(2);
		expect(screen.getAllByText("alumnos.csv")).toHaveLength(2);
		expect(screen.getAllByText("Alumnos")).toHaveLength(2);
		const counts = `· ${(1240).toLocaleString("es-AR")} ok · ${(3).toLocaleString("es-AR")} omitidas`;
		expect(
			screen.getAllByText((_, el) => el?.textContent === counts),
		).toHaveLength(2);
		expect(screen.getAllByText("por lean", { exact: false })).toHaveLength(2);
		expect(screen.getAllByText(/\d{2}:\d{2}:\d{2}/)).toHaveLength(2);
	});

	it("muestra el error en vez de conteos y marca re-subidas", () => {
		render(
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
		expect(screen.getByText("re-subida")).toBeInTheDocument();
		expect(screen.getByText("por —", { exact: false })).toBeInTheDocument();
	});

	it("groupByDay preserva el orden DESC dentro del día", () => {
		const groups = groupByDay(
			[
				makeSource({ id: "1", created_at: "2026-10-12T14:32:08" }),
				makeSource({ id: "2", created_at: "2026-10-12T11:05:44" }),
			],
			NOON,
		);
		expect(groups).toHaveLength(1);
		expect(groups[0].items.map((i) => i.id)).toEqual(["1", "2"]);
	});
});
