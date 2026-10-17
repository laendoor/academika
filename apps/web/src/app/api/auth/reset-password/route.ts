import type { NextRequest } from "next/server";

import { apiHandler, ok, RouteError } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const POST = apiHandler(async (req: NextRequest) => {
	const { token, new_password } = await req.json();

	const res = await fetch(`${API_URL}/api/v1/auth/reset-password`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ token, new_password }),
	});

	if (res.ok) return ok();
	if (res.status === 401) throw new RouteError((await res.json()).detail, 401);
	throw new Error();
});
