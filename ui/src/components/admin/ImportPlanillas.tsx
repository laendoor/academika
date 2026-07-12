"use client";
import { useRef, useState } from "react";

import { SourcesTable } from "@/components/workspace/SourcesTable";
import { useAdminImport } from "@/hooks/admin";

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

			<SourcesTable items={items} />

			{total === 0 && !loading && (
				<p className="mt-4 text-sm text-zinc-500">
					Sin importaciones registradas todavía.
				</p>
			)}
		</div>
	);
}
