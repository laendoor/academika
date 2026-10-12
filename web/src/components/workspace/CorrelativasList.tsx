"use client";
import { useEffect, useState } from "react";

import { Table, Tbody, Th } from "@/components/ui/Table";
import { useCorrelativas, useMaterias } from "@/hooks/workspace";
import type { MateriaRow } from "@/lib/api/workspace";

const PAGE_SIZE = 20;

export function CorrelativasList() {
	const [skip, setSkip] = useState(0);
	const [materiaId, setMateriaId] = useState("");
	const [materias, setMaterias] = useState<MateriaRow[]>([]);

	const { items, total, loading, error } = useCorrelativas({
		skip,
		limit: PAGE_SIZE,
		materia_id: materiaId || undefined,
	});
	const { items: materiasItems } = useMaterias({ skip: 0, limit: 100 });

	useEffect(() => {
		setMaterias(materiasItems);
	}, [materiasItems]);

	const hasNext = skip + PAGE_SIZE < total;
	const hasPrev = skip > 0;

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-zinc-800">Correlativas</h2>

			<div className="mb-4 flex gap-4">
				<select
					value={materiaId}
					onChange={(e) => {
						setMateriaId(e.target.value);
						setSkip(0);
					}}
					className="rounded border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700"
				>
					<option value="">Todas las materias</option>
					{materias.map((m) => (
						<option key={m.id} value={m.id}>
							{m.codigo} — {m.nombre}
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
						<Th>Materia</Th>
						<Th>Requisito</Th>
						<Th>Tipo</Th>
					</tr>
				</thead>
				<Tbody>
					{items.map((item) => (
						<tr
							key={`${item.materia.id}-${item.requisito.id}`}
							className="bg-white"
						>
							<td className="px-4 py-3 text-zinc-800">
								{item.materia.codigo} — {item.materia.nombre}
							</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.requisito.codigo} — {item.requisito.nombre}
							</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.es_obligatoria ? "Obligatoria" : "Recomendada"}
							</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && (
				<p className="mt-4 text-sm text-zinc-500">Sin correlativas.</p>
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
