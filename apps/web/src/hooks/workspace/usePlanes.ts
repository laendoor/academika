"use client";
import { useCallback } from "react";

import { usePagination } from "@/hooks/workspace/usePagination";
import * as workspace from "@/lib/api/workspace";

interface UsePlanesOptions {
	skip?: number;
	limit?: number;
	carrera_id?: string;
}

export function usePlanes({
	skip = 0,
	limit = 20,
	carrera_id,
}: UsePlanesOptions = {}) {
	const fetcher = useCallback(
		(s: number, l: number) => workspace.getPlanes(s, l, carrera_id),
		[carrera_id],
	);

	return usePagination(fetcher, { skip, limit });
}
