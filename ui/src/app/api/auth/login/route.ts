import { cookies } from "next/headers";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { API_URL } from "@/lib/constants";
import { setAuthCookies } from "@/lib/cookies";

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
	setAuthCookies(cookieStore, { access_token, refresh_token });

	return NextResponse.json({ ok: true });
}
