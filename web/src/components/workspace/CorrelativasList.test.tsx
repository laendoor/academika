import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CorrelativasList } from "@/components/workspace/CorrelativasList";
import { useCorrelativas, useMaterias } from "@/hooks/workspace";
import type { CorrelativaRow } from "@/lib/api/workspace";

vi.mock("@/hooks/workspace", () => ({
	useCorrelativas: vi.fn(),
	useMaterias: vi.fn(),
}));

const useCorrelativasMock = vi.mocked(useCorrelativas);
const useMateriasMock = vi.mocked(useMaterias);

function makeCorrelativa(suffix: string, obligatoria: boolean): CorrelativaRow {
	return {
		materia: {
			id: `m-${suffix}`,
			codigo: `C${suffix}`,
			nombre: `Materia ${suffix}`,
		},
		requisito: {
			id: `r-${suffix}`,
			codigo: `R${suffix}`,
			nombre: `Requisito ${suffix}`,
		},
		es_obligatoria: obligatoria,
	};
}

function mockHooks(items: CorrelativaRow[], total: number) {
	useCorrelativasMock.mockReturnValue({
		items,
		total,
		loading: false,
		error: undefined,
		refresh: vi.fn(),
	});
	useMateriasMock.mockReturnValue({
		items: [],
		total: 0,
		loading: false,
		error: undefined,
		refresh: vi.fn(),
	});
}

describe("CorrelativasList", () => {
	it("renderiza correlativas con su tipo", () => {
		mockHooks([makeCorrelativa("a", true), makeCorrelativa("b", false)], 2);
		render(<CorrelativasList />);
		expect(screen.getByText("Ca — Materia a")).toBeInTheDocument();
		expect(screen.getByText("Ra — Requisito a")).toBeInTheDocument();
		expect(screen.getByText("Obligatoria")).toBeInTheDocument();
		expect(screen.getByText("Recomendada")).toBeInTheDocument();
	});

	it("muestra mensaje vacío", () => {
		mockHooks([], 0);
		render(<CorrelativasList />);
		expect(screen.getByText("Sin correlativas.")).toBeInTheDocument();
	});

	it("muestra paginación cuando hay más de una página", () => {
		mockHooks([], 25);
		render(<CorrelativasList />);
		expect(screen.getByRole("button", { name: "Siguiente" })).toBeEnabled();
		expect(screen.getByRole("button", { name: "Anterior" })).toBeDisabled();
	});
});
