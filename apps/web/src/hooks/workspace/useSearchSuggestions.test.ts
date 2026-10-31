import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useSearchSuggestions } from "@/hooks/workspace/useSearchSuggestions";
import type { SearchHit } from "@/lib/api/search";

const HIT: SearchHit = { id: "a1", label: "Núñez, Lucía", term: "Núñez Lucía" };

describe("useSearchSuggestions", () => {
	it("pide las sugerencias del término debounced", async () => {
		const search = vi.fn().mockResolvedValue({ ok: true, data: [HIT] });

		const { result } = renderHook(() => useSearchSuggestions(search, "luci"));

		await waitFor(() => expect(result.current).toEqual([HIT]));
		expect(search).toHaveBeenCalledWith("luci");
	});

	it("no pide nada con menos de dos caracteres", async () => {
		const search = vi.fn().mockResolvedValue({ ok: true, data: [HIT] });

		const { result } = renderHook(() => useSearchSuggestions(search, "  "));

		expect(result.current).toEqual([]);
		expect(search).not.toHaveBeenCalled();

		const oneChar = renderHook(() => useSearchSuggestions(search, "a"));
		expect(oneChar.result.current).toEqual([]);
		expect(search).not.toHaveBeenCalled();
	});

	it("un error del backend deja la lista vacía", async () => {
		const search = vi
			.fn()
			.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useSearchSuggestions(search, "ana"));

		await waitFor(() => expect(search).toHaveBeenCalled());
		expect(result.current).toEqual([]);
	});
});
