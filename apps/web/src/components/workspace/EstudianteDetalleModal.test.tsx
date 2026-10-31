import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { EstudianteDetalleModal } from "@/components/workspace/EstudianteDetalleModal";
import { useEstudianteDetalle } from "@/hooks/workspace";

vi.mock("@/hooks/workspace", () => ({ useEstudianteDetalle: vi.fn() }));

const useEstudianteDetalleMock = vi.mocked(useEstudianteDetalle);

const LABELS = {
	estadoAcademicoLabels: { alumno_regular: "Alumno Regular" },
	estadoCursadaLabels: { aprobado: "Aprobado" },
	tipoCursadaLabels: { regular: "Cursada Regular" },
	onClose: () => {},
};

function renderModal() {
	render(<EstudianteDetalleModal alumnoId="a1" {...LABELS} />);
}

beforeEach(() => {
	vi.clearAllMocks();
});

describe("EstudianteDetalleModal", () => {
	it("mientras carga no tiene detalle y muestra el título genérico", () => {
		useEstudianteDetalleMock.mockReturnValue({
			detail: null,
			loading: true,
			error: undefined,
		});

		renderModal();

		expect(
			screen.getByRole("dialog", { name: "Detalle del estudiante" }),
		).toBeInTheDocument();
		expect(screen.getByText("Cargando…")).toBeInTheDocument();
	});

	it("muestra el error sin detalle", () => {
		useEstudianteDetalleMock.mockReturnValue({
			detail: null,
			loading: false,
			error: "estudiante no encontrado",
		});

		renderModal();

		expect(screen.getByRole("alert")).toHaveTextContent(
			"estudiante no encontrado",
		);
	});

	it("resuelve legajo, labels de lookup y nota; cae al valor crudo sin lookup", () => {
		useEstudianteDetalleMock.mockReturnValue({
			detail: {
				id: "a1",
				nombre: "Lucía",
				apellido: "Núñez",
				dni: "30111222",
				legajo: "12007",
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
					{
						plan_id: "p2",
						plan_nombre: "Plan 2019",
						anio: 2019,
						vigente: true,
						carrera_id: "c2",
						carrera_nombre: "Licenciatura",
						estado_academico: "egresado",
						fecha_ingreso: null,
					},
				],
				cursadas: [
					{
						id: "cu1",
						alumno: {
							id: "a1",
							nombre: "Lucía",
							apellido: "Núñez",
							legajo: "12007",
						},
						materia: { id: "m1", codigo: "AM", nombre: "Análisis Matemático" },
						carrera: { id: "c1", codigo: "TPI", nombre: "Tecnicatura" },
						anio: 2024,
						cuatrimestre: "1C",
						comision: "A",
						tipo_cursada: "regular",
						estado_cursada: "aprobado",
						nota: "8",
					},
					{
						id: "cu2",
						alumno: {
							id: "a1",
							nombre: "Lucía",
							apellido: "Núñez",
							legajo: "12007",
						},
						materia: { id: "m2", codigo: "IP", nombre: "Introducción" },
						carrera: { id: "c1", codigo: "TPI", nombre: "Tecnicatura" },
						anio: 2024,
						cuatrimestre: "1C",
						comision: null,
						tipo_cursada: "libre",
						estado_cursada: "en_curso",
						nota: null,
					},
				],
			},
			loading: false,
			error: undefined,
		});

		renderModal();

		expect(screen.getByText("Legajo 12007 · DNI 30111222")).toBeInTheDocument();
		expect(screen.getByRole("dialog")).toHaveTextContent("Alumno Regular");
		expect(screen.getByRole("dialog")).toHaveTextContent("egresado");
		expect(screen.getByText("Cursada Regular")).toBeInTheDocument();
		expect(screen.getByText("Aprobado")).toBeInTheDocument();
		expect(screen.getByText("libre")).toBeInTheDocument();
		expect(screen.getByText("en_curso")).toBeInTheDocument();
		expect(screen.getByText("—")).toBeInTheDocument();
	});
});
