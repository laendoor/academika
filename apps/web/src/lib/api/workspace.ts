import { type ApiResult, get } from "./client";

export interface CarreraInfo {
	plan_id: string;
	plan_nombre: string;
	anio: number;
	vigente: boolean;
	carrera_id: string;
	carrera_nombre: string;
	estado_academico: string;
	fecha_ingreso: string | null;
}

export interface EstudianteRow {
	id: string;
	nombre: string;
	apellido: string;
	dni: string;
	legajo: string | null;
	carreras: CarreraInfo[];
}

export interface EstudiantesResponse {
	total: number;
	items: EstudianteRow[];
}

export interface CarreraOption {
	id: string;
	nombre: string;
	codigo: string;
}

export function getCarreras(
	skip = 0,
	limit = 20,
): Promise<ApiResult<{ total: number; items: CarreraOption[] }>> {
	const params = new URLSearchParams({
		skip: String(skip),
		limit: String(limit),
	});
	return get(`/api/carreras?${params}`);
}

export interface PlanInfo {
	plan_id: string;
	plan_nombre: string;
	anio: number;
	vigente: boolean;
	carrera_id: string;
	carrera_nombre: string;
}

export interface MateriaRow {
	id: string;
	nombre: string;
	codigo: string;
	sigla: string | null;
	creditos: number | null;
	plan_vigente: PlanInfo | null;
	planes: PlanInfo[];
}

export interface MateriasResponse {
	total: number;
	items: MateriaRow[];
}

export function getMaterias(
	skip = 0,
	limit = 20,
): Promise<ApiResult<MateriasResponse>> {
	return get<MateriasResponse>(
		`/api/workspace/materias?skip=${skip}&limit=${limit}`,
	);
}

export function getEstudiantes(
	skip = 0,
	limit = 20,
	carrera_id?: string,
	estado_academico?: string,
): Promise<ApiResult<EstudiantesResponse>> {
	const params = new URLSearchParams({
		skip: String(skip),
		limit: String(limit),
	});
	if (carrera_id) params.set("carrera_id", carrera_id);
	if (estado_academico) params.set("estado_academico", estado_academico);
	return get<EstudiantesResponse>(`/api/workspace/estudiantes?${params}`);
}

export interface CorrelativaRef {
	id: string;
	codigo: string;
	nombre: string;
}

export interface CorrelativaRow {
	materia: CorrelativaRef;
	requisito: CorrelativaRef;
	es_obligatoria: boolean;
}

export interface CorrelativasResponse {
	total: number;
	items: CorrelativaRow[];
}

export function getCorrelativas(
	skip = 0,
	limit = 20,
	materia_id?: string,
): Promise<ApiResult<CorrelativasResponse>> {
	const params = new URLSearchParams({
		skip: String(skip),
		limit: String(limit),
	});
	if (materia_id) params.set("materia_id", materia_id);
	return get<CorrelativasResponse>(`/api/correlativas?${params}`);
}

export interface PlanRow {
	id: string;
	carrera_id: string;
	carrera_nombre: string;
	nombre: string;
	nivel: string | null;
	anio: number;
	vigente: boolean;
}

export interface PlanesResponse {
	total: number;
	items: PlanRow[];
}

export function getPlanes(
	skip = 0,
	limit = 20,
	carrera_id?: string,
): Promise<ApiResult<PlanesResponse>> {
	const params = new URLSearchParams({
		skip: String(skip),
		limit: String(limit),
	});
	if (carrera_id) params.set("carrera_id", carrera_id);
	return get<PlanesResponse>(`/api/planes?${params}`);
}

export interface MateriaEnPlan {
	id: string;
	codigo: string;
	sigla: string | null;
	nombre: string;
	creditos: number | null;
	nucleo: string | null;
	horas_semanales: number | null;
	carga_horaria_total: number | null;
}

export interface PlanDetail {
	id: string;
	carrera_id: string;
	carrera_nombre: string;
	nombre: string;
	nivel: string | null;
	anio: number;
	vigente: boolean;
	materias: MateriaEnPlan[];
}

export function getPlanDetail(id: string): Promise<ApiResult<PlanDetail>> {
	return get<PlanDetail>(`/api/planes/${encodeURIComponent(id)}`);
}

export interface CursadaRow {
	id: string;
	alumno: {
		id: string;
		nombre: string;
		apellido: string;
		legajo: string | null;
	};
	materia: { id: string; codigo: string; nombre: string };
	carrera: { id: string; codigo: string; nombre: string };
	anio: number;
	cuatrimestre: string;
	comision: string | null;
	tipo_cursada: string;
	estado_cursada: string;
	nota: string | null;
}

export interface CursadasResponse {
	total: number;
	items: CursadaRow[];
}

export interface CursadasFilters {
	carrera_id?: string;
	alumno?: string;
	materia?: string;
	anio?: number;
	cuatrimestre?: string;
	estado_cursada?: string[];
	tipo_cursada?: string;
}

export function getCursadas(
	skip = 0,
	limit = 20,
	filters: CursadasFilters = {},
): Promise<ApiResult<CursadasResponse>> {
	const params = new URLSearchParams({
		skip: String(skip),
		limit: String(limit),
	});
	for (const key of [
		"carrera_id",
		"alumno",
		"materia",
		"anio",
		"cuatrimestre",
		"tipo_cursada",
	] as const) {
		const value = filters[key];
		if (value !== undefined && value !== "") params.set(key, String(value));
	}
	for (const estado of filters.estado_cursada ?? []) {
		params.append("estado_cursada", estado);
	}
	return get<CursadasResponse>(`/api/workspace/cursadas?${params}`);
}

export interface EstudianteDetalle {
	id: string;
	nombre: string;
	apellido: string;
	dni: string;
	legajo: string | null;
	carreras: CarreraInfo[];
	cursadas: CursadaRow[];
}

export function getEstudianteDetalle(
	id: string,
): Promise<ApiResult<EstudianteDetalle>> {
	return get<EstudianteDetalle>(
		`/api/workspace/estudiantes/${encodeURIComponent(id)}`,
	);
}
