import { decodeJwt } from "jose";
import { cookies } from "next/headers";

import { ACCESS_TOKEN } from "@/lib/cookies";

export async function SiteHeader() {
	const cookieStore = await cookies();
	const token = cookieStore.get(ACCESS_TOKEN)?.value;
	let email: string | undefined;
	let role: string | undefined;
	if (token) {
		try {
			const payload = decodeJwt(token);
			email = payload.email as string | undefined;
			role = payload.role as string | undefined;
		} catch {}
	}

	return (
		<header className="flex items-center justify-between border-b border-zinc-200 px-6 py-3">
			<a href="/workspace" className="text-sm font-semibold text-zinc-900">
				Académika
			</a>

			{email && role && (
				<nav className="flex items-center gap-6">
					<a
						href="/workspace"
						className="text-sm text-zinc-600 hover:text-zinc-900"
					>
						Workspace
					</a>
					{role === "admin" && (
						<a
							href="/admin"
							className="text-sm text-zinc-600 hover:text-zinc-900"
						>
							Admin
						</a>
					)}
					<span className="text-sm text-zinc-400">{email}</span>
					<a
						href="/api/auth/signout"
						className="text-sm text-zinc-500 underline hover:text-zinc-700"
					>
						Salir
					</a>
				</nav>
			)}
		</header>
	);
}
