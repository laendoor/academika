import { decodeJwt } from "jose";
import { cookies } from "next/headers";
import Link from "next/link";

import { ADMIN_ROLE } from "@/lib/constants";
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
		} catch {} // ponytail: proxy already verified the token; decode failure = render without user
	}

	return (
		<header className="flex items-center justify-between border-b border-zinc-200 px-6 py-3">
			<Link href="/workspace" className="text-sm font-semibold text-zinc-900">
				Académika
			</Link>

			{email && role && (
				<nav className="flex items-center gap-6">
					<Link
						href="/workspace"
						className="text-sm text-zinc-600 hover:text-zinc-900"
					>
						Workspace
					</Link>
					{role === ADMIN_ROLE && (
						<Link
							href="/admin"
							className="text-sm text-zinc-600 hover:text-zinc-900"
						>
							Admin
						</Link>
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
