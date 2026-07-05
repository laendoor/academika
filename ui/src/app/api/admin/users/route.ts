import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { apiHandler, RouteError } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";
import { ACCESS_TOKEN } from "@/lib/cookies";

export const GET = apiHandler(async (req: NextRequest) => {
	const token = req.cookies.get(ACCESS_TOKEN)?.value;
	if (!token) throw new RouteError("No autorizado", 401);

	const res = await fetch(`${API_URL}/api/v1/admin/users?skip=0&limit=100`, {
		// limit=100 hardcodeado: el panel de usuarios de backoffice asume
		// una cantidad pequeña de usuarios. Si escala, forwardear searchParams.
		headers: { Authorization: `Bearer ${token}` },
	});

	if (!res.ok) {
		if (res.status === 401 || res.status === 403)
			throw new RouteError("No autorizado", res.status);
		throw new Error();
	}

	return NextResponse.json(await res.json());
});
