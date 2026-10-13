import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PlanDetailModal } from "@/components/workspace/PlanDetailModal";
import type { PlanDetail } from "@/lib/api/workspace";

function makeDetail(): PlanDetail {
	return {
		id: "p1",
		carrera_id: "c1",
		carrera_nombre: "TPI",
		nombre: "Plan 2015",
		nivel: "grado",
		anio: 2015,
		vigente: true,
		materias: [
			{
				id: "m1",
				codigo: "MAT1",
				sigla: "M1",
				nombre: "Matemática I",
				creditos: 6,
				nucleo: "basico",
				horas_semanales: 4,
				carga_horaria_total: 64,
			},
		],
	};
}

const LABELS = {
	nivelLabels: { grado: "Grado" },
	nucleoLabels: { basico: "Básico" },
};

describe("PlanDetailModal", () => {
	it("muestra cabecera y materias con labels de lookups", () => {
		render(
			<PlanDetailModal
				detail={makeDetail()}
				loading={false}
				{...LABELS}
				onClose={() => {}}
			/>,
		);

		expect(screen.getByText("Plan 2015")).toBeInTheDocument();
		expect(
			screen.getByText(/TPI · Plan 2015 · Grado · vigente/),
		).toBeInTheDocument();
		expect(screen.getByText("Matemática I")).toBeInTheDocument();
		expect(screen.getByText("Básico")).toBeInTheDocument();
	});

	it("muestra estado de carga y de error", () => {
		const { rerender } = render(
			<PlanDetailModal
				detail={null}
				loading={true}
				{...LABELS}
				onClose={() => {}}
			/>,
		);
		expect(screen.getByText("Cargando…")).toBeInTheDocument();

		rerender(
			<PlanDetailModal
				detail={null}
				loading={false}
				error="Falló la carga"
				{...LABELS}
				onClose={() => {}}
			/>,
		);
		expect(screen.getByRole("alert")).toHaveTextContent("Falló la carga");
	});

	it("cierra con Escape y con click en el backdrop, no con otras teclas", () => {
		const onClose = vi.fn();
		render(
			<PlanDetailModal
				detail={makeDetail()}
				loading={false}
				{...LABELS}
				onClose={onClose}
			/>,
		);

		fireEvent.keyDown(document, { key: "Enter" });
		expect(onClose).not.toHaveBeenCalled();

		fireEvent.keyDown(document, { key: "Escape" });
		expect(onClose).toHaveBeenCalledTimes(1);

		fireEvent.click(screen.getByTestId("plan-modal-backdrop"));
		expect(onClose).toHaveBeenCalledTimes(2);

		fireEvent.click(screen.getByRole("dialog"));
		expect(onClose).toHaveBeenCalledTimes(2);
	});

	it("muestra materia rala con guiones y labels crudos sin lookup", () => {
		render(
			<PlanDetailModal
				detail={{
					...makeDetail(),
					vigente: false,
					materias: [
						{
							id: "m2",
							codigo: "OPT1",
							sigla: null,
							nombre: "Optativa I",
							creditos: null,
							nucleo: "basico",
							horas_semanales: null,
							carga_horaria_total: null,
						},
						{
							id: "m3",
							codigo: "OPT2",
							sigla: null,
							nombre: "Optativa II",
							creditos: null,
							nucleo: null,
							horas_semanales: null,
							carga_horaria_total: null,
						},
					],
				}}
				loading={false}
				nivelLabels={{}}
				nucleoLabels={{}}
				onClose={() => {}}
			/>,
		);

		expect(screen.getByText(/grado · no vigente/)).toBeInTheDocument();
		expect(screen.getByText("Optativa I")).toBeInTheDocument();
		expect(screen.getByText("basico")).toBeInTheDocument();
		expect(screen.getAllByText("—").length).toBeGreaterThan(0);
	});

	it("avisa cuando el plan no tiene materias", () => {
		render(
			<PlanDetailModal
				detail={{ ...makeDetail(), nivel: null, materias: [] }}
				loading={false}
				{...LABELS}
				onClose={() => {}}
			/>,
		);

		expect(
			screen.getByText("Este plan no tiene materias vinculadas."),
		).toBeInTheDocument();
	});
});
