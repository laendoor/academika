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

	it("cierra con Escape y con click en el backdrop", () => {
		const onClose = vi.fn();
		render(
			<PlanDetailModal
				detail={makeDetail()}
				loading={false}
				{...LABELS}
				onClose={onClose}
			/>,
		);

		fireEvent.keyDown(document, { key: "Escape" });
		expect(onClose).toHaveBeenCalledTimes(1);

		fireEvent.click(screen.getByTestId("plan-modal-backdrop"));
		expect(onClose).toHaveBeenCalledTimes(2);
	});
});
