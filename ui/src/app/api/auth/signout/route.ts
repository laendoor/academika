import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function GET(request: NextRequest) {
	const response = NextResponse.redirect(new URL("/login", request.url));
	response.cookies.delete("access_token");
	response.cookies.delete("refresh_token");
	return response;
}
