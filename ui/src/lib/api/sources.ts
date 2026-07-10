import { type ApiResult, get } from "./client";

export interface ImportGuaraniDetails {
	sheet_type: string | null;
	files: string[];
	processed: number;
	skipped: number;
	error: string | null;
}

export interface SourceItem {
	id: string;
	created_at: string;
	status: "ok" | "processing" | "error";
	details: ImportGuaraniDetails;
}

export interface SourcesResponse {
	total: number;
	items: SourceItem[];
}

export function getSources(
	skip = 0,
	limit = 20,
): Promise<ApiResult<SourcesResponse>> {
	return get<SourcesResponse>(`/api/sources?skip=${skip}&limit=${limit}`);
}
