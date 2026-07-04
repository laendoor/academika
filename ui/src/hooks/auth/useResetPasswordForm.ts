"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { resetPassword } from "@/lib/api/auth";

export function useResetPasswordForm(token: string) {
	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);
	const router = useRouter();

	async function handleAction(formData: FormData) {
		setPending(true);
		setError(undefined);

		const result = await resetPassword(
			token,
			formData.get("new_password") as string,
		);

		if (result.ok) {
			router.push("/login");
			return;
		}

		setError(result.error);
		setPending(false);
	}

	return { handleAction, error, pending };
}
