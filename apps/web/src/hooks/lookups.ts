"use client";
import { useEffect, useState } from "react";

import type { ApiResult } from "@/lib/api/client";
import type { LookupOption } from "@/lib/api/lookups";
import * as lookups from "@/lib/api/lookups";

export function useUserRoles() {
	const { data, loading, error } = useLookup(lookups.getUserRoles);

	return { roles: data, loading, error };
}

export function useNivelesCarrera() {
	const { data, loading, error } = useLookup(lookups.getNivelesCarrera);

	return { niveles: data, loading, error };
}

export function useNucleosCarrera() {
	const { data, loading, error } = useLookup(lookups.getNucleosCarrera);

	return { nucleos: data, loading, error };
}

export function useEstadosAcademicos() {
	const { data, loading, error } = useLookup(lookups.getEstadosAcademicos);

	return { estados: data, loading, error };
}

export function useEstadosCursada() {
	const { data, loading, error } = useLookup(lookups.getEstadosCursada);

	return { estados: data, loading, error };
}

export function useTiposCursada() {
	const { data, loading, error } = useLookup(lookups.getTiposCursada);

	return { tipos: data, loading, error };
}

function useLookup(fetch: () => Promise<ApiResult<LookupOption[]>>) {
	const [data, setData] = useState<LookupOption[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();

	useEffect(() => {
		fetch().then((result) => {
			setLoading(false);
			if (result.ok) setData(result.data);
			else setError(result.error);
		});
	}, [fetch]);

	return { data, loading, error };
}
