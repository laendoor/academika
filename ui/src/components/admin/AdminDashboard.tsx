"use client";
import {
	BookOpen,
	GraduationCap,
	LayoutList,
	type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import * as workspace from "@/lib/api/workspace";

export function AdminDashboard() {
	const [estudiantes, setEstudiantes] = useState<number | null>(null);
	const [materias, setMaterias] = useState<number | null>(null);

	useEffect(() => {
		workspace.getEstudiantes(0, 1).then((r) => {
			if (r.ok) setEstudiantes(r.data.total);
		});
		workspace.getMaterias(0, 1).then((r) => {
			if (r.ok) setMaterias(r.data.total);
		});
	}, []);

	return (
		<div className="p-8">
			<div className="mb-6 flex items-center gap-2">
				<LayoutList className="h-5 w-5 text-zinc-500" />
				<h1 className="text-lg font-medium text-zinc-800">Datos Académicos</h1>
			</div>
			<div className="flex flex-col gap-4">
				<StatCard
					label="Estudiantes"
					href="/admin/estudiantes"
					value={estudiantes}
					Icon={GraduationCap}
				/>
				<StatCard
					label="Materias"
					href="/admin/materias"
					value={materias}
					Icon={BookOpen}
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
			className="block rounded-lg border border-zinc-200 bg-white p-5 transition-colors hover:bg-zinc-50"
		>
			<div className="flex items-center gap-3">
				<div className="rounded-lg bg-zinc-100 p-2 text-zinc-500">
					<Icon className="h-5 w-5" />
				</div>
				<p className="text-lg text-zinc-800">
					<span className="font-semibold">{value ?? "—"}</span> {label}
				</p>
			</div>
		</Link>
	);
}
