import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { API_URL } from "@/lib/constants";

const UNEXPECTED_ERROR = "Error inesperado. Intentá de nuevo más tarde.";

export async function POST(request: NextRequest) {
  const { email } = await request.json();

  const res = await fetch(`${API_URL}/api/v1/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (res.ok || res.status === 204) {
    return NextResponse.json({ sent: true });
  }

  return NextResponse.json({ error: UNEXPECTED_ERROR }, { status: 500 });
}
