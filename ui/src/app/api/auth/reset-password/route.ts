import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { API_URL } from "@/lib/constants";

const UNEXPECTED_ERROR = "Error inesperado. Intentá de nuevo más tarde.";

export async function POST(request: NextRequest) {
  const { token, new_password } = await request.json();

  const res = await fetch(`${API_URL}/api/v1/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password }),
  });

  if (res.ok || res.status === 204) {
    return NextResponse.json({ ok: true });
  }

  if (res.status === 401) {
    const body = await res.json();
    return NextResponse.json({ error: body.detail }, { status: 401 });
  }

  return NextResponse.json({ error: UNEXPECTED_ERROR }, { status: 500 });
}
