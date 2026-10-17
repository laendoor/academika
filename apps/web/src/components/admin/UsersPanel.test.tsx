import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { UsersPanel } from "@/components/admin/UsersPanel";
import { useAdminUsers, useInviteUser } from "@/hooks/admin";
import { useUserRoles } from "@/hooks/lookups";
import type { UserItem } from "@/lib/api/admin";

vi.mock("@/hooks/admin", () => ({
	useAdminUsers: vi.fn(),
	useInviteUser: vi.fn(),
}));
vi.mock("@/hooks/lookups", () => ({ useUserRoles: vi.fn() }));

const useAdminUsersMock = vi.mocked(useAdminUsers);
const useInviteUserMock = vi.mocked(useInviteUser);
const useUserRolesMock = vi.mocked(useUserRoles);

const ROLES = [
	{ key: "admin", label: "Administrador" },
	{ key: "director", label: "Director de Carrera" },
	{ key: "docente", label: "Docente" },
];

function makeUser(): UserItem {
	return {
		id: "u1",
		email: "a@unq.edu.ar",
		role: "director",
		is_active: true,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
	};
}

function mockPanel({
	loading = false,
	error,
	users = [makeUser()],
}: {
	loading?: boolean;
	error?: string;
	users?: UserItem[];
}) {
	useAdminUsersMock.mockReturnValue({
		users,
		loading,
		error,
		updating: null,
		deleting: null,
		handleUpdate: vi.fn(),
		handleDelete: vi.fn(),
	});
	useUserRolesMock.mockReturnValue({
		roles: ROLES,
		loading: false,
		error: undefined,
	});
	useInviteUserMock.mockReturnValue({
		email: "",
		setEmail: vi.fn(),
		role: "",
		setRole: vi.fn(),
		pending: false,
		error: undefined,
		success: undefined,
		handleSubmit: vi.fn(),
	});
}

describe("UsersPanel", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("muestra loading", () => {
		mockPanel({ loading: true, users: [] });
		render(<UsersPanel />);
		expect(screen.getByText("Cargando...")).toBeInTheDocument();
	});

	it("muestra loading mientras cargan los roles", () => {
		mockPanel({});
		useUserRolesMock.mockReturnValue({
			roles: [],
			loading: true,
			error: undefined,
		});
		render(<UsersPanel />);
		expect(screen.getByText("Cargando...")).toBeInTheDocument();
	});

	it("muestra error", () => {
		mockPanel({ error: "no autorizado", users: [] });
		render(<UsersPanel />);
		expect(screen.getByText("no autorizado")).toBeInTheDocument();
	});

	it("muestra la tabla con usuarios y los roles del lookup", () => {
		mockPanel({});
		render(<UsersPanel />);
		expect(screen.getByText("a@unq.edu.ar")).toBeInTheDocument();
		expect(
			screen.getByRole("option", { name: "Director de Carrera" }),
		).toBeInTheDocument();
	});

	it("oculta el form de invitación hasta que se abre", () => {
		mockPanel({});
		render(<UsersPanel />);

		expect(screen.queryByLabelText("Email")).not.toBeInTheDocument();

		fireEvent.click(screen.getByRole("button", { name: "Invitar" }));

		expect(screen.getByLabelText("Email")).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: "Enviar invitación" }),
		).toBeInTheDocument();
	});

	it("vuelve a ocultar el form al togglear", () => {
		mockPanel({});
		render(<UsersPanel />);

		const toggle = screen.getByRole("button", { name: "Invitar" });
		fireEvent.click(toggle);
		fireEvent.click(toggle);

		expect(screen.queryByLabelText("Email")).not.toBeInTheDocument();
	});
});
