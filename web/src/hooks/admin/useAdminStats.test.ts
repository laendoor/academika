import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAdminStats } from "@/hooks/admin/useAdminStats";
import * as workspace from "@/lib/api/workspace";

vi.mock("@/lib/api/workspace", () => ({
	getEstudiantes: vi.fn(),
	getMaterias: vi.fn(),
	getCarreras: vi.fn(),
	getPlanes: vi.fn(),
}));

const getEstudiantes = vi.mocked(workspace.getEstudiantes);
const getMaterias = vi.mocked(workspace.getMaterias);
const getCarreras = vi.mocked(workspace.getCarreras);
const getPlanes = vi.mocked(workspace.getPlanes);

describe("useAdminStats", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga totales de estudiantes, materias, carreras y planes", async () => {
		getEstudiantes.mockResolvedValue({
			ok: true,
			data: { total: 120, items: [] },
		});
		getMaterias.mockResolvedValue({ ok: true, data: { total: 45, items: [] } });
		getCarreras.mockResolvedValue({ ok: true, data: { total: 8, items: [] } });
		getPlanes.mockResolvedValue({ ok: true, data: { total: 12, items: [] } });

		const { result } = renderHook(() => useAdminStats());

		expect(result.current.status).toBe("loading");
		await waitFor(() => expect(result.current.status).toBe("ok"));
		expect(result.current.estudiantes).toBe(120);
		expect(result.current.materias).toBe(45);
		expect(result.current.carreras).toBe(8);
		expect(result.current.planes).toBe(12);
	});

	it("marca error si alguna consulta falla", async () => {
		getEstudiantes.mockResolvedValue({
			ok: true,
			data: { total: 120, items: [] },
		});
		getMaterias.mockResolvedValue({ ok: false, error: "boom" });

		const { result } = renderHook(() => useAdminStats());

		await waitFor(() => expect(result.current.status).toBe("error"));
	});
});
