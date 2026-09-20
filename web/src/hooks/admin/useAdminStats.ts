"use client";
import { useEffect, useState } from "react";

import * as workspace from "@/lib/api/workspace";

type Status = "loading" | "error" | "ok";

export function useAdminStats() {
	const [estudiantes, setEstudiantes] = useState<number | null>(null);
	const [materias, setMaterias] = useState<number | null>(null);
	const [status, setStatus] = useState<Status>("loading");

	useEffect(() => {
		Promise.all([workspace.getEstudiantes(0, 1), workspace.getMaterias(0, 1)])
			.then(([estR, matR]) => {
				if (estR.ok) setEstudiantes(estR.data.total);
				if (matR.ok) setMaterias(matR.data.total);
				setStatus(estR.ok && matR.ok ? "ok" : "error");
			})
			.catch(() => setStatus("error"));
	}, []);

	return { estudiantes, materias, status };
}
