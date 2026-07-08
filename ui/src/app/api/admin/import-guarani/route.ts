import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import {
	apiHandler,
	RouteError,
	requireAdminToken,
	throwIfAuthError,
	UNEXPECTED_ERROR,
} from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const POST = apiHandler(async (req: NextRequest) => {
	const token = requireAdminToken(req);

	const formData = await req.formData();
	const res = await fetch(`${API_URL}/api/v1/admin/import-guarani`, {
		method: "POST",
		headers: { Authorization: `Bearer ${token}` },
		body: formData,
	});

	if (!res.ok) {
		throwIfAuthError(res);
		const json = await res.json().catch(() => ({}));
		const message = (json as { detail?: string }).detail ?? UNEXPECTED_ERROR;
		throw new RouteError(message, res.status >= 500 ? 500 : res.status);
	}

	return NextResponse.json(await res.json());
});
