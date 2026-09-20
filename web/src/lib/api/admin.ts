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

export interface ImportAcceptedResponse {
	status: "processing";
	count: number;
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
): Promise<ApiResult<ImportAcceptedResponse>> {
	const formData = new FormData();
	for (const file of files) {
		formData.append("files", file);
	}
	return postFormData<ImportAcceptedResponse>(
		"/api/admin/import-guarani",
		formData,
	);
}
