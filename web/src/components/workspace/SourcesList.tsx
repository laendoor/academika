"use client";
import { useState } from "react";

import { SourcesTable } from "@/components/workspace/SourcesTable";
import { Pagination } from "@/components/ui/Pagination";
import { useSources } from "@/hooks/workspace";

const PAGE_SIZE = 20;

export function SourcesList() {
	const [skip, setSkip] = useState(0);
	const { items, total, loading, error, refresh } = useSources({
		skip,
		limit: PAGE_SIZE,
	});

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
