"use client";
import { useState } from "react";

import { Pagination } from "@/components/ui/Pagination";
import { Table, Tbody, Th } from "@/components/ui/Table";
import { useCarreras } from "@/hooks/workspace";

const PAGE_SIZE = 20;

export function CarrerasList() {
	const [skip, setSkip] = useState(0);

	const { items, total, loading, error } = useCarreras({
		skip,
		limit: PAGE_SIZE,
	});

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-zinc-800">Carreras</h2>

			{error && (
				<div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			)}

			<Table>
				<thead className="bg-zinc-50">
					<tr>
						<Th>Código</Th>
						<Th>Nombre</Th>
					</tr>
				</thead>
				<Tbody>
					{items.map((item) => (
						<tr key={item.id} className="bg-white">
							<td className="px-4 py-3 text-zinc-600">{item.codigo}</td>
							<td className="px-4 py-3 text-zinc-800">{item.nombre}</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && !error && (
				<p className="mt-4 text-sm text-zinc-500">Sin carreras.</p>
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
