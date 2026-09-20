"use client";
import { useState } from "react";

import { forgotPassword } from "@/lib/api/auth";

export function useForgotPasswordForm() {
	const [sent, setSent] = useState(false);
	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);

	async function handleAction(formData: FormData) {
		setPending(true);
		setError(undefined);

		const result = await forgotPassword(formData.get("email") as string);

		if (result.ok) {
			setSent(true);
			setPending(false);
			return;
		}

		setError(result.error);
		setPending(false);
	}

	return { handleAction, error, pending, sent };
}
