"use client";
import { useState } from "react";
import { useSources } from "@/hooks/workspace";
import * as admin from "@/lib/api/admin";

const LIMIT = 15;

export function useAdminImport() {
	const [uploading, setUploading] = useState(false);
	const [expectedTarget, setExpectedTarget] = useState<number | null>(null);
	const { items, total, loading, error, refresh } = useSources({
		limit: LIMIT,
		autoRefresh: uploading,
	});

	// Auto-stop: si el total llegó al expected, terminamos el upload.
	// Se ejecuta durante render pero solo acciona si uploading y target se cumplen.
	if (uploading && expectedTarget !== null && total >= expectedTarget) {
		setUploading(false);
		setExpectedTarget(null);
	}

	async function handleUpload(files: File[]) {
		if (!files.length) return;
		const baselineTotal = total;
		setUploading(true);
		const result = await admin.uploadGuaraniSheets(files);
		if (result.ok) {
			setExpectedTarget(baselineTotal + result.data.count);
		} else {
			setUploading(false);
		}
	}

	return { uploading, items, total, loading, error, handleUpload, refresh };
}
