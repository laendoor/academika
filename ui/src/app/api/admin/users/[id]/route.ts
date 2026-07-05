import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { RouteError } from "@/lib/api/route";
import { API_URL } from "@/lib/constants";
import { ACCESS_TOKEN } from "@/lib/cookies";

const UNEXPECTED_ERROR = "Error inesperado. Intentá de nuevo más tarde.";

export async function PUT(
	req: NextRequest,
	{ params }: { params: Promise<{ id: string }> },
) {
	try {
		const { id } = await params;
		const token = req.cookies.get(ACCESS_TOKEN)?.value;
		if (!token) throw new RouteError("No autorizado", 401);

		const body = await req.json();
		const res = await fetch(`${API_URL}/api/v1/admin/users/${id}`, {
			method: "PUT",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${token}`,
			},
			body: JSON.stringify(body),
		});

		if (!res.ok) {
			if (res.status === 401 || res.status === 403)
				throw new RouteError("No autorizado", res.status);
			if (res.status === 404)
				throw new RouteError("Usuario no encontrado", 404);

			const json = await res.json().catch(() => ({}));
			const message = (json as { detail?: string }).detail ?? UNEXPECTED_ERROR;
			throw new RouteError(message, res.status >= 500 ? 500 : res.status);
		}

		return NextResponse.json(await res.json());
	} catch (err) {
		if (err instanceof RouteError)
			return NextResponse.json({ error: err.message }, { status: err.status });
		return NextResponse.json({ error: UNEXPECTED_ERROR }, { status: 500 });
	}
}
