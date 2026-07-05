export const API_URL = process.env.API_URL ?? "http://localhost:8000";
export const IS_PRODUCTION = process.env.NODE_ENV === "production";
export const JWT_SECRET_KEY =
	process.env.JWT_SECRET_KEY ?? "dev-secret-key-change-in-production";
