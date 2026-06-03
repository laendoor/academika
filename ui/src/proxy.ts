import { type NextRequest, NextResponse } from "next/server";

const PUBLIC_ROUTES = ["/login", "/forgot-password", "/reset-password"];

export function proxy(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const isPublic = PUBLIC_ROUTES.some((route) => path.startsWith(route));
  const accessToken = request.cookies.get("access_token")?.value;

  if (isPublic || accessToken) {
    return NextResponse.next();
  }

  return NextResponse.redirect(new URL("/login", request.nextUrl));
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|.*\\.png$|.*\\.svg$|favicon\\.ico).*)",
  ],
};
