import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { GET } from "./route";

function makeRequest(token?: string): NextRequest {
	return new NextRequest("http://localhost:3000/api/admin/settings", {
		...(token && { headers: { cookie: `access_token=${token}` } }),
	});
}

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

describe("GET /api/admin/settings", () => {
	beforeEach(() => {
		vi.stubGlobal("fetch", vi.fn());
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("devuelve la lista del API", async () => {
		const settings = [
			{
				key: "auth.allowed_domains",
				value: ["@unq.edu.ar"],
				description: null,
			},
		];
		vi.mocked(fetch).mockResolvedValue(jsonResponse(200, settings));

		const res = await GET(makeRequest("token-admin"));

		expect(res.status).toBe(200);
		expect(await res.json()).toEqual(settings);
		expect(fetch).toHaveBeenCalledWith(
			expect.stringContaining("/api/v1/admin/settings"),
			expect.objectContaining({
				headers: expect.objectContaining({
					Authorization: "Bearer token-admin",
				}),
			}),
		);
	});

	it("sin cookie no llama al API", async () => {
		const res = await GET(makeRequest());

		expect(res.status).toBe(401);
		expect(fetch).not.toHaveBeenCalled();
	});
});
