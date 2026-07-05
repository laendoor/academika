"use client";
import { UsersTable } from "@/components/admin/UsersTable";
import { ErrorState, LoadingState } from "@/components/ui/PageState";
import { useAdminUsers } from "@/hooks/admin";

export default function AdminPage() {
	const { users, loading, error, updating, handleUpdate } = useAdminUsers();

	if (loading) return <LoadingState />;
	if (error) return <ErrorState error={error} />;

	return (
		<div className="p-8">
			<h1 className="mb-6 text-lg font-semibold text-zinc-900">Usuarios</h1>
			<UsersTable users={users} updating={updating} onUpdate={handleUpdate} />
		</div>
	);
}
