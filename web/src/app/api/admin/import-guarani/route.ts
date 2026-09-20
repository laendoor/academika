import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import {
	apiHandler,
	fetchWithToken,
	RouteError,
	UNEXPECTED_ERROR,
} from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const POST = apiHandler(async (req: NextRequest) => {
	const formData = await req.formData();
	const res = await fetchWithToken(
		req,
		`${API_URL}/api/v1/admin/import-guarani`,
		{
			method: "POST",
			body: formData,
		},
	);

	if (!res.ok) {
		const json = await res.json().catch(() => ({}));
		const message = (json as { detail?: string }).detail ?? UNEXPECTED_ERROR;
		throw new RouteError(message, res.status >= 500 ? 500 : res.status);
	}

	return NextResponse.json(await res.json());
});
