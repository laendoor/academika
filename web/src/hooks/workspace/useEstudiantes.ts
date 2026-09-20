"use client";
import { useCallback } from "react";

import { usePagination } from "@/hooks/workspace/usePagination";
import * as workspace from "@/lib/api/workspace";

interface UseEstudiantesOptions {
	skip?: number;
	limit?: number;
	carrera_id?: string;
	estado_academico?: string;
}

export function useEstudiantes({
	skip = 0,
	limit = 20,
	carrera_id,
	estado_academico,
}: UseEstudiantesOptions = {}) {
	const fetcher = useCallback(
		(s: number, l: number) =>
			workspace.getEstudiantes(s, l, carrera_id, estado_academico),
		[carrera_id, estado_academico],
	);

	return usePagination(fetcher, { skip, limit });
}
