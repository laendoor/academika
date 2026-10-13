import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET } from "./route";

const CTX: { params: Promise<Record<string, string>> } = {
	params: Promise.resolve({ id: "p1" }),
};

function makeRequest(token?: string): NextRequest {
	return new NextRequest("http://localhost:3000/api/planes/p1", {
		method: "GET",
		...(token && { headers: { cookie: `access_token=${token}` } }),
	});
}

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe("GET /api/planes/[id]", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("devuelve el detalle del plan", async () => {
		const detail = { id: "p1", carrera_nombre: "TPI", materias: [] };
		vi.mocked(fetch).mockResolvedValue(jsonResponse(200, detail));

		const res = await GET(makeRequest("token-dir"), CTX);

		expect(res.status).toBe(200);
		expect(await res.json()).toEqual(detail);
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/planes/p1"),
			expect.objectContaining({
				headers: expect.objectContaining({
					Authorization: "Bearer token-dir",
				}),
			}),
		);
	});

	it("traduce el 404 del API a Plan no encontrado", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(404, { detail: "planes_de_estudio 'p1' no encontrado" }),
		);

		const res = await GET(makeRequest("token-dir"), CTX);

		expect(res.status).toBe(404);
		expect(await res.json()).toEqual({ error: "Plan no encontrado" });
	});

	it("mapea el detail del API ante error 500", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(500, { detail: "DB caída" }),
		);

		const res = await GET(makeRequest("token-dir"), CTX);

		expect(res.status).toBe(500);
		expect(await res.json()).toEqual({ error: "DB caída" });
	});

	it("propaga el status ante error no-500 con detail", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(400, { detail: "Solicitud inválida" }),
		);

		const res = await GET(makeRequest("token-dir"), CTX);

		expect(res.status).toBe(400);
		expect(await res.json()).toEqual({ error: "Solicitud inválida" });
	});

	it("mapea el 422 con lista de Pydantic al error genérico", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(422, { detail: [{ msg: "Input inválido" }] }),
		);

		const res = await GET(makeRequest("token-dir"), CTX);

		expect(res.status).toBe(422);
		expect(await res.json()).toEqual({
			error: "Error inesperado. Intentá de nuevo más tarde.",
		});
	});

	it("lanza error sin contexto", async () => {
		const res = await GET(makeRequest("token-dir"), undefined);

		expect(res.status).toBe(400);
		expect(await res.json()).toEqual({ error: "Falta contexto" });
		expect(fetch).not.toHaveBeenCalled();
	});

	it("corta con 401 sin token de sesión", async () => {
		const res = await GET(makeRequest(), CTX);

		expect(res.status).toBe(401);
		expect(await res.json()).toEqual({ error: "No autorizado" });
		expect(fetch).not.toHaveBeenCalled();
	});
});
