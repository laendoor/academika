import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useRegisterForm } from "@/hooks/auth/useRegisterForm";

const { routerMock } = vi.hoisted(() => ({
	routerMock: { push: vi.fn() },
}));
const { registerMock } = vi.hoisted(() => ({ registerMock: vi.fn() }));

vi.mock("next/navigation", () => ({ useRouter: () => routerMock }));
vi.mock("@/lib/api/auth", () => ({ register: registerMock }));

function makeForm(password: string, confirm: string): FormData {
	const fd = new FormData();
	fd.set("password", password);
	fd.set("confirm_password", confirm);
	return fd;
}

describe("useRegisterForm", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("rechaza contraseñas distintas sin llamar a register", async () => {
		const { result } = renderHook(() => useRegisterForm("tok"));

		await act(async () => {
			await result.current.handleAction(makeForm("a", "b"));
		});

		expect(result.current.error).toBe("Las contraseñas no coinciden.");
		expect(registerMock).not.toHaveBeenCalled();
	});

	it("registra y redirige al éxito", async () => {
		registerMock.mockResolvedValue({ ok: true, data: { ok: true } });

		const { result } = renderHook(() => useRegisterForm("tok"));

		await act(async () => {
			await result.current.handleAction(makeForm("a", "a"));
		});

		expect(registerMock).toHaveBeenCalledWith("tok", "a");
		expect(routerMock.push).toHaveBeenCalledWith("/login");
	});

	it("setea error cuando register falla", async () => {
		registerMock.mockResolvedValue({ ok: false, error: "token inválido" });

		const { result } = renderHook(() => useRegisterForm("tok"));

		await act(async () => {
			await result.current.handleAction(makeForm("a", "a"));
		});

		expect(result.current.error).toBe("token inválido");
		expect(routerMock.push).not.toHaveBeenCalled();
	});
});
