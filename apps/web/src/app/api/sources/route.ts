import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = route.apiHandler(async (req: NextRequest) => {
	const skip = req.nextUrl.searchParams.get("skip") ?? "0";
	const limit = req.nextUrl.searchParams.get("limit") ?? "20";
	const res = await route.fetchWithToken(
		req,
		`${API_URL}/api/v1/sources?skip=${skip}&limit=${limit}`,
	);

	if (!res.ok) throw new Error();

	return NextResponse.json(await res.json());
});
