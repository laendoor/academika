import { type ApiResult, get } from "./client";

export interface SearchHit {
	id: string;
	label: string;
	/** Lo que se escribe en el filtro para que la búsqueda devuelva filas. */
	term: string;
}

export function searchAlumnos(q: string): Promise<ApiResult<SearchHit[]>> {
	return get(`/api/alumnos/search?q=${encodeURIComponent(q)}`);
}

export function searchMaterias(q: string): Promise<ApiResult<SearchHit[]>> {
	return get(`/api/materias/search?q=${encodeURIComponent(q)}`);
}
