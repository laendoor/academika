"use client";
import type { LucideIcon } from "lucide-react";
import {
	BookOpen,
	ClipboardList,
	GraduationCap,
	LayoutList,
	School,
} from "lucide-react";
import Link from "next/link";

import { useAdminStats } from "@/hooks/admin";

export function AdminDashboard() {
	const { estudiantes, materias, carreras, planes, status } = useAdminStats();

	return (
		<div className="p-8">
			<div className="mb-6 flex items-center gap-2">
				<LayoutList className="h-5 w-5 text-sage-700" />
				<h1 className="text-lg font-medium text-sage-800">Datos Académicos</h1>
			</div>
			{status === "error" && (
				<p className="mb-4 text-sm text-danger">Error al cargar datos.</p>
			)}
			<div className="grid grid-cols-2 gap-4">
				<StatCard
					label="Carreras"
					href="/admin/carreras"
					value={carreras}
					Icon={School}
				/>
				<StatCard
					label="Materias"
					href="/admin/materias"
					value={materias}
					Icon={BookOpen}
				/>
				<StatCard
					label="Planes"
					href="/admin/planes"
					value={planes}
					Icon={ClipboardList}
				/>
				<StatCard
					label="Estudiantes"
					href="/admin/estudiantes"
					value={estudiantes}
					Icon={GraduationCap}
				/>
			</div>
		</div>
	);
}

function StatCard({
	label,
	href,
	value,
	Icon,
}: {
	label: string;
	href: string;
	value: number | null;
	Icon: LucideIcon;
}) {
	return (
		<Link
			href={href}
			className="block rounded-lg border border-sage-200 bg-white p-5 transition-colors hover:bg-sage-50"
		>
			<div className="flex items-center gap-3">
				<div className="rounded-lg bg-sage-100 p-2 text-sage-700">
					<Icon className="h-5 w-5" />
				</div>
				<p className="text-lg text-sage-800">
					<span className="font-semibold">{value ?? "—"}</span> {label}
				</p>
			</div>
		</Link>
	);
}
