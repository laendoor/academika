"use client";
import { useCallback } from "react";

import { usePagination } from "@/hooks/workspace/usePagination";
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
}

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
}: UseCursadasOptions = {}) {
	// El array no puede ir en las deps: cambia de identidad en cada render y
	// dispararía un fetch por render. La clave estable sí.
	const estadosKey = (estado_cursada ?? []).join(",");

	const fetcher = useCallback(
		(s: number, l: number) =>
			workspace.getCursadas(s, l, {
				carrera_id,
				alumno,
				materia,
				anio,
				cuatrimestre,
				tipo_cursada,
				estado_cursada: estadosKey ? estadosKey.split(",") : undefined,
			}),
		[carrera_id, alumno, materia, anio, cuatrimestre, estadosKey, tipo_cursada],
	);

	return usePagination(fetcher, { skip, limit });
}
