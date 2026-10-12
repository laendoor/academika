import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAdminImport } from "@/hooks/admin/useAdminImport";
import { useSources } from "@/hooks/workspace";
import * as admin from "@/lib/api/admin";

const { state, useSourcesMock } = vi.hoisted(() => {
	const state = { wsEventCount: 0 };
	return {
		state,
		useSourcesMock: vi.fn(() => ({
			items: [],
			total: 0,
			loading: false,
			error: undefined,
			refresh: vi.fn(),
			get wsEventCount() {
				return state.wsEventCount;
			},
		})),
	};
});

vi.mock("@/hooks/workspace", () => ({
	useSources: useSourcesMock,
}));
vi.mock("@/lib/api/admin", () => ({ uploadGuaraniSheets: vi.fn() }));

const uploadGuaraniSheets = vi.mocked(admin.uploadGuaraniSheets);

describe("useAdminImport", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		state.wsEventCount = 0;
	});

	it("no sube archivos vacíos", () => {
		const { result } = renderHook(() => useAdminImport());

		act(() => {
			void result.current.handleUpload([]);
		});

		expect(uploadGuaraniSheets).not.toHaveBeenCalled();
	});

	it("sube archivos y queda en uploading al éxito", async () => {
		uploadGuaraniSheets.mockResolvedValue({
			ok: true,
			data: { status: "processing", count: 3 },
		});

		const { result } = renderHook(() => useAdminImport());
		const file = new File(["x"], "alumnos.csv");

		await act(async () => {
			await result.current.handleUpload([file]);
		});

		expect(uploadGuaraniSheets).toHaveBeenCalledWith([file]);
		expect(result.current.uploading).toBe(true);
	});

	it("frena el uploading si la subida falla", async () => {
		uploadGuaraniSheets.mockResolvedValue({ ok: false, error: "boom" });

		const { result } = renderHook(() => useAdminImport());

		await act(async () => {
			await result.current.handleUpload([new File(["x"], "alumnos.csv")]);
		});

		expect(result.current.uploading).toBe(false);
	});

	it("pide la página indicada con tamaño 20", () => {
		renderHook(() => useAdminImport(40));
		expect(useSourcesMock).toHaveBeenCalledWith({ skip: 40, limit: 20 });
	});

	it("frena el uploading cuando llegan los eventos WS esperados", async () => {
		uploadGuaraniSheets.mockResolvedValue({
			ok: true,
			data: { status: "processing", count: 3 },
		});

		const { result, rerender } = renderHook(() => useAdminImport());

		await act(async () => {
			await result.current.handleUpload([new File(["x"], "alumnos.csv")]);
		});
		expect(result.current.uploading).toBe(true);

		state.wsEventCount = 3;
		rerender();

		expect(result.current.uploading).toBe(false);
	});
});
