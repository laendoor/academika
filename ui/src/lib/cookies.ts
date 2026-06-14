import type { cookies } from "next/headers";
import type { NextResponse } from "next/server";

import { IS_PRODUCTION } from "@/lib/constants";

export const ACCESS_TOKEN = "access_token";
export const REFRESH_TOKEN = "refresh_token";

const ACCESS_TOKEN_MAX_AGE = 15 * 60;
const REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60;

type CookieStore = Awaited<ReturnType<typeof cookies>>;

export function setAuthCookies(
	cookieStore: CookieStore,
	tokens: { access_token: string; refresh_token: string },
) {
	const secure = IS_PRODUCTION;
	cookieStore.set(ACCESS_TOKEN, tokens.access_token, {
		httpOnly: true,
		secure,
		sameSite: "lax",
		maxAge: ACCESS_TOKEN_MAX_AGE,
		path: "/",
	});
	cookieStore.set(REFRESH_TOKEN, tokens.refresh_token, {
		httpOnly: true,
		secure,
		sameSite: "lax",
		maxAge: REFRESH_TOKEN_MAX_AGE,
		path: "/",
	});
}

export function clearAuthCookies(response: NextResponse) {
	response.cookies.delete(ACCESS_TOKEN);
	response.cookies.delete(REFRESH_TOKEN);
}
