import { type NextRequest, NextResponse } from "next/server";

import { apiHandler, RouteError } from "@/lib/api/route";
import { ACCESS_TOKEN } from "@/lib/cookies";

export const GET = apiHandler(async (req: NextRequest) => {
	const token = req.cookies.get(ACCESS_TOKEN)?.value;
	if (!token) throw new RouteError("No autorizado", 401);
	return NextResponse.json({ token });
});
// ponytail: expone el token al cliente JS para WebSocket cross-origin.
// En prod con mismo-origen, migrar a cookie-based auth en ws.py (websocket.cookies).
