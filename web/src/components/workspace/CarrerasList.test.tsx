import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CarrerasList } from "@/components/workspace/CarrerasList";
import { useCarreras } from "@/hooks/workspace";
import type { CarreraOption } from "@/lib/api/workspace";

vi.mock("@/hooks/workspace", () => ({ useCarreras: vi.fn() }));

const useCarrerasMock = vi.mocked(useCarreras);

function makeCarrera(id: string): CarreraOption {
	return { id, nombre: `Carrera ${id}`, codigo: `C${id}` };
}

describe("CarrerasList", () => {
	it("renderiza carreras", () => {
		useCarrerasMock.mockReturnValue({
			items: [makeCarrera("c1")],
			total: 1,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<CarrerasList />);
		expect(screen.getByText("Carrera c1")).toBeInTheDocument();
	});

	it("muestra mensaje vacío", () => {
		useCarrerasMock.mockReturnValue({
			items: [],
			total: 0,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<CarrerasList />);
		expect(screen.getByText("Sin carreras.")).toBeInTheDocument();
	});

	it("muestra paginación cuando hay más de una página", () => {
		useCarrerasMock.mockReturnValue({
			items: [],
			total: 25,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
		});
		render(<CarrerasList />);
		expect(screen.getByRole("button", { name: "Siguiente" })).toBeEnabled();
		expect(screen.getByRole("button", { name: "Anterior" })).toBeDisabled();
	});
});
