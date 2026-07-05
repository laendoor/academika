const UNEXPECTED_ERROR = "Error inesperado. Intentá de nuevo más tarde.";

export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: string };

async function request<T>(
	method: string,
	path: string,
	body?: unknown,
): Promise<ApiResult<T>> {
	try {
		const res = await fetch(path, {
			method,
			...(body !== undefined && {
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(body),
			}),
		});

		if (res.ok) {
			return { ok: true, data: (await res.json()) as T };
		}

		const json = await res.json().catch(() => ({}));
		return {
			ok: false,
			error: (json as { error?: string }).error ?? UNEXPECTED_ERROR,
		};
	} catch {
		return { ok: false, error: UNEXPECTED_ERROR };
	}
}

export function get<T>(path: string): Promise<ApiResult<T>> {
	return request("GET", path);
}

export function post<T>(path: string, body: unknown): Promise<ApiResult<T>> {
	return request("POST", path, body);
}

export function put<T>(path: string, body: unknown): Promise<ApiResult<T>> {
	return request("PUT", path, body);
}
