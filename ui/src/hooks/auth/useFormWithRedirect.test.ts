import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useFormWithRedirect } from "@/hooks/auth/useFormWithRedirect";

const { routerMock } = vi.hoisted(() => ({
	routerMock: { push: vi.fn() },
}));

vi.mock("next/navigation", () => ({ useRouter: () => routerMock }));

describe("useFormWithRedirect", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("redirige al éxito", async () => {
		const action = vi.fn().mockResolvedValue({ ok: true, data: {} });

		const { result } = renderHook(() => useFormWithRedirect(action, "/"));

		await act(async () => {
			await result.current.handleAction(new FormData());
		});

		expect(routerMock.push).toHaveBeenCalledWith("/");
		expect(result.current.error).toBeUndefined();
		expect(result.current.pending).toBe(false);
	});

	it("setea error sin redirigir al fallar", async () => {
		const action = vi
			.fn()
			.mockResolvedValue({ ok: false, error: "credenciales inválidas" });

		const { result } = renderHook(() => useFormWithRedirect(action, "/"));

		await act(async () => {
			await result.current.handleAction(new FormData());
		});

		expect(result.current.error).toBe("credenciales inválidas");
		expect(routerMock.push).not.toHaveBeenCalled();
	});
});
