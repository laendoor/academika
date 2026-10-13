import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET } from "./route";

function makeRequest(token?: string, qs = ""): NextRequest {
	return new NextRequest(`http://localhost:3000/api/planes${qs}`, {
		method: "GET",
		headers: {
			...(token && { cookie: `access_token=${token}` }),
		},
	});
}

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe("GET /api/planes", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("reenvía paginación y filtro por carrera al API", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(200, { total: 1, items: [] }),
		);

		const res = await GET(
			makeRequest("token-dir", "?skip=0&limit=20&carrera_id=c1"),
		);

		expect(res.status).toBe(200);
		expect(await res.json()).toEqual({ total: 1, items: [] });
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/planes?skip=0&limit=20&carrera_id=c1"),
			expect.objectContaining({
				headers: expect.objectContaining({
					Authorization: "Bearer token-dir",
				}),
			}),
		);
	});

	it("propaga el status del API ante error", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(403, { detail: "Sin permiso" }),
		);

		const res = await GET(makeRequest("token-doc"));

		expect(res.status).toBe(403);
		expect(await res.json()).toEqual({ error: "Sin permiso" });
	});

	it("mapea el detail del API ante error 500", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(500, { detail: "DB caída" }),
		);

		const res = await GET(makeRequest("token-dir"));

		expect(res.status).toBe(500);
		expect(await res.json()).toEqual({ error: "DB caída" });
	});

	it("mapea el 422 con lista de Pydantic al error genérico", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(422, { detail: [{ msg: "Input inválido" }] }),
		);

		const res = await GET(makeRequest("token-dir", "?carrera_id=no-uuid"));

		expect(res.status).toBe(422);
		expect(await res.json()).toEqual({
			error: "Error inesperado. Intentá de nuevo más tarde.",
		});
	});

	it("omite el query cuando no hay filtros", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(200, { total: 0, items: [] }),
		);

		const res = await GET(makeRequest("token-dir"));

		expect(res.status).toBe(200);
		const url = vi.mocked(fetch).mock.calls[0][0] as string;
		expect(url).toContain("/api/v1/planes");
		expect(url).not.toContain("?");
	});

	it("corta con 401 sin token de sesión", async () => {
		const res = await GET(makeRequest());

		expect(res.status).toBe(401);
		expect(await res.json()).toEqual({ error: "No autorizado" });
		expect(fetch).not.toHaveBeenCalled();
	});
});
