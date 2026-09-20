import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { apiHandler } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export const POST = apiHandler(async (req: NextRequest) => {
	const { email } = await req.json();

	const res = await fetch(`${API_URL}/api/v1/auth/forgot-password`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ email }),
	});

	if (!res.ok) throw new Error();
	return NextResponse.json({ sent: true });
});
