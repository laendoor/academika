import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useInviteUser } from "@/hooks/admin/useInviteUser";
import * as admin from "@/lib/api/admin";
import type { ApiResult, OkResponse } from "@/lib/api/client";

vi.mock("@/lib/api/admin", () => ({
	inviteUser: vi.fn(),
}));

const inviteUser = vi.mocked(admin.inviteUser);

describe("useInviteUser", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("envía la invitación, limpia el form y muestra el éxito", async () => {
		inviteUser.mockResolvedValue({ ok: true, data: { ok: true } });

		const { result } = renderHook(() => useInviteUser());

		act(() => {
			result.current.setEmail("nuevo@unq.edu.ar");
			result.current.setRole("docente");
		});
		await act(() => result.current.handleSubmit());

		expect(inviteUser).toHaveBeenCalledWith("nuevo@unq.edu.ar", "docente");
		expect(result.current.success).toBe(
			"Invitación enviada a nuevo@unq.edu.ar",
		);
		expect(result.current.email).toBe("");
		expect(result.current.role).toBe("");
		expect(result.current.error).toBeUndefined();
	});

	it("muestra el error y conserva los valores si falla", async () => {
		inviteUser.mockResolvedValue({
			ok: false,
			error: "Ya existe un usuario activo con email 'nuevo@unq.edu.ar'",
		});

		const { result } = renderHook(() => useInviteUser());

		act(() => {
			result.current.setEmail("nuevo@unq.edu.ar");
			result.current.setRole("docente");
		});
		await act(() => result.current.handleSubmit());

		expect(result.current.error).toBe(
			"Ya existe un usuario activo con email 'nuevo@unq.edu.ar'",
		);
		expect(result.current.success).toBeUndefined();
		expect(result.current.email).toBe("nuevo@unq.edu.ar");
		expect(result.current.role).toBe("docente");
	});

	it("marca pending mientras espera la respuesta", async () => {
		let resolveInvite: (value: ApiResult<OkResponse>) => void;
		inviteUser.mockReturnValue(
			new Promise((resolve) => {
				resolveInvite = resolve;
			}),
		);

		const { result } = renderHook(() => useInviteUser());

		act(() => {
			result.current.setEmail("nuevo@unq.edu.ar");
			result.current.setRole("docente");
		});
		act(() => {
			result.current.handleSubmit();
		});

		expect(result.current.pending).toBe(true);

		await act(async () => {
			resolveInvite({ ok: true, data: { ok: true } });
		});

		await waitFor(() => expect(result.current.pending).toBe(false));
	});
});
