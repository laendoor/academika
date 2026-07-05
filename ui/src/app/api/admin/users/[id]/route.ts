import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { apiHandler, RouteError, UNEXPECTED_ERROR } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";
import { ACCESS_TOKEN } from "@/lib/cookies";

export const PUT = apiHandler(async (req: NextRequest, ctx) => {
	const { id } = await ctx!.params;
	const token = req.cookies.get(ACCESS_TOKEN)?.value;
	if (!token) throw new RouteError("No autorizado", 401);

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
		if (res.status === 401 || res.status === 403)
			throw new RouteError("No autorizado", res.status);
		if (res.status === 404) throw new RouteError("Usuario no encontrado", 404);
		const json = await res.json().catch(() => ({}));
		const message = (json as { detail?: string }).detail ?? UNEXPECTED_ERROR;
		throw new RouteError(message, res.status >= 500 ? 500 : res.status);
	}

	return NextResponse.json(await res.json());
});
