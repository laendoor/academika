import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PlanesList } from "@/components/workspace/PlanesList";
import { usePlanes } from "@/hooks/workspace";
import * as lookups from "@/lib/api/lookups";
import type { PlanDetail, PlanRow } from "@/lib/api/workspace";
import * as workspace from "@/lib/api/workspace";

vi.mock("@/hooks/workspace", () => ({ usePlanes: vi.fn() }));
vi.mock("@/lib/api/workspace", () => ({
	getCarreras: vi.fn(),
	getPlanDetail: vi.fn(),
}));
vi.mock("@/lib/api/lookups", () => ({
	getNivelesCarrera: vi.fn(),
	getNucleosCarrera: vi.fn(),
}));

const usePlanesMock = vi.mocked(usePlanes);
const getCarreras = vi.mocked(workspace.getCarreras);
const getPlanDetail = vi.mocked(workspace.getPlanDetail);
const getNivelesCarrera = vi.mocked(lookups.getNivelesCarrera);
const getNucleosCarrera = vi.mocked(lookups.getNucleosCarrera);

function makePlan(id: string): PlanRow {
	return {
		id,
		carrera_id: "c1",
		carrera_nombre: "TPI",
		nombre: `Plan ${id}`,
		nivel: "grado",
		anio: 2015,
		vigente: true,
	};
}

function makeDetail(): PlanDetail {
	return {
		id: "p1",
		carrera_id: "c1",
		carrera_nombre: "TPI",
		nombre: "Plan p1",
		nivel: "grado",
		anio: 2015,
		vigente: true,
		materias: [
			{
				id: "m1",
				codigo: "MAT1",
				sigla: null,
				nombre: "Matemática I",
				creditos: 6,
				nucleo: "basico",
				horas_semanales: 4,
				carga_horaria_total: 64,
			},
		],
	};
}

describe("PlanesList", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		usePlanesMock.mockReturnValue({
			items: [],
			total: 0,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		getCarreras.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });
		getNivelesCarrera.mockResolvedValue({ ok: true, data: [] });
		getNucleosCarrera.mockResolvedValue({ ok: true, data: [] });
	});

	it("renderiza planes con nivel por lookup", async () => {
		usePlanesMock.mockReturnValue({
			items: [makePlan("p1")],
			total: 1,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		getNivelesCarrera.mockResolvedValue({
			ok: true,
			data: [{ key: "grado", label: "Grado" }],
		});

		render(<PlanesList />);

		expect(screen.getByText("Plan p1")).toBeInTheDocument();
		await waitFor(() => expect(screen.getByText("Grado")).toBeInTheDocument());
	});

	it("muestra mensaje vacío", () => {
		render(<PlanesList />);
		expect(screen.getByText("Sin planes.")).toBeInTheDocument();
	});

	it("carga opciones de carreras en el filtro", async () => {
		getCarreras.mockResolvedValue({
			ok: true,
			data: { total: 1, items: [{ id: "c1", nombre: "TPI", codigo: "TPI" }] },
		});

		render(<PlanesList />);

		await waitFor(() => expect(screen.getByText("TPI")).toBeInTheDocument());
	});

	it("click en un plan abre el modal con sus materias", async () => {
		usePlanesMock.mockReturnValue({
			items: [makePlan("p1")],
			total: 1,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		getPlanDetail.mockResolvedValue({ ok: true, data: makeDetail() });
		getNucleosCarrera.mockResolvedValue({
			ok: true,
			data: [{ key: "basico", label: "Básico" }],
		});

		render(<PlanesList />);

		fireEvent.click(screen.getByRole("button", { name: "Plan p1" }));

		await waitFor(() =>
			expect(screen.getByText("Matemática I")).toBeInTheDocument(),
		);
		expect(getPlanDetail).toHaveBeenCalledWith("p1");
		await waitFor(() => expect(screen.getByText("Básico")).toBeInTheDocument());
	});
});
