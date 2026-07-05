import { type JWTPayload, jwtVerify } from "jose";
import { type NextRequest, NextResponse } from "next/server";

import { API_URL, IS_PRODUCTION, JWT_SECRET_KEY } from "@/lib/constants";
import {
	ACCESS_TOKEN,
	ACCESS_TOKEN_MAX_AGE,
	REFRESH_TOKEN,
} from "@/lib/cookies";

const PUBLIC_ROUTES = [
	"/login",
	"/forgot-password",
	"/reset-password",
	"/register",
];
const HOME_ROUTE = "/workspace";
const ADMIN_ROUTE = "/admin";

const secret = new TextEncoder().encode(JWT_SECRET_KEY);

type AccessTokenPayload = JWTPayload & { role: string };

async function verifyAccessToken(
	token: string,
): Promise<AccessTokenPayload | null> {
	try {
		const { payload } = await jwtVerify(token, secret, {
			algorithms: ["HS256"],
		});
		return payload as AccessTokenPayload;
	} catch {
		return null;
	}
}

async function refreshAccessToken(
	refreshToken: string,
): Promise<string | null> {
	const res = await fetch(`${API_URL}/api/v1/auth/refresh`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ refresh_token: refreshToken }),
	});
	if (!res.ok) return null;
	const { access_token } = await res.json();
	return access_token;
}

export async function proxy(request: NextRequest) {
	const path = request.nextUrl.pathname;
	const isPublic = PUBLIC_ROUTES.some((route) => path.startsWith(route));

	const accessToken = request.cookies.get(ACCESS_TOKEN)?.value;
	let payload = accessToken ? await verifyAccessToken(accessToken) : null;

	let refreshedToken: string | null = null;
	if (!payload) {
		const refreshToken = request.cookies.get(REFRESH_TOKEN)?.value;
		refreshedToken = refreshToken
			? await refreshAccessToken(refreshToken)
			: null;
		payload = refreshedToken ? await verifyAccessToken(refreshedToken) : null;
	}

	const isAuthenticated = !!payload;

	if (isAuthenticated && (isPublic || path === "/")) {
		return NextResponse.redirect(new URL(HOME_ROUTE, request.nextUrl));
	}

	if (!isAuthenticated && !isPublic) {
		return NextResponse.redirect(new URL("/login", request.nextUrl));
	}

	if (payload && path.startsWith(ADMIN_ROUTE) && payload.role !== "admin") {
		return NextResponse.redirect(new URL(HOME_ROUTE, request.nextUrl));
	}

	const response = NextResponse.next();
	if (refreshedToken) {
		response.cookies.set(ACCESS_TOKEN, refreshedToken, {
			httpOnly: true,
			secure: IS_PRODUCTION,
			sameSite: "lax",
			maxAge: ACCESS_TOKEN_MAX_AGE,
			path: "/",
		});
	}
	return response;
}

export const config = {
	matcher: [
		"/((?!api|_next/static|_next/image|.*\\.png$|.*\\.svg$|favicon\\.ico).*)",
	],
};
