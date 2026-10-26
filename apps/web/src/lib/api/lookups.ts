import { type ApiResult, get } from "./client";

export interface LookupOption {
	key: string;
	label: string;
}

export function toLabels(options: LookupOption[]): Record<string, string> {
	return Object.fromEntries(options.map((o) => [o.key, o.label]));
}

export function getUserRoles(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/user-roles");
}

export function getEstadosAcademicos(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/estado-academico");
}

export function getNivelesCarrera(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/nivel-carrera");
}

export function getNucleosCarrera(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/nucleo-carrera");
}

export function getEstadosCursada(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/estado-cursada");
}

export function getTiposCursada(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/tipo-cursada");
}
