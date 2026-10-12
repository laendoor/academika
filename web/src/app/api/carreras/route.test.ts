import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET } from "./route";

function makeRequest(token?: string, qs = ""): NextRequest {
	return new NextRequest(`http://localhost:3000/api/carreras${qs}`, {
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

describe("GET /api/carreras", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("reenvía los query params al API", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(200, { total: 1, items: [] }),
		);

		const res = await GET(makeRequest("token-dir", "?skip=0&limit=20"));

		expect(res.status).toBe(200);
		expect(await res.json()).toEqual({ total: 1, items: [] });
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/carreras?skip=0&limit=20"),
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
		expect(fetch).toHaveBeenCalled();
	});

	it("mapea el detail del API ante error 500", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(500, { detail: "DB caída" }),
		);

		const res = await GET(makeRequest("token-dir"));

		expect(res.status).toBe(500);
		expect(await res.json()).toEqual({ error: "DB caída" });
	});

	it("descarta skip/limit no numéricos", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(200, { total: 0, items: [] }),
		);

		const res = await GET(makeRequest("token-dir", "?skip=abc&limit=-5"));

		expect(res.status).toBe(200);
		const url = vi.mocked(fetch).mock.calls[0][0] as string;
		expect(url).toContain("/api/v1/carreras");
		expect(url).not.toContain("skip=");
		expect(url).not.toContain("limit=");
	});

	it("corta con 401 sin token de sesión", async () => {
		const res = await GET(makeRequest());

		expect(res.status).toBe(401);
		expect(await res.json()).toEqual({ error: "No autorizado" });
		expect(fetch).not.toHaveBeenCalled();
	});
});
