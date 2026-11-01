"use client";
import { useState } from "react";

import { Pagination } from "@/components/ui/Pagination";
import { Table, Tbody, Th } from "@/components/ui/Table";
import { useCorrelativas, useMaterias } from "@/hooks/workspace";

const PAGE_SIZE = 20;

export function CorrelativasList() {
	const [skip, setSkip] = useState(0);
	const [materiaId, setMateriaId] = useState("");

	const { items, total, loading, error } = useCorrelativas({
		skip,
		limit: PAGE_SIZE,
		materia_id: materiaId || undefined,
	});
	// shortcut: select capado a 100 materias, agregar búsqueda por texto cuando haya más de 100
	const { items: materiasItems } = useMaterias({ skip: 0, limit: 100 });

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-sage-800">Correlativas</h2>

			<div className="mb-4 flex gap-4">
				<select
					aria-label="Filtrar por materia"
					value={materiaId}
					onChange={(e) => {
						setMateriaId(e.target.value);
						setSkip(0);
					}}
					className="rounded border border-sage-200 px-3 py-1.5 text-sm text-sage-800"
				>
					<option value="">Todas las materias</option>
					{materiasItems.map((m) => (
						<option key={m.id} value={m.id}>
							{m.codigo} — {m.nombre}
						</option>
					))}
				</select>
			</div>

			{error && (
				<div className="mb-4 rounded border border-danger/20 bg-danger/10 p-3 text-sm text-danger">
					{error}
				</div>
			)}

			<Table>
				<thead>
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
							<td className="px-4 py-3 text-sage-800">
								{item.materia.codigo} — {item.materia.nombre}
							</td>
							<td className="px-4 py-3 text-sage-700">
								{item.requisito.codigo} — {item.requisito.nombre}
							</td>
							<td className="px-4 py-3 text-sage-700">
								{item.es_obligatoria ? "Obligatoria" : "Recomendada"}
							</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && !error && (
				<p className="mt-4 text-sm text-sage-700">Sin correlativas.</p>
			)}

			<Pagination
				skip={skip}
				total={total}
				pageSize={PAGE_SIZE}
				loading={loading}
				onChange={setSkip}
			/>
		</div>
	);
}
