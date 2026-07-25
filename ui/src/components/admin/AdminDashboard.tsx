"use client";
import { BookOpen, FileText, GraduationCap, Users } from "lucide-react";
import { useEffect, useState } from "react";

import * as admin from "@/lib/api/admin";
import * as sources from "@/lib/api/sources";
import * as workspace from "@/lib/api/workspace";

interface Stat {
	label: string;
	value: number | null;
	icon: React.ReactNode;
}

export function AdminDashboard() {
	const [stats, setStats] = useState<Stat[]>(() => [
		{ label: "Usuarios", value: null, icon: <Users className="h-5 w-5" /> },
		{
			label: "Estudiantes",
			value: null,
			icon: <GraduationCap className="h-5 w-5" />,
		},
		{ label: "Materias", value: null, icon: <BookOpen className="h-5 w-5" /> },
		{
			label: "Fuentes importadas",
			value: null,
			icon: <FileText className="h-5 w-5" />,
		},
	]);

	useEffect(() => {
		const update = (label: string, value: number) =>
			setStats((prev) =>
				prev.map((s) => (s.label === label ? { ...s, value } : s)),
			);

		admin.getUsers().then((r) => {
			if (r.ok) update("Usuarios", r.data.total);
		});
		workspace.getEstudiantes(0, 1).then((r) => {
			if (r.ok) update("Estudiantes", r.data.total);
		});
		workspace.getMaterias(0, 1).then((r) => {
			if (r.ok) update("Materias", r.data.total);
		});
		sources.getSources(0, 1).then((r) => {
			if (r.ok) update("Fuentes importadas", r.data.total);
		});
	}, []);

	return (
		<div className="p-8">
			<h1 className="mb-6 text-lg font-medium text-zinc-800">Dashboard</h1>
			<div className="grid grid-cols-2 gap-4">
				{stats.map((stat) => (
					<div
						key={stat.label}
						className="rounded-lg border border-zinc-200 bg-white p-5"
					>
						<div className="flex items-center gap-3">
							<div className="rounded-lg bg-zinc-100 p-2 text-zinc-500">
								{stat.icon}
							</div>
							<div>
								<div className="text-xs text-zinc-400">{stat.label}</div>
								<div className="text-2xl font-semibold text-zinc-800">
									{stat.value ?? "—"}
								</div>
							</div>
						</div>
					</div>
				))}
			</div>
		</div>
	);
}
