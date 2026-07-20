import { type NextRequest, NextResponse } from "next/server";

import { fetchWithToken, RouteError, UNEXPECTED_ERROR } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";

export async function GET(
	request: NextRequest,
	{ params }: { params: Promise<{ path?: string[] }> },
) {
	try {
		const path = ((await params).path ?? []).join("/");
		const qs = request.nextUrl.searchParams.toString();
		const url = `${API_URL}/api/v1/workspace/${path}${qs ? `?${qs}` : ""}`;

		const res = await fetchWithToken(request, url);

		if (!res.ok) {
			const body = await res.json().catch(() => ({}));
			return NextResponse.json(body, { status: res.status });
		}

		return NextResponse.json(await res.json());
	} catch (err) {
		if (err instanceof RouteError)
			return NextResponse.json({ error: err.message }, { status: err.status });
		return NextResponse.json({ error: UNEXPECTED_ERROR }, { status: 500 });
	}
}
