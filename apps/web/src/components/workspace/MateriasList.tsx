"use client";
import { useState } from "react";

import { Pagination } from "@/components/ui/Pagination";
import { Table, Tbody, Th } from "@/components/ui/Table";
import { useMaterias } from "@/hooks/workspace";

const PAGE_SIZE = 20;

export function MateriasList() {
	const [skip, setSkip] = useState(0);

	const { items, total, loading, error } = useMaterias({
		skip,
		limit: PAGE_SIZE,
	});

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-sage-800">Materias</h2>

			{error && (
				<div className="mb-4 rounded border border-danger/20 bg-danger/10 p-3 text-sm text-danger">
					{error}
				</div>
			)}

			<Table>
				<thead>
					<tr>
						<Th>Código</Th>
						<Th>Sigla</Th>
						<Th>Nombre</Th>
						<Th>Créditos</Th>
						<Th>Plan vigente</Th>
						<Th>Carrera</Th>
					</tr>
				</thead>
				<Tbody>
					{items.map((item) => (
						<tr key={item.id} className="bg-white">
							<td className="px-4 py-3 text-sage-700">{item.codigo}</td>
							<td className="px-4 py-3 text-sage-700">{item.sigla ?? "—"}</td>
							<td className="px-4 py-3 text-sage-800">{item.nombre}</td>
							<td className="px-4 py-3 text-sage-700">
								{item.creditos?.toString() ?? "—"}
							</td>
							<td className="px-4 py-3 text-sage-700">
								{item.plan_vigente?.plan_nombre ?? "—"}
							</td>
							<td className="px-4 py-3 text-sage-700">
								{item.plan_vigente?.carrera_nombre ?? "—"}
							</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && (
				<p className="mt-4 text-sm text-sage-700">Sin materias.</p>
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
