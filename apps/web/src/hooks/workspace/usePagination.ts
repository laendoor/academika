"use client";
import { useCallback, useEffect, useState } from "react";

import type { ApiResult } from "@/lib/api/client";

interface UsePaginationResult<T> {
	items: T[];
	total: number;
	loading: boolean;
	error: string | undefined;
	refresh: () => void;
}

export function usePagination<T>(
	fetcher: (
		skip: number,
		limit: number,
	) => Promise<ApiResult<{ total: number; items: T[] }>>,
	{ skip, limit }: { skip: number; limit: number },
): UsePaginationResult<T> {
	const [items, setItems] = useState<T[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();

	const refresh = useCallback(async () => {
		setLoading(true);
		const result = await fetcher(skip, limit);
		if (result.ok) {
			setItems(result.data.items);
			setTotal(result.data.total);
			setError(undefined);
		} else {
			setError(result.error);
		}
		setLoading(false);
	}, [fetcher, skip, limit]);

	useEffect(() => {
		refresh();
	}, [refresh]);

	return { items, total, loading, error, refresh };
}
