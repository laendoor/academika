"use client";
import { useRef, useState } from "react";

import { Table, Tbody, Th } from "@/components/ui/Table";
import { useAdminImport } from "@/hooks/admin";

const TYPE_LABELS: Record<string, string> = {
	carreras: "Carreras",
	materias: "Materias",
	planes_de_estudio: "Planes de estudio",
	correlativas: "Correlativas",
	alumnos: "Alumnos",
	historial_cursadas: "Historial de cursadas",
	inscripciones: "Inscripciones",
};

export function ImportPlanillas() {
	const { uploading, results, errors, handleUpload, handleClear } =
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
				{(results.length > 0 || errors.length > 0) && (
					<button
						type="button"
						onClick={handleClear}
						disabled={uploading}
						className="text-sm text-zinc-500 underline hover:text-zinc-700 disabled:opacity-50"
					>
						Limpiar historial
					</button>
				)}
			</form>

			{results.length > 0 && (
				<div className="mb-4">
					<Table>
						<thead className="bg-zinc-50">
							<tr>
								<Th>Tipo</Th>
								<Th>Archivos</Th>
								<Th>Procesados</Th>
								<Th>Omitidos</Th>
							</tr>
						</thead>
						<Tbody>
							{results.map((r) => (
								<tr key={r.id} className="bg-white">
									<td className="px-4 py-3 text-zinc-800">
										{TYPE_LABELS[r.type] ?? r.type}
									</td>
									<td className="px-4 py-3 text-zinc-600">
										{r.files.join(", ")}
									</td>
									<td className="px-4 py-3 text-right text-zinc-700">
										{r.processed}
									</td>
									<td className="px-4 py-3 text-right text-zinc-700">
										{r.skipped}
									</td>
								</tr>
							))}
						</Tbody>
					</Table>
				</div>
			)}

			{errors.length > 0 && (
				<div className="rounded-lg border border-red-200 bg-red-50 p-4">
					<h3 className="mb-2 text-sm font-medium text-red-700">
						Errores ({errors.length})
					</h3>
					<ul className="space-y-1 text-sm text-red-700">
						{errors.map((e) => (
							<li key={e.id}>
								<span className="font-medium">{e.file}</span> — {e.error}
							</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
}
