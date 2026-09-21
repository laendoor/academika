import type { NextRequest } from "next/server";

import {
	apiHandler,
	fetchWithToken,
	ok,
	RouteError,
	UNEXPECTED_ERROR,
} from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

type InviteError = { detail?: string | { msg?: string }[] };

export const POST = apiHandler(async (req: NextRequest) => {
	const body = await req.json();

	const res = await fetchWithToken(req, `${API_URL}/api/v1/auth/invite`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(body),
	});

	if (res.ok) return ok();

	const { detail } = (await res.json().catch(() => ({}))) as InviteError;

	if (res.status === 409 && typeof detail === "string")
		throw new RouteError(detail, 409);

	if (res.status === 422)
		throw new RouteError(
			Array.isArray(detail)
				? (detail[0]?.msg ?? UNEXPECTED_ERROR)
				: UNEXPECTED_ERROR,
			422,
		);

	throw new Error();
});
