import { type ApiResult, get } from "./client";

export interface LookupOption {
	key: string;
	label: string;
}

export function getUserRoles(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/user-roles");
}

export function getEstadosAcademicos(): Promise<ApiResult<LookupOption[]>> {
	return get<LookupOption[]>("/api/lookups/estado-academico");
}
