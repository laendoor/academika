import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import * as route from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = route.apiHandler(async (req: NextRequest) => {
	const token = route.requireAdminToken(req);

	const skip = req.nextUrl.searchParams.get("skip") ?? "0";
	const limit = req.nextUrl.searchParams.get("limit") ?? "20";
	const res = await fetch(
		`${API_URL}/api/v1/sources?skip=${skip}&limit=${limit}`,
		{ headers: { Authorization: `Bearer ${token}` } },
	);

	if (!res.ok) {
		route.throwIfAuthError(res);
		throw new Error();
	}

	return NextResponse.json(await res.json());
});
