import { describe, expect, it, vi } from "vitest";

import * as client from "@/lib/api/client";
import {
	getCursadas,
	getEstudianteDetalle,
	getPlanDetail,
	getPlanes,
} from "@/lib/api/workspace";

vi.mock("@/lib/api/client", () => ({ get: vi.fn() }));

const getMock = vi.mocked(client.get);

describe("getPlanes", () => {
	it("incluye el filtro por carrera solo cuando se pasa", async () => {
		getMock.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });

		await getPlanes(0, 20, "c1");
		expect(getMock).toHaveBeenCalledWith(
			"/api/planes?skip=0&limit=20&carrera_id=c1",
		);

		await getPlanes();
		expect(getMock).toHaveBeenCalledWith("/api/planes?skip=0&limit=20");
	});
});

describe("getPlanDetail", () => {
	it("encodea el id en la URL", async () => {
		getMock.mockResolvedValue({ ok: true, data: null });

		await getPlanDetail("a/b");
		expect(getMock).toHaveBeenCalledWith("/api/planes/a%2Fb");
	});
});

describe("getCursadas", () => {
	it("omite los filtros vacíos y repite estado_cursada", async () => {
		getMock.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });

		await getCursadas(0, 20, {
			carrera_id: "c1",
			alumno: "",
			anio: 2024,
			estado_cursada: ["regular", "aprobado"],
		});

		expect(getMock).toHaveBeenCalledWith(
			"/api/workspace/cursadas?skip=0&limit=20&carrera_id=c1&anio=2024&estado_cursada=regular&estado_cursada=aprobado",
		);
	});

	it("sin filtros manda solo la paginación", async () => {
		getMock.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });

		await getCursadas();
		expect(getMock).toHaveBeenCalledWith(
			"/api/workspace/cursadas?skip=0&limit=20",
		);
	});
});

describe("getEstudianteDetalle", () => {
	it("encodea el id en la URL", async () => {
		getMock.mockResolvedValue({ ok: true, data: null });

		await getEstudianteDetalle("a/b");
		expect(getMock).toHaveBeenCalledWith("/api/workspace/estudiantes/a%2Fb");
	});
});
