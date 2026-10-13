import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = route.apiHandler(async (req: NextRequest, ctx) => {
	if (!ctx) throw new route.RouteError("Falta contexto", 400);
	const { id } = await ctx.params;

	const res = await route.fetchWithToken(
		req,
		`${API_URL}/api/v1/planes/${encodeURIComponent(id)}`,
	);

	if (!res.ok) {
		if (res.status === 404)
			throw new route.RouteError("Plan no encontrado", 404);
		const json = (await res.json().catch(() => ({}))) as { detail?: string };
		const message =
			typeof json.detail === "string" ? json.detail : route.UNEXPECTED_ERROR;
		throw new route.RouteError(message, res.status >= 500 ? 500 : res.status);
	}

	return NextResponse.json(await res.json());
});
