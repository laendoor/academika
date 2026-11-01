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
			<h2 className="mb-4 text-lg font-medium text-sage-800">Carreras</h2>

			{error && (
				<div className="mb-4 rounded border border-danger/20 bg-danger/10 p-3 text-sm text-danger">
					{error}
				</div>
			)}

			<Table>
				<thead>
					<tr>
						<Th>Código</Th>
						<Th>Nombre</Th>
					</tr>
				</thead>
				<Tbody>
					{items.map((item) => (
						<tr key={item.id} className="bg-white">
							<td className="px-4 py-3 text-sage-700">{item.codigo}</td>
							<td className="px-4 py-3 text-sage-800">{item.nombre}</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && !error && (
				<p className="mt-4 text-sm text-sage-700">Sin carreras.</p>
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
