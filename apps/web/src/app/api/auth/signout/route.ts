import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { clearAuthCookies } from "@/lib/cookies";

export function GET(request: NextRequest) {
	const host = request.headers.get("host") ?? "localhost:3000";
	const proto = request.headers.get("x-forwarded-proto") ?? "http";
	const response = NextResponse.redirect(
		new URL("/login", `${proto}://${host}`),
	);
	clearAuthCookies(response);
	return response;
}
