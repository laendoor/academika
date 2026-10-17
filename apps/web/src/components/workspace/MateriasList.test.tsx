import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MateriasList } from "@/components/workspace/MateriasList";
import { useMaterias } from "@/hooks/workspace";
import type { MateriaRow } from "@/lib/api/workspace";

vi.mock("@/hooks/workspace", () => ({ useMaterias: vi.fn() }));

const useMateriasMock = vi.mocked(useMaterias);

function makeMateria(id: string): MateriaRow {
	return {
		id,
		nombre: `Materia ${id}`,
		codigo: `C${id}`,
		sigla: null,
		creditos: 4,
		plan_vigente: null,
		planes: [],
	};
}

describe("MateriasList", () => {
	it("renderiza materias", () => {
		useMateriasMock.mockReturnValue({
			items: [makeMateria("m1")],
			total: 1,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<MateriasList />);
		expect(screen.getByText("Materia m1")).toBeInTheDocument();
	});

	it("muestra mensaje vacío", () => {
		useMateriasMock.mockReturnValue({
			items: [],
			total: 0,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<MateriasList />);
		expect(screen.getByText("Sin materias.")).toBeInTheDocument();
	});

	it("muestra paginación cuando hay más de una página", () => {
		useMateriasMock.mockReturnValue({
			items: [],
			total: 25,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<MateriasList />);
		expect(screen.getByRole("button", { name: "Siguiente" })).toBeEnabled();
		expect(screen.getByRole("button", { name: "Anterior" })).toBeDisabled();
	});
});
