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

	async function handleUpdate(key: string, value: unknown) {
		setUpdating(key);
		const result = await admin.updateSetting(key, value);
		setUpdating(null);
		if (result.ok) {
			setSettings((prev) =>
				prev.map((s) => (s.key === result.data.key ? result.data : s)),
			);
		} else {
			setError(result.error);
		}
	}

	return { settings, loading, error, updating, handleUpdate };
}
