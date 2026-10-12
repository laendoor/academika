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

export function useNivelesCarrera() {
	const [niveles, setNiveles] = useState<LookupOption[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();

	useEffect(() => {
		lookups.getNivelesCarrera().then((result) => {
			setLoading(false);
			if (result.ok) setNiveles(result.data);
			else setError(result.error);
		});
	}, []);

	return { niveles, loading, error };
}

export function useNucleosCarrera() {
	const [nucleos, setNucleos] = useState<LookupOption[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();

	useEffect(() => {
		lookups.getNucleosCarrera().then((result) => {
			setLoading(false);
			if (result.ok) setNucleos(result.data);
			else setError(result.error);
		});
	}, []);

	return { nucleos, loading, error };
}
