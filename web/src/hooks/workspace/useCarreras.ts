"use client";
import { usePagination } from "@/hooks/workspace/usePagination";
import * as workspace from "@/lib/api/workspace";

interface UseCarrerasOptions {
	skip?: number;
	limit?: number;
}

export function useCarreras({ skip = 0, limit = 20 }: UseCarrerasOptions = {}) {
	return usePagination(workspace.getCarreras, { skip, limit });
}
