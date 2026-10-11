import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAdminSettings } from "@/hooks/admin/useAdminSettings";
import * as admin from "@/lib/api/admin";

vi.mock("@/lib/api/admin", () => ({
	getSettings: vi.fn(),
	updateSetting: vi.fn(),
}));

const getSettings = vi.mocked(admin.getSettings);
const updateSetting = vi.mocked(admin.updateSetting);

function makeSetting(
	key: string,
	value: unknown = ["@unq.edu.ar"],
): admin.SettingItem {
	return { key, value, description: `${key} desc` };
}

describe("useAdminSettings", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga la lista de settings", async () => {
		getSettings.mockResolvedValue({
			ok: true,
			data: [makeSetting("auth.allowed_domains")],
		});

		const { result } = renderHook(() => useAdminSettings());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.settings).toHaveLength(1);
		expect(result.current.error).toBeUndefined();
	});

	it("setea error cuando la carga falla", async () => {
		getSettings.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useAdminSettings());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("no autorizado");
	});

	it("actualiza el valor en la lista al guardar", async () => {
		getSettings.mockResolvedValue({
			ok: true,
			data: [makeSetting("auth.allowed_domains")],
		});
		updateSetting.mockResolvedValue({
			ok: true,
			data: makeSetting("auth.allowed_domains", []),
		});

		const { result } = renderHook(() => useAdminSettings());
		await waitFor(() => expect(result.current.loading).toBe(false));

		let ok = false;
		await act(async () => {
			ok = await result.current.handleUpdate("auth.allowed_domains", []);
		});

		expect(ok).toBe(true);
		expect(updateSetting).toHaveBeenCalledWith("auth.allowed_domains", []);
		expect(result.current.settings[0].value).toEqual([]);
	});

	it("setea error cuando falla el guardado", async () => {
		getSettings.mockResolvedValue({
			ok: true,
			data: [makeSetting("auth.allowed_domains")],
		});
		updateSetting.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useAdminSettings());
		await waitFor(() => expect(result.current.loading).toBe(false));

		let ok = true;
		await act(async () => {
			ok = await result.current.handleUpdate("auth.allowed_domains", []);
		});

		expect(ok).toBe(false);
		expect(result.current.error).toBe("no autorizado");
		expect(result.current.settings[0].value).toEqual(["@unq.edu.ar"]);
	});
});
