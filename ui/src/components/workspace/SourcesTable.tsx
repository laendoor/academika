import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, Tbody, Th } from "@/components/ui/Table";
import type { SourceItem } from "@/lib/api/sources";
import { SHEET_TYPE_LABELS } from "@/lib/constants";

export function SourcesTable({ items }: { items: SourceItem[] }) {
	return (
		<Table>
			<thead className="bg-zinc-50">
				<tr>
					<Th>Fecha</Th>
					<Th>Tipo</Th>
					<Th>Estado</Th>
					<Th>Procesados</Th>
					<Th>Omitidos</Th>
					<Th>Error</Th>
				</tr>
			</thead>
			<Tbody>
				{items.map((item) => (
					<tr key={item.id} className="bg-white">
						<td className="px-4 py-3 text-zinc-600">
							{new Date(item.created_at).toLocaleString("es-AR")}
						</td>
						<td className="px-4 py-3 text-zinc-800">
							{item.details.sheet_type
								? (SHEET_TYPE_LABELS[item.details.sheet_type] ??
									item.details.sheet_type)
								: "—"}
						</td>
						<td className="px-4 py-3">
							<StatusBadge status={item.status} />
						</td>
						<td className="px-4 py-3 text-right text-zinc-700">
							{item.details.processed}
						</td>
						<td className="px-4 py-3 text-right text-zinc-700">
							{item.details.skipped}
						</td>
						<td className="px-4 py-3 text-zinc-600">
							{item.details.error ?? "—"}
						</td>
					</tr>
				))}
			</Tbody>
		</Table>
	);
}
