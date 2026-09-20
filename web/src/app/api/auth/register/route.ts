import { cookies } from "next/headers";
import type { NextRequest } from "next/server";

import { apiHandler, ok, RouteError } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";
import { setAuthCookies } from "@/lib/cookies";

export const POST = apiHandler(async (req: NextRequest) => {
	const { token, password } = await req.json();

	const res = await fetch(`${API_URL}/api/v1/auth/register`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ token, password }),
	});

	if (res.ok) {
		const { access_token, refresh_token } = await res.json();
		setAuthCookies(await cookies(), { access_token, refresh_token });
		return ok();
	}

	const body = await res.json();

	if (res.status === 401 || res.status === 409)
		throw new RouteError(body.detail, res.status);

	if (res.status === 422)
		throw new RouteError(
			Array.isArray(body.detail) ? body.detail[0]?.msg : body.detail,
			422,
		);

	throw new Error();
});
