import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = route.apiHandler(async (req: NextRequest) => {
	const qs = req.nextUrl.searchParams.toString();
	const res = await route.fetchWithToken(
		req,
		`${API_URL}/api/v1/correlativas${qs ? `?${qs}` : ""}`,
	);
	if (!res.ok)
		return NextResponse.json(await res.json().catch(() => ({})), {
			status: res.status,
		});
	return NextResponse.json(await res.json());
});
