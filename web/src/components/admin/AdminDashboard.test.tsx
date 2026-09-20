import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AdminDashboard } from "@/components/admin/AdminDashboard";
import { useAdminStats } from "@/hooks/admin";

vi.mock("@/hooks/admin", () => ({ useAdminStats: vi.fn() }));

const useAdminStatsMock = vi.mocked(useAdminStats);

describe("AdminDashboard", () => {
	it("muestra totales de estudiantes y materias", () => {
		useAdminStatsMock.mockReturnValue({
			estudiantes: 120,
			materias: 45,
			status: "ok",
		});
		render(<AdminDashboard />);
		expect(screen.getByText("120")).toBeInTheDocument();
		expect(screen.getByText("45")).toBeInTheDocument();
	});

	it("muestra guion cuando no hay datos", () => {
		useAdminStatsMock.mockReturnValue({
			estudiantes: null,
			materias: null,
			status: "loading",
		});
		render(<AdminDashboard />);
		expect(screen.getAllByText("—").length).toBeGreaterThan(0);
	});

	it("muestra error cuando falla", () => {
		useAdminStatsMock.mockReturnValue({
			estudiantes: null,
			materias: null,
			status: "error",
		});
		render(<AdminDashboard />);
		expect(screen.getByText("Error al cargar datos.")).toBeInTheDocument();
	});
});
