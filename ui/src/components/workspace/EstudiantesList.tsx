"use client";
import { useEffect, useState } from "react";

import { Table, Tbody, Th } from "@/components/ui/Table";
import { useEstudiantes } from "@/hooks/workspace";
import type { CarreraOption, EstadoOption } from "@/lib/api/workspace";
import * as workspace from "@/lib/api/workspace";

const PAGE_SIZE = 20;

export function EstudiantesList() {
	const [skip, setSkip] = useState(0);
	const [carreraId, setCarreraId] = useState("");
	const [estadoAcademicoId, setEstadoAcademicoId] = useState("");
	const [carreras, setCarreras] = useState<CarreraOption[]>([]);
	const [estadosAcademicos, setEstadosAcademicos] = useState<EstadoOption[]>(
		[],
	);

	const { items, total, loading, error } = useEstudiantes({
		skip,
		limit: PAGE_SIZE,
		carrera_id: carreraId || undefined,
		estado_academico: estadoAcademicoId || undefined,
	});

	useEffect(() => {
		workspace.getCarreras().then((r) => {
			if (r.ok) setCarreras(r.data.items);
			else console.warn("Error fetching carreras:", r.error);
		});
		workspace.getEstadosAcademicos().then((r) => {
			if (r.ok) setEstadosAcademicos(r.data);
			else console.warn("Error fetching estados:", r.error);
		});
	}, []);

	const hasNext = skip + PAGE_SIZE < total;
	const hasPrev = skip > 0;

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-zinc-800">Estudiantes</h2>

			<div className="mb-4 flex gap-4">
				<select
					value={carreraId}
					onChange={(e) => {
						setCarreraId(e.target.value);
						setSkip(0);
					}}
					className="rounded border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700"
				>
					<option value="">Todas las carreras</option>
					{carreras.map((c) => (
						<option key={c.id} value={c.id}>
							{c.nombre}
						</option>
					))}
				</select>

				<select
					value={estadoAcademicoId}
					onChange={(e) => {
						setEstadoAcademicoId(e.target.value);
						setSkip(0);
					}}
					className="rounded border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700"
				>
					<option value="">Todos los estados</option>
					{estadosAcademicos.map((e) => (
						<option key={e.key} value={e.key}>
							{e.nombre}
						</option>
					))}
				</select>
			</div>

			{error && (
				<div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			)}

			<Table>
				<thead className="bg-zinc-50">
					<tr>
						<Th>Legajo</Th>
						<Th>DNI</Th>
						<Th>Apellido</Th>
						<Th>Nombre</Th>
						<Th>Carreras</Th>
						<Th>Estado</Th>
					</tr>
				</thead>
				<Tbody>
					{items.map((item) => (
						<tr key={item.id} className="bg-white">
							<td className="px-4 py-3 text-zinc-600">{item.legajo ?? "—"}</td>
							<td className="px-4 py-3 text-zinc-600">{item.dni}</td>
							<td className="px-4 py-3 text-zinc-800">{item.apellido}</td>
							<td className="px-4 py-3 text-zinc-800">{item.nombre}</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.carreras.map((c) => c.carrera_nombre).join(", ")}
							</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.carreras.map((c) => c.estado_academico).join(", ")}
							</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && (
				<p className="mt-4 text-sm text-zinc-500">Sin estudiantes.</p>
			)}

			{(hasPrev || hasNext) && (
				<div className="mt-4 flex justify-between">
					<button
						type="button"
						onClick={() => setSkip((s) => Math.max(0, s - PAGE_SIZE))}
						disabled={!hasPrev || loading}
						className="rounded border border-zinc-200 px-3 py-1 text-sm text-zinc-700 hover:bg-zinc-50 disabled:opacity-50"
					>
						Anterior
					</button>
					<span className="text-sm text-zinc-500">
						{skip + 1}-{Math.min(skip + PAGE_SIZE, total)} de {total}
					</span>
					<button
						type="button"
						onClick={() => setSkip((s) => s + PAGE_SIZE)}
						disabled={!hasNext || loading}
						className="rounded border border-zinc-200 px-3 py-1 text-sm text-zinc-700 hover:bg-zinc-50 disabled:opacity-50"
					>
						Siguiente
					</button>
				</div>
			)}
		</div>
	);
}
