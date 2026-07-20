"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const ITEMS = [
	{ label: "Importar Datos", href: "/admin/importar" },
	{ label: "Ver Datos Importados", href: "/admin/datos" },
	{ label: "Estudiantes", href: "/admin/estudiantes" },
	{ label: "Materias", href: "/admin/materias" },
] as const;

export function AdminSidebar() {
	const pathname = usePathname();
	const active = (href: string) => pathname.startsWith(href);

	return (
		<aside className="flex w-56 flex-col gap-1 border-r border-zinc-200 px-4 py-6">
			{ITEMS.map((item) => {
				const isActive = active(item.href);
				return (
					<Link
						key={item.href}
						href={item.href}
						className={`rounded-md px-3 py-2 text-sm transition-colors ${
							isActive
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
