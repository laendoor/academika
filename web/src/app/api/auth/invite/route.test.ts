import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";

function makeRequest(token?: string): NextRequest {
	return new NextRequest("http://localhost:3000/api/auth/invite", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			...(token && { cookie: `access_token=${token}` }),
		},
		body: JSON.stringify({ email: "nuevo@unq.edu.ar", role: "docente" }),
	});
}

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe("POST /api/auth/invite", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("traduce el 204 del API a ok()", async () => {
		vi.mocked(fetch).mockResolvedValue(new Response(null, { status: 204 }));

		const res = await POST(makeRequest("token-admin"));

		expect(res.status).toBe(200);
		expect(await res.json()).toEqual({ ok: true });
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/auth/invite"),
			expect.objectContaining({
				method: "POST",
				headers: expect.objectContaining({
					Authorization: "Bearer token-admin",
				}),
			}),
		);
	});

	it("propaga el detalle del 409 (usuario ya existe)", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(409, {
				detail: "Ya existe un usuario activo con email 'nuevo@unq.edu.ar'",
			}),
		);

		const res = await POST(makeRequest("token-admin"));

		expect(res.status).toBe(409);
		expect(await res.json()).toEqual({
			error: "Ya existe un usuario activo con email 'nuevo@unq.edu.ar'",
		});
	});

	it("propaga el detalle del 401 (dominio no autorizado)", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(401, {
				detail: "El email debe pertenecer al dominio @unq.edu.ar",
			}),
		);

		const res = await POST(makeRequest("token-admin"));

		expect(res.status).toBe(401);
		expect(await res.json()).toEqual({
			error: "El email debe pertenecer al dominio @unq.edu.ar",
		});
	});

	it("propaga el primer msg del 422 (validación)", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(422, { detail: [{ msg: "Input should be..." }] }),
		);

		const res = await POST(makeRequest("token-admin"));

		expect(res.status).toBe(422);
		expect(await res.json()).toEqual({ error: "Input should be..." });
	});

	it("responde genérico ante un 500 del API", async () => {
		vi.mocked(fetch).mockResolvedValue(jsonResponse(500, { detail: "boom" }));

		const res = await POST(makeRequest("token-admin"));

		expect(res.status).toBe(500);
		expect(await res.json()).toEqual({
			error: "Error inesperado. Intentá de nuevo más tarde.",
		});
	});

	it("corta con 401 sin token de sesión", async () => {
		const res = await POST(makeRequest());

		expect(res.status).toBe(401);
		expect(await res.json()).toEqual({ error: "No autorizado" });
		expect(fetch).not.toHaveBeenCalled();
	});
});
