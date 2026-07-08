"use client";

import { UsersTable } from "@/components/admin/UsersTable";
import { ErrorState, LoadingState } from "@/components/ui/PageState";
import { useAdminUsers } from "@/hooks/admin";

export function UsersPanel() {
	const { users, loading, error, updating, handleUpdate } = useAdminUsers();

	if (loading) return <LoadingState />;
	if (error) return <ErrorState error={error} />;

	return (
		<UsersTable users={users} updating={updating} onUpdate={handleUpdate} />
	);
}
