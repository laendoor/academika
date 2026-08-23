export const API_URL = process.env.API_URL ?? "http://localhost:8000";
export const IS_PRODUCTION = process.env.NODE_ENV === "production";
export const ADMIN_ROLE = "admin";

export function buildWsUrl(location: {
	protocol: string;
	host: string;
}): string {
	const protocol = location.protocol === "https:" ? "wss:" : "ws:";
	return `${protocol}//${location.host}/ws`;
}

export const WS_URL =
	process.env.NEXT_PUBLIC_WS_URL ??
	(typeof window === "undefined" ? "" : buildWsUrl(window.location));

export const SHEET_TYPE_LABELS: Record<string, string> = {
	carreras: "Carreras",
	materias: "Materias",
	planes_de_estudio: "Planes de estudio",
	correlativas: "Correlativas",
	alumnos: "Alumnos",
	historial_cursadas: "Historial de cursadas",
	inscripciones: "Inscripciones",
};
