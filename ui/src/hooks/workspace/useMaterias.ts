"use client";
import { usePagination } from "@/hooks/workspace/usePagination";
import * as workspace from "@/lib/api/workspace";

interface UseMateriasOptions {
	skip?: number;
	limit?: number;
}

export function useMaterias({ skip = 0, limit = 20 }: UseMateriasOptions = {}) {
	return usePagination(workspace.getMaterias, { skip, limit });
}
