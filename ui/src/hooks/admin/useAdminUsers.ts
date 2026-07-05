"use client";
import { useEffect, useState } from "react";

import * as admin from "@/lib/api/admin";

export function useAdminUsers() {
	const [users, setUsers] = useState<admin.UserItem[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();
	const [updating, setUpdating] = useState<string | null>(null);

	useEffect(() => {
		admin.getUsers().then((result) => {
			setLoading(false);
			if (result.ok) setUsers(result.data.items);
			else setError(result.error);
		});
	}, []);

	async function handleUpdate(id: string, data: admin.UserUpdate) {
		setUpdating(id);
		const result = await admin.updateUser(id, data);
		setUpdating(null);
		if (result.ok) {
			setUsers((prev) =>
				prev.map((u) => (u.id === result.data.id ? result.data : u)),
			);
		} else {
			setError(result.error);
		}
	}

	return { users, loading, error, updating, handleUpdate };
}
