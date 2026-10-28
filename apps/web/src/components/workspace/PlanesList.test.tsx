import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PlanesList } from "@/components/workspace/PlanesList";
import { usePlanes } from "@/hooks/workspace";
import type { ApiResult } from "@/lib/api/client";
import * as lookups from "@/lib/api/lookups";
import type { PlanDetail, PlanRow } from "@/lib/api/workspace";
import * as workspace from "@/lib/api/workspace";

vi.mock("@/hooks/workspace", () => ({ usePlanes: vi.fn() }));
vi.mock("@/lib/api/workspace", () => ({
	getCarreras: vi.fn(),
	getPlanDetail: vi.fn(),
}));
vi.mock("@/lib/api/lookups", async (importOriginal) => ({
	...(await importOriginal<typeof import("@/lib/api/lookups")>()),
	getNivelesCarrera: vi.fn(),
	getNucleosCarrera: vi.fn(),
}));

const usePlanesMock = vi.mocked(usePlanes);
const getCarreras = vi.mocked(workspace.getCarreras);
const getPlanDetail = vi.mocked(workspace.getPlanDetail);
const getNivelesCarrera = vi.mocked(lookups.getNivelesCarrera);
const getNucleosCarrera = vi.mocked(lookups.getNucleosCarrera);

function makePlan(id: string, overrides: Partial<PlanRow> = {}): PlanRow {
	return {
		id,
		carrera_id: "c1",
		carrera_nombre: "TPI",
		nombre: `Plan ${id}`,
		nivel: "grado",
		anio: 2015,
		vigente: true,
		...overrides,
	};
}

function makeDetail(id = "p1"): PlanDetail {
	return {
		id,
		carrera_id: "c1",
		carrera_nombre: "TPI",
		nombre: `Plan ${id}`,
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

function mockList(items: PlanRow[], total: number, error?: string) {
	usePlanesMock.mockReturnValue({
		items,
		total,
		loading: false,
		error,
		refresh: vi.fn(),
	});
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
		mockList([makePlan("p1")], 1);
		getNivelesCarrera.mockResolvedValue({
			ok: true,
			data: [{ key: "grado", label: "Grado" }],
		});

		render(<PlanesList />);

		expect(screen.getByText("Plan p1")).toBeInTheDocument();
		expect(screen.getByText("TPI")).toBeInTheDocument();
		await waitFor(() => expect(screen.getByText("Grado")).toBeInTheDocument());
	});

	it("muestra guiones sin nivel y No cuando no está vigente", () => {
		mockList([makePlan("p1", { nivel: null, vigente: false })], 1);
		render(<PlanesList />);
		expect(screen.getAllByText("—").length).toBeGreaterThan(0);
		expect(screen.getByText("No")).toBeInTheDocument();
	});

	it("muestra mensaje vacío", () => {
		render(<PlanesList />);
		expect(screen.getByText("Sin planes.")).toBeInTheDocument();
	});

	it("muestra el error del hook sin mensaje vacío", () => {
		mockList([], 0, "Falló la carga");
		render(<PlanesList />);
		expect(screen.getByText("Falló la carga")).toBeInTheDocument();
		expect(screen.queryByText("Sin planes.")).not.toBeInTheDocument();
	});

	it("avisa por consola si fallan carreras o lookups", async () => {
		const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
		getCarreras.mockResolvedValue({ ok: false, error: "caído" });
		getNivelesCarrera.mockResolvedValue({ ok: false, error: "caído" });
		getNucleosCarrera.mockResolvedValue({ ok: false, error: "caído" });

		render(<PlanesList />);

		await waitFor(() => expect(warn).toHaveBeenCalledTimes(3));
		warn.mockRestore();
	});

	it("filtrar por carrera resetea la paginación", async () => {
		getCarreras.mockResolvedValue({
			ok: true,
			data: { total: 1, items: [{ id: "c1", nombre: "TPI", codigo: "TPI" }] },
		});
		render(<PlanesList />);

		const select = await screen.findByRole("combobox", {
			name: "Filtrar por carrera",
		});
		fireEvent.change(select, { target: { value: "c1" } });

		expect(usePlanesMock).toHaveBeenLastCalledWith(
			expect.objectContaining({ carrera_id: "c1", skip: 0 }),
		);
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
		mockList([makePlan("p1")], 1);
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

	it("muestra el error si falla el detalle", async () => {
		mockList([makePlan("p1")], 1);
		getPlanDetail.mockResolvedValue({ ok: false, error: "Plan no encontrado" });

		render(<PlanesList />);
		fireEvent.click(screen.getByRole("button", { name: "Plan p1" }));

		await waitFor(() =>
			expect(screen.getByRole("alert")).toHaveTextContent("Plan no encontrado"),
		);
	});

	it("ignora respuestas viejas ante clicks rápidos", async () => {
		mockList([makePlan("p1"), makePlan("p2")], 2);
		const resolvers: {
			p1?: (r: ApiResult<PlanDetail>) => void;
			p2?: (r: ApiResult<PlanDetail>) => void;
		} = {};
		getPlanDetail.mockImplementation(
			(id: string) =>
				new Promise<ApiResult<PlanDetail>>((resolve) => {
					resolvers[id as "p1" | "p2"] = resolve;
				}),
		);

		render(<PlanesList />);
		fireEvent.click(screen.getByRole("button", { name: "Plan p1" }));
		fireEvent.click(screen.getByRole("button", { name: "Plan p2" }));

		await waitFor(() => expect(getPlanDetail).toHaveBeenCalledTimes(2));
		expect(resolvers.p1).toBeDefined();
		expect(resolvers.p2).toBeDefined();
		resolvers.p2?.({ ok: true, data: makeDetail("p2") });
		resolvers.p1?.({ ok: true, data: makeDetail("p1") });

		await waitFor(() =>
			expect(
				screen.getByRole("dialog", { name: "Detalle de Plan p2" }),
			).toBeInTheDocument(),
		);
		expect(
			screen.queryByRole("dialog", { name: "Detalle de Plan p1" }),
		).not.toBeInTheDocument();
	});

	it("cierra el modal con el botón Cerrar", async () => {
		mockList([makePlan("p1")], 1);
		getPlanDetail.mockResolvedValue({ ok: true, data: makeDetail() });

		render(<PlanesList />);
		fireEvent.click(screen.getByRole("button", { name: "Plan p1" }));
		await waitFor(() =>
			expect(screen.getByText("Matemática I")).toBeInTheDocument(),
		);

		fireEvent.click(screen.getByRole("button", { name: "Cerrar detalle" }));
		await waitFor(() =>
			expect(screen.queryByText("Matemática I")).not.toBeInTheDocument(),
		);
	});
});
