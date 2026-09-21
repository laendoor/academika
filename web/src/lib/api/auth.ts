import { type ApiResult, type OkResponse, post } from "./client";

export function login(
	email: string,
	password: string,
): Promise<ApiResult<OkResponse>> {
	return post("/api/auth/login", { email, password });
}

export function forgotPassword(
	email: string,
): Promise<ApiResult<{ sent: true }>> {
	return post("/api/auth/forgot-password", { email });
}

export function resetPassword(
	token: string,
	newPassword: string,
): Promise<ApiResult<OkResponse>> {
	return post("/api/auth/reset-password", { token, new_password: newPassword });
}

export function register(
	token: string,
	password: string,
): Promise<ApiResult<OkResponse>> {
	return post("/api/auth/register", { token, password });
}
