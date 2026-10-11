import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PUT } from "./route";

const CTX: { params: Promise<Record<string, string>> } = {
	params: Promise.resolve({ key: "auth.allowed_domains" }),
};

function makeRequest(token?: string): NextRequest {
	return new NextRequest(
		"http://localhost:3000/api/admin/settings/auth.allowed_domains",
		{
			method: "PUT",
			headers: {
				"Content-Type": "application/json",
				...(token && { cookie: `access_token=${token}` }),
			},
			body: JSON.stringify({ value: [] }),
		},
	);
}

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe("PUT /api/admin/settings/[key]", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("devuelve el setting actualizado", async () => {
		const updated = {
			key: "auth.allowed_domains",
			value: [],
			description: null,
		};
		vi.mocked(fetch).mockResolvedValue(jsonResponse(200, updated));

		const res = await PUT(makeRequest("token-admin"), CTX);

		expect(res.status).toBe(200);
		expect(await res.json()).toEqual(updated);
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/admin/settings/auth.allowed_domains"),
			expect.objectContaining({ method: "PUT" }),
		);
	});

	it("traduce el 404 del API", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(404, { detail: "settings 'no.existe' no encontrado" }),
		);

		const res = await PUT(makeRequest("token-admin"), CTX);

		expect(res.status).toBe(404);
		expect(await res.json()).toEqual({
			error: "Configuración no encontrada",
		});
	});

	it("sin cookie no llama al API", async () => {
		const res = await PUT(makeRequest(), CTX);

		expect(res.status).toBe(401);
		expect(fetch).not.toHaveBeenCalled();
	});
});
