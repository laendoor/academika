import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useCursadas } from "@/hooks/workspace/useCursadas";
import * as workspace from "@/lib/api/workspace";

vi.mock("@/lib/api/workspace", () => ({ getCursadas: vi.fn() }));

const getCursadas = vi.mocked(workspace.getCursadas);

beforeEach(() => {
	vi.clearAllMocks();
	getCursadas.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });
});

describe("useCursadas", () => {
	it("manda los estados repetidos y omite los filtros vacíos", async () => {
		const { result } = renderHook(() =>
			useCursadas({
				carrera_id: "c1",
				estado_cursada: ["regular", "aprobado"],
			}),
		);

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(getCursadas).toHaveBeenCalledWith(
			0,
			20,
			expect.objectContaining({
				carrera_id: "c1",
				estado_cursada: ["regular", "aprobado"],
				alumno: undefined,
			}),
		);
	});

	it("no pide nada mientras ready es false", async () => {
		const { result } = renderHook(() => useCursadas({ ready: false }));

		await waitFor(() => expect(result.current.loading).toBe(true));
		expect(getCursadas).not.toHaveBeenCalled();
		expect(result.current.items).toEqual([]);
	});
});
