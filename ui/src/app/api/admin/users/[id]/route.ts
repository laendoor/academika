import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const PUT = route.apiHandler(async (req: NextRequest, ctx) => {
	if (!ctx) throw new route.RouteError("Falta contexto", 400);
	const { id } = await ctx.params;
	const token = route.requireAdminToken(req);

	const body = await req.json();
	const res = await fetch(`${API_URL}/api/v1/admin/users/${id}`, {
		method: "PUT",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${token}`,
		},
		body: JSON.stringify(body),
	});

	if (!res.ok) {
		route.throwIfAuthError(res);
		if (res.status === 404)
			throw new route.RouteError("Usuario no encontrado", 404);
		const json = await res.json().catch(() => ({}));
		const message =
			(json as { detail?: string }).detail ?? route.UNEXPECTED_ERROR;
		throw new route.RouteError(message, res.status >= 500 ? 500 : res.status);
	}

	return NextResponse.json(await res.json());
});
