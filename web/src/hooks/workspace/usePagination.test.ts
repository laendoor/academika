import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { usePagination } from "@/hooks/workspace/usePagination";

describe("usePagination", () => {
	it("carga items y total", async () => {
		const fetcher = vi.fn().mockResolvedValue({
			ok: true,
			data: { total: 2, items: [1, 2] },
		});

		const { result } = renderHook(() =>
			usePagination(fetcher, { skip: 0, limit: 20 }),
		);

		expect(result.current.loading).toBe(true);
		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.items).toEqual([1, 2]);
		expect(result.current.total).toBe(2);
		expect(fetcher).toHaveBeenCalledWith(0, 20);
	});

	it("setea error cuando el fetch falla", async () => {
		const fetcher = vi.fn().mockResolvedValue({ ok: false, error: "boom" });

		const { result } = renderHook(() =>
			usePagination(fetcher, { skip: 0, limit: 20 }),
		);

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("boom");
		expect(result.current.items).toEqual([]);
	});
});
