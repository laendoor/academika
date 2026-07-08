"use client";
import { useRef, useState } from "react";

import * as admin from "@/lib/api/admin";

type ResultRow = admin.ImportResult & { id: number };
type ErrorRow = admin.ImportFailure & { id: number };

export function useAdminImport() {
	const [uploading, setUploading] = useState(false);
	const [results, setResults] = useState<ResultRow[]>([]);
	const [errors, setErrors] = useState<ErrorRow[]>([]);
	const nextId = useRef(0);

	async function handleUpload(files: File[]) {
		if (!files.length) return;
		setUploading(true);
		const result = await admin.uploadGuaraniSheets(files);
		setUploading(false);
		const id = () => ++nextId.current;
		if (result.ok) {
			setResults((prev) => [
				...prev,
				...result.data.results.map((r) => ({ ...r, id: id() })),
			]);
			setErrors((prev) => [
				...prev,
				...result.data.errors.map((e) => ({ ...e, id: id() })),
			]);
		} else {
			setErrors((prev) => [
				...prev,
				{ file: "(upload)", error: result.error, id: id() },
			]);
		}
	}

	function handleClear() {
		setResults([]);
		setErrors([]);
	}

	return { uploading, results, errors, handleUpload, handleClear };
}
