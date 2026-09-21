import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useUserRoles } from "@/hooks/lookups";
import * as lookups from "@/lib/api/lookups";

vi.mock("@/lib/api/lookups", () => ({
	getUserRoles: vi.fn(),
}));

const getUserRoles = vi.mocked(lookups.getUserRoles);

describe("useUserRoles", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga los roles del lookup", async () => {
		getUserRoles.mockResolvedValue({
			ok: true,
			data: [{ key: "docente", label: "Docente" }],
		});

		const { result } = renderHook(() => useUserRoles());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.roles).toEqual([
			{ key: "docente", label: "Docente" },
		]);
		expect(result.current.error).toBeUndefined();
	});

	it("expone el error si falla el fetch", async () => {
		getUserRoles.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useUserRoles());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("no autorizado");
		expect(result.current.roles).toEqual([]);
	});
});
