import { type NextRequest, NextResponse } from "next/server";

import { ACCESS_TOKEN } from "@/lib/cookies";

const PUBLIC_ROUTES = ["/login", "/forgot-password", "/reset-password"];
const HOME_ROUTE = "/workspace";

export function proxy(request: NextRequest) {
	const path = request.nextUrl.pathname;
	const isPublic = PUBLIC_ROUTES.some((route) => path.startsWith(route));
	const accessToken = request.cookies.get(ACCESS_TOKEN)?.value;
	const isAuthenticated = !!accessToken;

	if (isAuthenticated && (isPublic || path === "/")) {
		return NextResponse.redirect(new URL(HOME_ROUTE, request.nextUrl));
	}

	if (!isAuthenticated && !isPublic) {
		return NextResponse.redirect(new URL("/login", request.nextUrl));
	}

	return NextResponse.next();
}

export const config = {
	matcher: [
		"/((?!api|_next/static|_next/image|.*\\.png$|.*\\.svg$|favicon\\.ico).*)",
	],
};
