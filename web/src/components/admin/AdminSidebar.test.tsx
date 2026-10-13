import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AdminSidebar } from "@/components/admin/AdminSidebar";

vi.mock("next/navigation", () => ({
	usePathname: () => "/admin/estudiantes",
}));

describe("AdminSidebar", () => {
	it("muestra las secciones y links de navegación", () => {
		render(<AdminSidebar />);

		expect(screen.getByText("Datos Académicos")).toBeInTheDocument();
		expect(screen.getByText("Sistema")).toBeInTheDocument();
		expect(screen.getByRole("link", { name: "Estudiantes" })).toHaveAttribute(
			"href",
			"/admin/estudiantes",
		);
		expect(screen.getByRole("link", { name: "Materias" })).toHaveAttribute(
			"href",
			"/admin/materias",
		);
		expect(screen.getByRole("link", { name: "Planes" })).toHaveAttribute(
			"href",
			"/admin/planes",
		);
		expect(screen.getByRole("link", { name: "Usuarios" })).toHaveAttribute(
			"href",
			"/admin/usuarios",
		);
		expect(
			screen.getByRole("link", { name: "Importar Datos" }),
		).toHaveAttribute("href", "/admin/importar");
		expect(
			screen.queryByRole("link", { name: "Ver Datos Importados" }),
		).not.toBeInTheDocument();
	});

	it("resalta el link activo según el pathname", () => {
		render(<AdminSidebar />);

		const active = screen.getByRole("link", { name: "Estudiantes" });
		expect(active.className).toContain("bg-zinc-100");
		const inactive = screen.getByRole("link", { name: "Materias" });
		expect(inactive.className).not.toContain("bg-zinc-100");
	});

	it("muestra la versión y el sha (dev en local)", () => {
		render(<AdminSidebar />);

		expect(screen.getByText("vdev · dev")).toBeInTheDocument();
	});
});
