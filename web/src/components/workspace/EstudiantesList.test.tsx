import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { EstudiantesList } from "@/components/workspace/EstudiantesList";
import { useEstudiantes } from "@/hooks/workspace";
import * as workspace from "@/lib/api/workspace";

vi.mock("@/hooks/workspace", () => ({ useEstudiantes: vi.fn() }));
vi.mock("@/lib/api/workspace", () => ({
	getCarreras: vi.fn(),
	getEstadosAcademicos: vi.fn(),
}));

const useEstudiantesMock = vi.mocked(useEstudiantes);
const getCarreras = vi.mocked(workspace.getCarreras);
const getEstadosAcademicos = vi.mocked(workspace.getEstadosAcademicos);

function makeEstudiante(id: string) {
	return {
		id,
		nombre: "Juan",
		apellido: "Perez",
		dni: "12345678",
		legajo: null,
		carreras: [
			{
				plan_id: "p1",
				plan_nombre: "Plan 2020",
				anio: 2020,
				vigente: true,
				carrera_id: "c1",
				carrera_nombre: "Ingeniería",
				estado_academico: "Activo",
				fecha_ingreso: null,
			},
		],
	};
}

describe("EstudiantesList", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		getCarreras.mockResolvedValue({
			ok: true,
			data: { total: 0, items: [] },
		});
		getEstadosAcademicos.mockResolvedValue({ ok: true, data: [] });
	});

	it("renderiza estudiantes", () => {
		useEstudiantesMock.mockReturnValue({
			items: [makeEstudiante("e1")],
			total: 1,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<EstudiantesList />);
		expect(screen.getByText("Perez")).toBeInTheDocument();
		expect(screen.getByText("Juan")).toBeInTheDocument();
		expect(screen.getByText("12345678")).toBeInTheDocument();
	});

	it("muestra mensaje vacío", () => {
		useEstudiantesMock.mockReturnValue({
			items: [],
			total: 0,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<EstudiantesList />);
		expect(screen.getByText("Sin estudiantes.")).toBeInTheDocument();
	});

	it("carga opciones de carreras en el filtro", async () => {
		useEstudiantesMock.mockReturnValue({
			items: [],
			total: 0,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		getCarreras.mockResolvedValue({
			ok: true,
			data: { total: 1, items: [{ id: "c1", nombre: "Ingeniería" }] },
		});

		render(<EstudiantesList />);

		await waitFor(() =>
			expect(screen.getByText("Ingeniería")).toBeInTheDocument(),
		);
	});
});
