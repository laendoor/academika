"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { login } from "@/lib/api/auth";

export function useLoginForm() {
	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);
	const router = useRouter();

	async function handleAction(formData: FormData) {
		setPending(true);
		setError(undefined);

		const result = await login(
			formData.get("email") as string,
			formData.get("password") as string,
		);

		if (result.ok) {
			router.push("/");
			return;
		}

		setError(result.error);
		setPending(false);
	}

	return { handleAction, error, pending };
}
