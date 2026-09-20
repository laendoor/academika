"use client";
import { login } from "@/lib/api/auth";

import { useFormWithRedirect } from "./useFormWithRedirect";

export function useLoginForm() {
	return useFormWithRedirect(
		(fd) => login(fd.get("email") as string, fd.get("password") as string),
		"/",
	);
}
