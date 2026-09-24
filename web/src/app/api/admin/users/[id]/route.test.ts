import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { DELETE } from "./route";

const CTX: { params: Promise<Record<string, string>> } = {
	params: Promise.resolve({ id: "u1" }),
};

function makeRequest(token?: string): NextRequest {
	return new NextRequest("http://localhost:3000/api/admin/users/u1", {
		method: "DELETE",
		...(token && { headers: { cookie: `access_token=${token}` } }),
	});
}

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe("DELETE /api/admin/users/[id]", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("traduce el 204 del API a ok()", async () => {
		vi.mocked(fetch).mockResolvedValue(new Response(null, { status: 204 }));

		const res = await DELETE(makeRequest("token-admin"), CTX);

		expect(res.status).toBe(200);
		expect(await res.json()).toEqual({ ok: true });
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/admin/users/u1"),
			expect.objectContaining({
				method: "DELETE",
				headers: expect.objectContaining({
					Authorization: "Bearer token-admin",
				}),
			}),
		);
	});

	it("propaga el detalle del 409 (usuario con eventos de log)", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(409, {
				detail: "El usuario tiene eventos de log asociados",
			}),
		);

		const res = await DELETE(makeRequest("token-admin"), CTX);

		expect(res.status).toBe(409);
		expect(await res.json()).toEqual({
			error: "El usuario tiene eventos de log asociados",
		});
	});

	it("propaga el detalle del 422 (self-delete)", async () => {
		vi.mocked(fetch).mockResolvedValue(
			jsonResponse(422, {
				detail: "Un admin no puede eliminarse a sí mismo",
			}),
		);

		const res = await DELETE(makeRequest("token-admin"), CTX);

		expect(res.status).toBe(422);
		expect(await res.json()).toEqual({
			error: "Un admin no puede eliminarse a sí mismo",
		});
	});

	it("responde 401 sin cookie sin llamar a la API", async () => {
		const res = await DELETE(makeRequest(), CTX);

		expect(res.status).toBe(401);
		expect(fetch).not.toHaveBeenCalled();
	});
});
