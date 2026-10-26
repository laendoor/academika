"use client";
import { useEffect, useRef, useState } from "react";

import type { EstudianteDetalle } from "@/lib/api/workspace";
import * as workspace from "@/lib/api/workspace";

export function useEstudianteDetalle(alumnoId: string) {
	const [detail, setDetail] = useState<EstudianteDetalle | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>(undefined);
	const requestId = useRef(0);

	useEffect(() => {
		const id = ++requestId.current;
		setLoading(true);
		setError(undefined);
		workspace.getEstudianteDetalle(alumnoId).then((r) => {
			if (requestId.current !== id) return;
			setLoading(false);
			if (r.ok) setDetail(r.data);
			else setError(r.error);
		});
	}, [alumnoId]);

	return { detail, loading, error };
}
