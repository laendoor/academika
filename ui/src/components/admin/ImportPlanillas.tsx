"use client";
import { useRef, useState } from "react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Table, Tbody, Th } from "@/components/ui/Table";
import { useAdminImport } from "@/hooks/admin";
import { SHEET_TYPE_LABELS } from "@/lib/constants";

export function ImportPlanillas() {
	const { uploading, items, total, loading, error, handleUpload, refresh } =
		useAdminImport();
	const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
	const inputRef = useRef<HTMLInputElement>(null);

	function onChange(e: React.ChangeEvent<HTMLInputElement>) {
		setSelectedFiles(Array.from(e.target.files ?? []));
	}

	async function onSubmit(e: React.FormEvent) {
		e.preventDefault();
		if (!selectedFiles.length) return;
		await handleUpload(selectedFiles);
		setSelectedFiles([]);
		if (inputRef.current) inputRef.current.value = "";
	}

	return (
		<div>
			<form onSubmit={onSubmit} className="mb-6 flex flex-wrap items-end gap-3">
				<input
					ref={inputRef}
					type="file"
					multiple
					accept=".csv"
					onChange={onChange}
					disabled={uploading}
					className="text-sm text-zinc-700 file:mr-3 file:rounded file:border-0 file:bg-zinc-100 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-zinc-700 hover:file:bg-zinc-200 disabled:opacity-50"
				/>
				<button
					type="submit"
					disabled={uploading || !selectedFiles.length}
					className="rounded bg-zinc-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
				>
					{uploading ? "Subiendo..." : "Subir planillas"}
				</button>
				{!uploading && (
					<button
						type="button"
						onClick={refresh}
						disabled={loading}
						className="text-sm text-zinc-500 underline hover:text-zinc-700 disabled:opacity-50"
					>
						Refrescar
					</button>
				)}
			</form>

			{error && (
				<div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			)}

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

			{total === 0 && !loading && (
				<p className="mt-4 text-sm text-zinc-500">
					Sin importaciones registradas todavía.
				</p>
			)}
		</div>
	);
}
