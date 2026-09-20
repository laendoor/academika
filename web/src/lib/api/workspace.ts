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
}

export interface EstadoOption {
	key: string;
	nombre: string;
}

export function getCarreras(): Promise<
	ApiResult<{ total: number; items: CarreraOption[] }>
> {
	return get("/api/carreras");
}

export function getEstadosAcademicos(): Promise<ApiResult<EstadoOption[]>> {
	return get("/api/lookups/estado-academico");
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
