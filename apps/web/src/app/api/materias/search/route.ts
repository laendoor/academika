import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = route.apiHandler(async (req: NextRequest) => {
	const q = req.nextUrl.searchParams.get("q") ?? "";
	const params = new URLSearchParams({ q });
	const res = await route.fetchWithToken(
		req,
		`${API_URL}/api/v1/materias/search?${params}`,
	);
	if (!res.ok) {
		const json = (await res.json().catch(() => ({}))) as { detail?: string };
		const message =
			typeof json.detail === "string" ? json.detail : route.UNEXPECTED_ERROR;
		throw new route.RouteError(message, res.status >= 500 ? 500 : res.status);
	}
	return NextResponse.json(await res.json());
});
