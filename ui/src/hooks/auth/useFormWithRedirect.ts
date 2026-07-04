"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

import type { ApiResult } from "@/lib/api/client";

export function useFormWithRedirect(
	action: (fd: FormData) => Promise<ApiResult<unknown>>,
	redirectTo: string,
) {
	const [error, setError] = useState<string | undefined>();
	const [pending, setPending] = useState(false);
	const router = useRouter();

	async function handleAction(fd: FormData) {
		setPending(true);
		setError(undefined);
		const result = await action(fd);
		setPending(false);
		if (result.ok) {
			router.push(redirectTo);
			return;
		}
		setError(result.error);
	}

	return { handleAction, error, pending };
}
