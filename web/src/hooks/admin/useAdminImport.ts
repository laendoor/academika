"use client";
import { useEffect, useRef, useState } from "react";

import { useSources } from "@/hooks/workspace";
import * as admin from "@/lib/api/admin";

const LIMIT = 15;

export function useAdminImport() {
	const [uploading, setUploading] = useState(false);
	const [expectedTarget, setExpectedTarget] = useState<number | null>(null);
	const baselineRef = useRef(0);
	const { items, total, loading, error, refresh, wsEventCount } = useSources({
		limit: LIMIT,
	});

	useEffect(() => {
		if (
			uploading &&
			expectedTarget !== null &&
			wsEventCount - baselineRef.current >= expectedTarget
		) {
			setUploading(false);
			setExpectedTarget(null);
		}
	}, [wsEventCount, uploading, expectedTarget]);

	async function handleUpload(files: File[]) {
		if (!files.length) return;
		baselineRef.current = wsEventCount;
		setUploading(true);
		const result = await admin.uploadGuaraniSheets(files);
		if (result.ok) {
			setExpectedTarget(result.data.count);
		} else {
			setUploading(false);
		}
	}

	return { uploading, items, total, loading, error, handleUpload, refresh };
}
