import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { InviteUserForm } from "@/components/admin/InviteUserForm";
import { useInviteUser } from "@/hooks/admin";
import type { LookupOption } from "@/lib/api/lookups";

vi.mock("@/hooks/admin", () => ({ useInviteUser: vi.fn() }));

const useInviteUserMock = vi.mocked(useInviteUser);

const ROLES: LookupOption[] = [
	{ key: "admin", label: "Administrador" },
	{ key: "director", label: "Director de Carrera" },
	{ key: "docente", label: "Docente" },
];

function mockInviteUser(overrides: Partial<ReturnType<typeof useInviteUser>>) {
	useInviteUserMock.mockReturnValue({
		email: "",
		setEmail: vi.fn(),
		role: "",
		setRole: vi.fn(),
		pending: false,
		error: undefined,
		success: undefined,
		handleSubmit: vi.fn(),
		...overrides,
	});
}

describe("InviteUserForm", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("renderiza el select con los roles del lookup y sin default", () => {
		mockInviteUser({});

		render(<InviteUserForm roles={ROLES} />);

		const select = screen.getByRole("combobox");
		expect(select).toHaveValue("");
		expect(
			screen.getByRole("option", { name: "Seleccioná un rol" }),
		).toBeInTheDocument();
		for (const role of ROLES) {
			expect(screen.getByRole("option", { name: role.label })).toHaveValue(
				role.key,
			);
		}
	});

	it("envía el form con el email y el rol elegidos", () => {
		const setEmail = vi.fn();
		const setRole = vi.fn();
		mockInviteUser({ setEmail, setRole });

		render(<InviteUserForm roles={ROLES} />);

		fireEvent.change(screen.getByLabelText("Email"), {
			target: { value: "nuevo@unq.edu.ar" },
		});
		fireEvent.change(screen.getByLabelText("Rol"), {
			target: { value: "docente" },
		});

		expect(setEmail).toHaveBeenCalledWith("nuevo@unq.edu.ar");
		expect(setRole).toHaveBeenCalledWith("docente");
	});

	it("llama handleSubmit al enviar", () => {
		const handleSubmit = vi.fn();
		mockInviteUser({ handleSubmit });

		render(<InviteUserForm roles={ROLES} />);

		fireEvent.submit(screen.getByRole("button", { name: "Enviar invitación" }));

		expect(handleSubmit).toHaveBeenCalled();
	});

	it("muestra error y éxito", () => {
		mockInviteUser({ error: "dominio inválido" });

		render(<InviteUserForm roles={ROLES} />);

		expect(screen.getByText("dominio inválido")).toBeInTheDocument();
	});

	it("muestra el mensaje de éxito", () => {
		mockInviteUser({ success: "Invitación enviada a nuevo@unq.edu.ar" });

		render(<InviteUserForm roles={ROLES} />);

		expect(
			screen.getByText("Invitación enviada a nuevo@unq.edu.ar"),
		).toBeInTheDocument();
	});

	it("deshabilita los controles mientras envía", () => {
		mockInviteUser({ pending: true });

		render(<InviteUserForm roles={ROLES} />);

		expect(screen.getByLabelText("Email")).toBeDisabled();
		expect(screen.getByLabelText("Rol")).toBeDisabled();
		expect(screen.getByRole("button", { name: "Invitando..." })).toBeDisabled();
	});
});
