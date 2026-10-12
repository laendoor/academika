"use client";
import { useCallback } from "react";

import { usePagination } from "@/hooks/workspace/usePagination";
import * as workspace from "@/lib/api/workspace";

interface UseCorrelativasOptions {
	skip?: number;
	limit?: number;
	materia_id?: string;
}

export function useCorrelativas({
	skip = 0,
	limit = 20,
	materia_id,
}: UseCorrelativasOptions = {}) {
	const fetcher = useCallback(
		(s: number, l: number) => workspace.getCorrelativas(s, l, materia_id),
		[materia_id],
	);

	return usePagination(fetcher, { skip, limit });
}
