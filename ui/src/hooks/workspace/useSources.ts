"use client";
import { useCallback, useEffect, useRef, useState } from "react";

import * as sources from "@/lib/api/sources";

interface UseSourcesOptions {
	skip?: number;
	limit?: number;
	autoRefresh?: boolean;
}

export function useSources({
	skip = 0,
	limit = 20,
	autoRefresh = false,
}: UseSourcesOptions = {}) {
	const [items, setItems] = useState<sources.SourceItem[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();
	const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

	const refresh = useCallback(async () => {
		const result = await sources.getSources(skip, limit);
		if (result.ok) {
			setItems(result.data.items);
			setTotal(result.data.total);
			setError(undefined);
		} else {
			setError(result.error);
		}
		setLoading(false);
	}, [skip, limit]);

	useEffect(() => {
		refresh();
	}, [refresh]);

	useEffect(() => {
		if (autoRefresh) {
			timerRef.current = setInterval(refresh, 2500);
			return () => {
				if (timerRef.current) clearInterval(timerRef.current);
			};
		}
	}, [autoRefresh, refresh]);

	return { items, total, loading, error, refresh };
}
