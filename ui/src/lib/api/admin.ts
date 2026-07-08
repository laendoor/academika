import { type ApiResult, get, postFormData, put } from "./client";

export type UserRole = "admin" | "director" | "docente";

export interface UserItem {
	id: string;
	email: string;
	role: UserRole;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

export interface UsersResponse {
	total: number;
	items: UserItem[];
}

export interface UserUpdate {
	role?: UserRole;
	is_active?: boolean;
}

export interface ImportResult {
	type: string;
	files: string[];
	processed: number;
	skipped: number;
}

export interface ImportFailure {
	file: string;
	error: string;
}

export interface ImportResponse {
	results: ImportResult[];
	errors: ImportFailure[];
}

export function getUsers(): Promise<ApiResult<UsersResponse>> {
	return get<UsersResponse>("/api/admin/users");
}

export function updateUser(
	id: string,
	data: UserUpdate,
): Promise<ApiResult<UserItem>> {
	return put<UserItem>(`/api/admin/users/${id}`, data);
}

export function uploadGuaraniSheets(
	files: File[],
): Promise<ApiResult<ImportResponse>> {
	const formData = new FormData();
	for (const file of files) {
		formData.append("files", file);
	}
	return postFormData<ImportResponse>("/api/admin/import-guarani", formData);
}
