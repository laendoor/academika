import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import {
	apiHandler,
	requireAdminToken,
	throwIfAuthError,
} from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const GET = apiHandler(async (req: NextRequest) => {
	const token = requireAdminToken(req);

	const res = await fetch(`${API_URL}/api/v1/admin/users?skip=0&limit=100`, {
		// limit=100 hardcodeado: el panel de usuarios de backoffice asume
		// una cantidad pequeña de usuarios. Si escala, forwardear searchParams.
		headers: { Authorization: `Bearer ${token}` },
	});

	if (!res.ok) {
		throwIfAuthError(res);
		throw new Error();
	}

	return NextResponse.json(await res.json());
});
