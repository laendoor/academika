"use client";
import { LayoutList, type LucideIcon, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { APP_SHA, APP_VERSION } from "@/lib/constants";

export function AdminSidebar() {
	return (
		<aside className="flex w-56 flex-col gap-4 border-r border-accent-100 bg-accent-50 px-4 py-6">
			<div>
				<SectionHeader label="Datos Académicos" Icon={LayoutList} />
				<LinkItem label="Estudiantes" href="/admin/estudiantes" />
				<LinkItem label="Cursadas e Inscripciones" href="/admin/cursadas" />
				<LinkItem label="Materias" href="/admin/materias" />
				<LinkItem label="Carreras" href="/admin/carreras" />
				<LinkItem label="Planes" href="/admin/planes" />
				<LinkItem label="Correlativas" href="/admin/correlativas" />
				<hr className="mx-1 my-1 border-sage-200" />
				<LinkItem label="Importar Datos" href="/admin/importar" />
			</div>

			<div>
				<SectionHeader label="Sistema" Icon={Settings} />
				<LinkItem label="Usuarios" href="/admin/usuarios" />
				<LinkItem label="Configuración" href="/admin/settings" />
			</div>

			<div className="mt-auto border-t border-sage-200 px-3 pt-2 text-xs text-sage-700">
				v{APP_VERSION} · {APP_SHA}
			</div>
		</aside>
	);
}

function SectionHeader({ label, Icon }: { label: string; Icon: LucideIcon }) {
	return (
		<div className="mb-1 flex items-center gap-2 px-3 text-xs font-medium uppercase tracking-wider text-sage-700">
			<Icon className="h-4 w-4" />
			{label}
		</div>
	);
}

function LinkItem({ label, href }: { label: string; href: string }) {
	const pathname = usePathname();
	const isActive = pathname.startsWith(href);

	return (
		<Link
			href={href}
			className={`block rounded-md px-3 py-1.5 text-sm transition-colors ${
				isActive
					? "bg-accent-100 font-medium text-accent-950"
					: "text-sage-800 hover:bg-white hover:text-accent-950"
			}`}
		>
			{label}
		</Link>
	);
}
