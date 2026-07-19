"use client";
import { useCallback, useEffect, useState } from "react";

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
	const [items, setItems] = useState<workspace.EstudianteRow[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();

	const refresh = useCallback(async () => {
		setLoading(true);
		const result = await workspace.getEstudiantes(
			skip,
			limit,
			carrera_id,
			estado_academico,
		);
		if (result.ok) {
			setItems(result.data.items);
			setTotal(result.data.total);
			setError(undefined);
		} else {
			setError(result.error);
		}
		setLoading(false);
	}, [skip, limit, carrera_id, estado_academico]);

	useEffect(() => {
		refresh();
	}, [refresh]);

	return { items, total, loading, error, refresh };
}
