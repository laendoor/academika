import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { API_URL, IS_PRODUCTION } from "@/lib/constants";

const UNEXPECTED_ERROR = "Error inesperado. Intentá de nuevo más tarde.";

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  const res = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    if (res.status === 401) {
      const body = await res.json();
      return NextResponse.json({ error: body.detail }, { status: 401 });
    }
    return NextResponse.json({ error: UNEXPECTED_ERROR }, { status: 500 });
  }

  const { access_token, refresh_token } = await res.json();
  const cookieStore = await cookies();
  const secure = IS_PRODUCTION;

  cookieStore.set("access_token", access_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    maxAge: 15 * 60,
    path: "/",
  });
  cookieStore.set("refresh_token", refresh_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    maxAge: 7 * 24 * 60 * 60,
    path: "/",
  });

  return NextResponse.json({ ok: true });
}
