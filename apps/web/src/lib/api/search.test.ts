import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { searchAlumnos, searchMaterias } from "@/lib/api/search";

function jsonResponse(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe("lib/api/search", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("searchAlumnos pega en el BFF de alumnos con q urlencodeado", async () => {
		const hits = [{ id: "a1", label: "Núñez, Lucía", term: "Núñez Lucía" }];
		vi.mocked(fetch).mockResolvedValue(jsonResponse(hits));

		const result = await searchAlumnos("Núñez");

		expect(result).toEqual({ ok: true, data: hits });
		expect(fetch).toHaveBeenCalledWith(
			"/api/alumnos/search?q=N%C3%BA%C3%B1ez",
			expect.anything(),
		);
	});

	it("searchMaterias pega en el BFF de materias", async () => {
		vi.mocked(fetch).mockResolvedValue(jsonResponse([]));

		const result = await searchMaterias("anali");

		expect(result).toEqual({ ok: true, data: [] });
		expect(fetch).toHaveBeenCalledWith(
			"/api/materias/search?q=anali",
			expect.anything(),
		);
	});

	it("traduce el error del BFF al ApiResult", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse({ error: "No autorizado" }, 401),
		);

		const result = await searchMaterias("anali");

		expect(result).toEqual({ ok: false, error: "No autorizado" });
	});
});
