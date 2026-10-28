import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET as getAlumnos } from "@/app/api/alumnos/search/route";
import { GET as getMaterias } from "@/app/api/materias/search/route";

const HANDLERS = [
	{
		ruta: "/api/alumnos/search",
		api: "/api/v1/alumnos/search",
		handler: getAlumnos,
	},
	{
		ruta: "/api/materias/search",
		api: "/api/v1/materias/search",
		handler: getMaterias,
	},
];

function makeRequest(url: string, token = "token-director"): NextRequest {
	return new NextRequest(url, { headers: { cookie: `access_token=${token}` } });
}

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe.each(HANDLERS)("GET $ruta", ({ ruta, api, handler }) => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("reenvía q al API con el token de la cookie", async () => {
		const hits = [{ id: "a1", label: "Núñez, Lucía", term: "Núñez Lucía" }];
		vi.mocked(fetch).mockResolvedValue(jsonResponse(200, hits));

		const res = await handler(
			makeRequest(`http://localhost:3000${ruta}?q=N%C3%BA%C3%B1ez`),
		);

		expect(await res.json()).toEqual(hits);
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining(`${api}?q=N%C3%BA%C3%B1ez`),
			expect.objectContaining({
				headers: expect.objectContaining({
					Authorization: "Bearer token-director",
				}),
			}),
		);
	});

	it("sin cookie responde 401 sin llamar al API", async () => {
		const req = new NextRequest(`http://localhost:3000${ruta}?q=ana`);

		const res = await handler(req);

		expect(res.status).toBe(401);
		expect(fetch).not.toHaveBeenCalled();
	});

	it("propaga el status y el detalle del API", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(422, { detail: "String should have at least 2 characters" }),
		);

		const res = await handler(makeRequest(`http://localhost:3000${ruta}?q=a`));

		expect(res.status).toBe(422);
		expect(await res.json()).toEqual({
			error: "String should have at least 2 characters",
		});
	});
});
