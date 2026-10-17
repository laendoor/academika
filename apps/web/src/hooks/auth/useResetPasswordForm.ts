"use client";
import { resetPassword } from "@/lib/api/auth";

import { useFormWithRedirect } from "./useFormWithRedirect";

export function useResetPasswordForm(token: string) {
	return useFormWithRedirect(
		(fd) => resetPassword(token, fd.get("new_password") as string),
		"/login",
	);
}
