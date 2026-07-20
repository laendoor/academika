"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const ITEMS = [
	{ label: "Fuentes", href: "/workspace" },
	{ label: "Estudiantes", href: "/workspace/estudiantes" },
	{ label: "Materias", href: "/workspace/materias" },
] as const;

export function Sidebar() {
	const pathname = usePathname();

	return (
		<aside className="flex w-56 flex-col gap-1 border-r border-zinc-200 px-4 py-6">
			{ITEMS.map((item) => {
				const active = pathname === item.href;
				return (
					<Link
						key={item.href}
						href={item.href}
						className={`rounded-md px-3 py-2 text-sm transition-colors ${
							active
								? "bg-zinc-100 font-medium text-zinc-900"
								: "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"
						}`}
					>
						{item.label}
					</Link>
				);
			})}
		</aside>
	);
}
