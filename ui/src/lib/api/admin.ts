import { type ApiResult, get, put } from "./client";

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

export function getUsers(): Promise<ApiResult<UsersResponse>> {
	return get<UsersResponse>("/api/admin/users");
}

export function updateUser(
	id: string,
	data: UserUpdate,
): Promise<ApiResult<UserItem>> {
	return put<UserItem>(`/api/admin/users/${id}`, data);
}
