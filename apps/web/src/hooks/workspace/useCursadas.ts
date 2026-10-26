"use client";
import { useCallback } from "react";

import { usePagination } from "@/hooks/workspace/usePagination";
import type { ApiResult } from "@/lib/api/client";
import type { CursadasResponse } from "@/lib/api/workspace";
import * as workspace from "@/lib/api/workspace";

interface UseCursadasOptions {
	skip?: number;
	limit?: number;
	carrera_id?: string;
	alumno?: string;
	materia?: string;
	anio?: number;
	cuatrimestre?: string;
	estado_cursada?: string[];
	tipo_cursada?: string;
	/** false mientras falten datos para armar los filtros; evita un request que se descarta. */
	ready?: boolean;
}

const EMPTY_PAGE: ApiResult<CursadasResponse> = {
	ok: true,
	data: { total: 0, items: [] },
};

export function useCursadas({
	skip = 0,
	limit = 20,
	carrera_id,
	alumno,
	materia,
	anio,
	cuatrimestre,
	estado_cursada,
	tipo_cursada,
	ready = true,
}: UseCursadasOptions = {}) {
	// El array no puede ir en las deps: cambia de identidad en cada render y
	// dispararía un fetch por render. La clave estable sí.
	const estadosKey = (estado_cursada ?? []).join(",");

	const fetcher = useCallback(
		(s: number, l: number) =>
			ready
				? workspace.getCursadas(s, l, {
						carrera_id,
						alumno,
						materia,
						anio,
						cuatrimestre,
						tipo_cursada,
						estado_cursada: estadosKey ? estadosKey.split(",") : undefined,
					})
				: Promise.resolve(EMPTY_PAGE),
		[
			carrera_id,
			alumno,
			materia,
			anio,
			cuatrimestre,
			estadosKey,
			tipo_cursada,
			ready,
		],
	);

	const { items, total, loading, error, refresh } = usePagination(fetcher, {
		skip,
		limit,
	});

	return { items, total, loading: loading || !ready, error, refresh };
}
