"use client";
import { UserPlus } from "lucide-react";
import { useState } from "react";

import { InviteUserForm } from "@/components/admin/InviteUserForm";
import { UsersTable } from "@/components/admin/UsersTable";
import { ErrorState, LoadingState } from "@/components/ui/PageState";
import { useAdminUsers } from "@/hooks/admin";
import { useUserRoles } from "@/hooks/lookups";

export function UsersPanel() {
	const {
		users,
		loading,
		error,
		updating,
		deleting,
		handleUpdate,
		handleDelete,
	} = useAdminUsers();
	const { roles, loading: rolesLoading, error: rolesError } = useUserRoles();
	const [showInvite, setShowInvite] = useState(false);

	const panelError = error ?? rolesError;

	if (loading || rolesLoading) return <LoadingState />;
	if (panelError) return <ErrorState error={panelError} />;

	return (
		<div>
			<button
				type="button"
				onClick={() => setShowInvite((visible) => !visible)}
				className="mb-4 flex items-center gap-2 rounded border border-zinc-300 px-4 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
			>
				<UserPlus className="h-4 w-4" />
				Invitar
			</button>

			{showInvite && <InviteUserForm roles={roles} />}

			<UsersTable
				users={users}
				roles={roles}
				updating={updating}
				deleting={deleting}
				onUpdate={handleUpdate}
				onDelete={handleDelete}
			/>
		</div>
	);
}
