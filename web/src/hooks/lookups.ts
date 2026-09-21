"use client";
import { useEffect, useState } from "react";

import type { LookupOption } from "@/lib/api/lookups";
import * as lookups from "@/lib/api/lookups";

export function useUserRoles() {
	const [roles, setRoles] = useState<LookupOption[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();

	useEffect(() => {
		lookups.getUserRoles().then((result) => {
			setLoading(false);
			if (result.ok) setRoles(result.data);
			else setError(result.error);
		});
	}, []);

	return { roles, loading, error };
}
