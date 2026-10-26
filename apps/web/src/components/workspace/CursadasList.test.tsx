import {
	fireEvent,
	render,
	screen,
	waitFor,
	within,
} from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { CursadasList } from "@/components/workspace/CursadasList";
import {
	useEstadosAcademicos,
	useEstadosCursada,
	useTiposCursada,
} from "@/hooks/lookups";
import {
	useCarreras,
	useCursadas,
	useEstudianteDetalle,
} from "@/hooks/workspace";
import type { CursadaRow } from "@/lib/api/workspace";

vi.mock("@/hooks/workspace", () => ({
	useCursadas: vi.fn(),
	useCarreras: vi.fn(),
	useEstudianteDetalle: vi.fn(),
}));
vi.mock("@/hooks/lookups", () => ({
	useEstadosCursada: vi.fn(),
	useTiposCursada: vi.fn(),
	useEstadosAcademicos: vi.fn(),
}));

const useCursadasMock = vi.mocked(useCursadas);
const useCarrerasMock = vi.mocked(useCarreras);
const useEstudianteDetalleMock = vi.mocked(useEstudianteDetalle);
const useEstadosCursadaMock = vi.mocked(useEstadosCursada);
const useTiposCursadaMock = vi.mocked(useTiposCursada);
const useEstadosAcademicosMock = vi.mocked(useEstadosAcademicos);

function makeRow(overrides: Partial<CursadaRow> = {}): CursadaRow {
	return {
		id: "cu1",
		alumno: { id: "a1", nombre: "Ana", apellido: "García", legajo: "123" },
		materia: { id: "m1", codigo: "IP", nombre: "Introducción" },
		carrera: { id: "c1", codigo: "TPI", nombre: "Tecnicatura" },
		anio: 2024,
		cuatrimestre: "1C",
		comision: "A",
		tipo_cursada: "regular",
		estado_cursada: "aprobado",
		nota: "8",
		...overrides,
	};
}

const emptyPage = {
	items: [],
	total: 0,
	loading: false,
	error: undefined,
	refresh: vi.fn(),
};

beforeEach(() => {
	vi.clearAllMocks();
	useCarrerasMock.mockReturnValue(emptyPage);
	useCursadasMock.mockReturnValue({
		...emptyPage,
		items: [makeRow()],
		total: 1,
	});
	useEstadosCursadaMock.mockReturnValue({
		estados: [
			{ key: "inscripto", label: "Inscripto" },
			{ key: "regular", label: "Regular" },
			{ key: "aprobado", label: "Aprobado" },
		],
		loading: false,
		error: undefined,
	});
	useTiposCursadaMock.mockReturnValue({
		tipos: [{ key: "regular", label: "Cursada Regular" }],
		loading: false,
		error: undefined,
	});
	useEstadosAcademicosMock.mockReturnValue({
		estados: [{ key: "alumno_regular", label: "Alumno Regular" }],
		loading: false,
		error: undefined,
	});
});

describe("CursadasList", () => {
	it("el tab Historial presetea todos los estados menos inscripto", () => {
		render(<CursadasList />);

		expect(useCursadasMock).toHaveBeenLastCalledWith(
			expect.objectContaining({
				estado_cursada: ["regular", "aprobado"],
			}),
		);
	});

	it("el tab Inscripciones presetea inscripto", () => {
		render(<CursadasList />);

		fireEvent.click(screen.getByRole("button", { name: "Inscripciones" }));

		expect(useCursadasMock).toHaveBeenLastCalledWith(
			expect.objectContaining({ estado_cursada: ["inscripto"] }),
		);
	});

	it("espera el lookup de estados antes de pedir el Historial", () => {
		useEstadosCursadaMock.mockReturnValue({
			estados: [],
			loading: true,
			error: undefined,
		});

		render(<CursadasList />);

		expect(useCursadasMock).toHaveBeenLastCalledWith(
			expect.objectContaining({ ready: false }),
		);
	});

	it("Igual pide si el lookup de estados falla", () => {
		useEstadosCursadaMock.mockReturnValue({
			estados: [],
			loading: false,
			error: "no autorizado",
		});

		render(<CursadasList />);

		expect(useCursadasMock).toHaveBeenLastCalledWith(
			expect.objectContaining({ ready: true }),
		);
	});

	it("el select de estado pisa el preset del tab", () => {
		render(<CursadasList />);

		fireEvent.change(screen.getByLabelText("Filtrar por estado"), {
			target: { value: "regular" },
		});

		expect(useCursadasMock).toHaveBeenLastCalledWith(
			expect.objectContaining({ estado_cursada: ["regular"] }),
		);
	});

	it("muestra la fila con las referencias resueltas", () => {
		render(<CursadasList />);

		const table = within(screen.getByRole("table"));
		expect(table.getByText("García, Ana")).toBeInTheDocument();
		expect(table.getByText("IP — Introducción")).toBeInTheDocument();
		expect(table.getByText("TPI")).toBeInTheDocument();
		expect(table.getByText("Cursada Regular")).toBeInTheDocument();
		expect(table.getByText("Aprobado")).toBeInTheDocument();
	});

	it("abre el detalle del estudiante con carreras e historial", async () => {
		useEstudianteDetalleMock.mockReturnValue({
			loading: false,
			error: undefined,
			detail: {
				id: "a1",
				nombre: "Ana",
				apellido: "García",
				dni: "12345678",
				legajo: "123",
				carreras: [
					{
						plan_id: "p1",
						plan_nombre: "Plan 2015",
						anio: 2015,
						vigente: true,
						carrera_id: "c1",
						carrera_nombre: "Tecnicatura",
						estado_academico: "alumno_regular",
						fecha_ingreso: null,
					},
				],
				cursadas: [makeRow()],
			},
		});

		render(<CursadasList />);
		fireEvent.click(screen.getByRole("button", { name: "García, Ana" }));

		await waitFor(() => expect(screen.getByRole("dialog")).toBeInTheDocument());
		expect(useEstudianteDetalleMock).toHaveBeenCalledWith("a1");
		expect(screen.getByText(/Plan 2015/)).toBeInTheDocument();
		expect(screen.getByText(/Alumno Regular/)).toBeInTheDocument();
		expect(screen.getByText("Historial de cursadas (1)")).toBeInTheDocument();
	});

	it("muestra el error del detalle sin romper la tabla", async () => {
		useEstudianteDetalleMock.mockReturnValue({
			detail: null,
			loading: false,
			error: "estudiante no encontrado",
		});

		render(<CursadasList />);
		fireEvent.click(screen.getByRole("button", { name: "García, Ana" }));

		await waitFor(() =>
			expect(screen.getByRole("alert")).toHaveTextContent(
				"estudiante no encontrado",
			),
		);
		expect(screen.getByRole("table")).toBeInTheDocument();
	});
});
