import { cookies } from "next/headers";
import type { NextRequest } from "next/server";

import { apiHandler, ok, RouteError } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";
import { setAuthCookies } from "@/lib/cookies";

export const POST = apiHandler(async (req: NextRequest) => {
	const { email, password } = await req.json();

	const res = await fetch(`${API_URL}/api/v1/auth/login`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ email, password }),
	});

	if (!res.ok) {
		if (res.status === 401)
			throw new RouteError((await res.json()).detail, 401);
		throw new Error();
	}

	const { access_token, refresh_token } = await res.json();
	setAuthCookies(await cookies(), { access_token, refresh_token });
	return ok();
});
