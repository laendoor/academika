"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { register } from "@/lib/api/auth";

export function useRegisterForm(token: string) {
	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);
	const router = useRouter();

	async function handleAction(formData: FormData) {
		setError(undefined);

		const password = formData.get("password") as string;
		const confirmPassword = formData.get("confirm_password") as string;

		if (password !== confirmPassword) {
			setError("Las contraseñas no coinciden.");
			return;
		}

		setPending(true);
		const result = await register(token, password);

		if (result.ok) {
			router.push("/login");
			setPending(false);
			return;
		}

		setError(result.error);
		setPending(false);
	}

	return { handleAction, error, pending };
}
