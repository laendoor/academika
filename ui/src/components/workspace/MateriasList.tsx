"use client";
import { useState } from "react";

import { Table, Tbody, Th } from "@/components/ui/Table";
import { useMaterias } from "@/hooks/workspace";

const PAGE_SIZE = 20;

export function MateriasList() {
	const [skip, setSkip] = useState(0);

	const { items, total, loading, error } = useMaterias({
		skip,
		limit: PAGE_SIZE,
	});

	const hasNext = skip + PAGE_SIZE < total;
	const hasPrev = skip > 0;

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-zinc-800">Materias</h2>

			{error && (
				<div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			)}

			<Table>
				<thead className="bg-zinc-50">
					<tr>
						<Th>Nombre</Th>
						<Th>Código</Th>
						<Th>Sigla</Th>
						<Th>Créditos</Th>
						<Th>Plan vigente</Th>
						<Th>Carrera</Th>
					</tr>
				</thead>
				<Tbody>
					{items.map((item) => (
						<tr key={item.id} className="bg-white">
							<td className="px-4 py-3 text-zinc-800">{item.nombre}</td>
							<td className="px-4 py-3 text-zinc-600">{item.codigo}</td>
							<td className="px-4 py-3 text-zinc-600">{item.sigla ?? "—"}</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.creditos?.toString() ?? "—"}
							</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.plan_vigente?.plan_nombre ?? "—"}
							</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.plan_vigente?.carrera_nombre ?? "—"}
							</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && (
				<p className="mt-4 text-sm text-zinc-500">Sin materias.</p>
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
