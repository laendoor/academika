import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { clearAuthCookies } from "@/lib/cookies";

export function GET(request: NextRequest) {
	const response = NextResponse.redirect(new URL("/login", request.url));
	clearAuthCookies(response);
	return response;
}
