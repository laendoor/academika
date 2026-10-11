import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = route.apiHandler(async (req: NextRequest) => {
	const res = await route.fetchWithToken(
		req,
		`${API_URL}/api/v1/admin/settings`,
	);

	if (!res.ok) {
		const json = await res.json().catch(() => ({}));
		const message =
			(json as { detail?: string }).detail ?? route.UNEXPECTED_ERROR;
		throw new route.RouteError(message, res.status >= 500 ? 500 : res.status);
	}

	return NextResponse.json(await res.json());
});
