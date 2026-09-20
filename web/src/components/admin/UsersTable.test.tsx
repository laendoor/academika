import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { UsersTable } from "@/components/admin/UsersTable";
import type { UserItem } from "@/lib/api/admin";

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

describe("UsersTable", () => {
	it("renderiza email, rol y estado", () => {
		render(
			<UsersTable users={[makeUser()]} updating={null} onUpdate={vi.fn()} />,
		);

		expect(screen.getByText("a@unq.edu.ar")).toBeInTheDocument();
		expect(screen.getByText("Director")).toBeInTheDocument();
		expect(screen.getByText("Activo")).toBeInTheDocument();
	});

	it("llama onUpdate al cambiar el rol", () => {
		const onUpdate = vi.fn();
		render(
			<UsersTable users={[makeUser()]} updating={null} onUpdate={onUpdate} />,
		);

		fireEvent.change(screen.getByRole("combobox"), {
			target: { value: "admin" },
		});

		expect(onUpdate).toHaveBeenCalledWith("u1", { role: "admin" });
	});

	it("llama onUpdate al alternar el estado", () => {
		const onUpdate = vi.fn();
		render(
			<UsersTable users={[makeUser()]} updating={null} onUpdate={onUpdate} />,
		);

		fireEvent.click(screen.getByRole("button", { name: "Activo" }));

		expect(onUpdate).toHaveBeenCalledWith("u1", { is_active: false });
	});

	it("deshabilita controles mientras actualiza ese usuario", () => {
		render(
			<UsersTable users={[makeUser()]} updating="u1" onUpdate={vi.fn()} />,
		);

		expect(screen.getByRole("combobox")).toBeDisabled();
		expect(screen.getByRole("button", { name: "Activo" })).toBeDisabled();
	});
});
