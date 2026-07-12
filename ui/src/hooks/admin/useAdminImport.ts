"use client";
import { useEffect, useState } from "react";

import { useSources } from "@/hooks/workspace";
import * as admin from "@/lib/api/admin";

const LIMIT = 15;
const MAX_POLL_TICKS = 20;

export function useAdminImport() {
	const [uploading, setUploading] = useState(false);
	const [expectedTarget, setExpectedTarget] = useState<number | null>(null);
	const [pollTicks, setPollTicks] = useState(0);
	const { items, total, loading, error, refresh } = useSources({
		limit: LIMIT,
		autoRefresh: uploading,
	});

	// Auto-stop: si el total llegó al expected, terminamos el upload.
	// Fallback: si pasamos MAX_POLL_TICKS refreshes sin llegar, abortamos igual.
	useEffect(() => {
		if (!uploading) return;
		if (expectedTarget !== null && total >= expectedTarget) {
			setUploading(false);
			setExpectedTarget(null);
			setPollTicks(0);
		} else {
			setPollTicks((t) => t + 1);
		}
	}, [total, uploading, expectedTarget]);

	useEffect(() => {
		if (pollTicks >= MAX_POLL_TICKS) {
			setUploading(false);
			setExpectedTarget(null);
			setPollTicks(0);
		}
	}, [pollTicks]);

	async function handleUpload(files: File[]) {
		if (!files.length) return;
		const baselineTotal = total;
		setUploading(true);
		setPollTicks(0);
		const result = await admin.uploadGuaraniSheets(files);
		if (result.ok) {
			setExpectedTarget(baselineTotal + result.data.count);
		} else {
			setUploading(false);
		}
	}

	return { uploading, items, total, loading, error, handleUpload, refresh };
}
