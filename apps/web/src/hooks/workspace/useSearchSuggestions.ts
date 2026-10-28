"use client";
import { useEffect, useState } from "react";

import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import type { ApiResult } from "@/lib/api/client";
import type { SearchHit } from "@/lib/api/search";

const NO_HITS: SearchHit[] = [];

/** Sugerencias del backend para el autocompletado; un fallo se ve como lista vacía. */
export function useSearchSuggestions(
	search: (q: string) => Promise<ApiResult<SearchHit[]>>,
	term: string,
): SearchHit[] {
	const debounced = useDebouncedValue(term);
	const [hits, setHits] = useState<SearchHit[]>(NO_HITS);

	useEffect(() => {
		const q = debounced.trim();
		if (q.length < 2) {
			setHits(NO_HITS);
			return;
		}
		let active = true;
		search(q).then((result) => {
			if (active) setHits(result.ok ? result.data : NO_HITS);
		});
		return () => {
			active = false;
		};
	}, [debounced, search]);

	return hits;
}
