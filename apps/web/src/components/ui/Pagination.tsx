"use client";

interface PaginationProps {
	skip: number;
	total: number;
	pageSize: number;
	loading: boolean;
	onChange: (skip: number) => void;
}

export function Pagination({
	skip,
	total,
	pageSize,
	loading,
	onChange,
}: PaginationProps) {
	const hasNext = skip + pageSize < total;
	const hasPrev = skip > 0;

	if (!hasPrev && !hasNext) return null;

	return (
		<div className="mt-4 flex justify-between">
			<button
				type="button"
				onClick={() => onChange(Math.max(0, skip - pageSize))}
				disabled={!hasPrev || loading}
				className="rounded border border-sage-200 px-3 py-1 text-sm text-sage-800 hover:bg-sage-50 disabled:opacity-50"
			>
				Anterior
			</button>
			<span className="text-sm text-sage-700">
				{skip + 1}-{Math.min(skip + pageSize, total)} de {total}
			</span>
			<button
				type="button"
				onClick={() => onChange(skip + pageSize)}
				disabled={!hasNext || loading}
				className="rounded border border-sage-200 px-3 py-1 text-sm text-sage-800 hover:bg-sage-50 disabled:opacity-50"
			>
				Siguiente
			</button>
		</div>
	);
}
