export const API_URL = process.env.API_URL ?? "http://localhost:8000";
export const WS_URL = process.env.WS_URL ?? "ws://localhost:8000/ws";
export const IS_PRODUCTION = process.env.NODE_ENV === "production";
export const ADMIN_ROLE = "admin";

export const SHEET_TYPE_LABELS: Record<string, string> = {
	carreras: "Carreras",
	materias: "Materias",
	planes_de_estudio: "Planes de estudio",
	correlativas: "Correlativas",
	alumnos: "Alumnos",
	historial_cursadas: "Historial de cursadas",
	inscripciones: "Inscripciones",
};
