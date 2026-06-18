import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const UNEXPECTED_ERROR = "Error inesperado. Intentá de nuevo más tarde.";

export class RouteError extends Error {
	constructor(
		public override message: string,
		public status: number,
	) {
		super(message);
	}
}

export function apiHandler(fn: (req: NextRequest) => Promise<NextResponse>) {
	return async (req: NextRequest) => {
		try {
			return await fn(req);
		} catch (err) {
			if (err instanceof RouteError)
				return NextResponse.json(
					{ error: err.message },
					{ status: err.status },
				);
			return NextResponse.json({ error: UNEXPECTED_ERROR }, { status: 500 });
		}
	};
}

export function ok(): NextResponse {
	return NextResponse.json({ ok: true });
}
