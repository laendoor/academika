import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = route.apiHandler(async (req: NextRequest) => {
	const qs = route.paginationParams(req.nextUrl.searchParams).toString();
	const res = await route.fetchWithToken(
		req,
		`${API_URL}/api/v1/carreras${qs ? `?${qs}` : ""}`,
	);
	if (!res.ok) {
		const json = (await res.json().catch(() => ({}))) as { detail?: string };
		return NextResponse.json(
			{ error: json.detail ?? route.UNEXPECTED_ERROR },
			{ status: res.status },
		);
	}
	return NextResponse.json(await res.json());
});
