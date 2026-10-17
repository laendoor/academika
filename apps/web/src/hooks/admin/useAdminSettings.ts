"use client";
import { useEffect, useState } from "react";

import * as admin from "@/lib/api/admin";

export function useAdminSettings() {
	const [settings, setSettings] = useState<admin.SettingItem[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();
	const [updating, setUpdating] = useState<string | null>(null);

	useEffect(() => {
		admin.getSettings().then((result) => {
			setLoading(false);
			if (result.ok) setSettings(result.data);
			else setError(result.error);
		});
	}, []);

	async function handleUpdate(key: string, value: unknown): Promise<boolean> {
		setUpdating(key);
		setError(undefined);
		const result = await admin.updateSetting(key, value);
		setUpdating(null);
		if (result.ok) {
			setSettings((prev) =>
				prev.map((s) => (s.key === result.data.key ? result.data : s)),
			);
			return true;
		}
		setError(result.error);
		return false;
	}

	return { settings, loading, error, updating, handleUpdate };
}
