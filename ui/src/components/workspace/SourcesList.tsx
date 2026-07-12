"use client";
import { useState } from "react";

import { SourcesTable } from "@/components/workspace/SourcesTable";
import { useSources } from "@/hooks/workspace";

const PAGE_SIZE = 20;

export function SourcesList() {
	const [skip, setSkip] = useState(0);
	const { items, total, loading, error, refresh } = useSources({
		skip,
		limit: PAGE_SIZE,
		autoRefresh: false,
	});

	const hasNext = skip + PAGE_SIZE < total;
	const hasPrev = skip > 0;

	return (
		<div>
			<div className="mb-4 flex items-center justify-between">
				<h2 className="text-lg font-medium text-zinc-800">
					Planillas importadas
				</h2>
				<button
					type="button"
					onClick={refresh}
					disabled={loading}
					className="text-sm text-zinc-500 underline hover:text-zinc-700 disabled:opacity-50"
				>
					Refrescar
				</button>
			</div>

			{error && (
				<div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			)}

			<SourcesTable items={items} />

			{total === 0 && !loading && (
				<p className="mt-4 text-sm text-zinc-500">
					Sin planillas importadas todavía.
				</p>
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
