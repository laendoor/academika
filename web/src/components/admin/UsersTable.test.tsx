import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { UsersTable } from "@/components/admin/UsersTable";
import type { UserItem, UserUpdate } from "@/lib/api/admin";
import type { LookupOption } from "@/lib/api/lookups";

const ROLES: LookupOption[] = [
	{ key: "admin", label: "Administrador" },
	{ key: "director", label: "Director de Carrera" },
	{ key: "docente", label: "Docente" },
];

function makeUser(overrides: Partial<UserItem> = {}): UserItem {
	return {
		id: "u1",
		email: "a@unq.edu.ar",
		role: "director",
		is_active: true,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
		...overrides,
	};
}

function renderTable({
	users = [makeUser()],
	updating = null,
	deleting = null,
	onUpdate = vi.fn(),
	onDelete = vi.fn(),
}: {
	users?: UserItem[];
	updating?: string | null;
	deleting?: string | null;
	onUpdate?: (id: string, data: UserUpdate) => void;
	onDelete?: (id: string) => void;
} = {}) {
	render(
		<UsersTable
			users={users}
			roles={ROLES}
			updating={updating}
			deleting={deleting}
			onUpdate={onUpdate}
			onDelete={onDelete}
		/>,
	);
}

describe("UsersTable", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("renderiza email, rol y estado", () => {
		renderTable();

		expect(screen.getByText("a@unq.edu.ar")).toBeInTheDocument();
		expect(screen.getByText("Director de Carrera")).toBeInTheDocument();
		expect(screen.getByText("Activo")).toBeInTheDocument();
	});

	it("llama onUpdate al cambiar el rol", () => {
		const onUpdate = vi.fn();
		renderTable({ onUpdate });

		fireEvent.change(screen.getByRole("combobox"), {
			target: { value: "admin" },
		});

		expect(onUpdate).toHaveBeenCalledWith("u1", { role: "admin" });
	});

	it("llama onUpdate al alternar el estado", () => {
		const onUpdate = vi.fn();
		renderTable({ onUpdate });

		fireEvent.click(screen.getByRole("button", { name: "Activo" }));

		expect(onUpdate).toHaveBeenCalledWith("u1", { is_active: false });
	});

	it("deshabilita controles mientras actualiza ese usuario", () => {
		renderTable({ updating: "u1" });

		expect(screen.getByRole("combobox")).toBeDisabled();
		expect(screen.getByRole("button", { name: "Activo" })).toBeDisabled();
		expect(screen.getByRole("button", { name: "Eliminar" })).toBeDisabled();
	});

	it("llama onDelete al confirmar la eliminación", () => {
		const onDelete = vi.fn();
		const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(true);
		renderTable({ onDelete });

		fireEvent.click(screen.getByRole("button", { name: "Eliminar" }));

		expect(confirmSpy).toHaveBeenCalled();
		expect(onDelete).toHaveBeenCalledWith("u1");
	});

	it("no llama onDelete si se cancela la confirmación", () => {
		const onDelete = vi.fn();
		vi.spyOn(window, "confirm").mockReturnValue(false);
		renderTable({ onDelete });

		fireEvent.click(screen.getByRole("button", { name: "Eliminar" }));

		expect(onDelete).not.toHaveBeenCalled();
	});

	it("deshabilita el botón de eliminar mientras borra ese usuario", () => {
		renderTable({ deleting: "u1" });

		expect(screen.getByRole("button", { name: "Eliminar" })).toBeDisabled();
	});
});
