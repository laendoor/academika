import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAdminUsers } from "@/hooks/admin/useAdminUsers";
import * as admin from "@/lib/api/admin";

vi.mock("@/lib/api/admin", () => ({
	getUsers: vi.fn(),
	updateUser: vi.fn(),
}));

const getUsers = vi.mocked(admin.getUsers);
const updateUser = vi.mocked(admin.updateUser);

function makeUser(id: string): admin.UserItem {
	return {
		id,
		email: `${id}@unq.edu.ar`,
		role: "director",
		is_active: true,
		created_at: "2026-01-01T00:00:00Z",
		updated_at: "2026-01-01T00:00:00Z",
	};
}

describe("useAdminUsers", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga la lista de usuarios", async () => {
		getUsers.mockResolvedValue({
			ok: true,
			data: { total: 1, items: [makeUser("u1")] },
		});

		const { result } = renderHook(() => useAdminUsers());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.users).toHaveLength(1);
		expect(result.current.error).toBeUndefined();
	});

	it("setea error cuando la carga falla", async () => {
		getUsers.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useAdminUsers());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("no autorizado");
	});

	it("actualiza el usuario en la lista al editar", async () => {
		getUsers.mockResolvedValue({
			ok: true,
			data: { total: 1, items: [makeUser("u1")] },
		});
		const updated = { ...makeUser("u1"), role: "admin" as const };
		updateUser.mockResolvedValue({ ok: true, data: updated });

		const { result } = renderHook(() => useAdminUsers());
		await waitFor(() => expect(result.current.loading).toBe(false));

		await act(async () => {
			await result.current.handleUpdate("u1", { role: "admin" });
		});

		expect(updateUser).toHaveBeenCalledWith("u1", { role: "admin" });
		expect(result.current.users[0].role).toBe("admin");
	});
});
