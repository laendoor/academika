import { UserPlus } from "lucide-react";

import { useInviteUser } from "@/hooks/admin";
import type { UserRole } from "@/lib/api/admin";
import type { LookupOption } from "@/lib/api/lookups";

export function InviteUserForm({ roles }: { roles: LookupOption[] }) {
	const {
		email,
		setEmail,
		role,
		setRole,
		pending,
		error,
		success,
		handleSubmit,
	} = useInviteUser();

	return (
		<form
			onSubmit={(e) => {
				e.preventDefault();
				handleSubmit();
			}}
			className="mb-6 flex flex-wrap items-end gap-3"
		>
			<div>
				<label
					htmlFor="invite-email"
					className="block text-sm font-medium text-zinc-700"
				>
					Email
				</label>
				<input
					id="invite-email"
					name="email"
					type="email"
					required
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					disabled={pending}
					placeholder="usuario@unq.edu.ar"
					className="mt-1 rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 disabled:opacity-50"
				/>
			</div>

			<div>
				<label
					htmlFor="invite-role"
					className="block text-sm font-medium text-zinc-700"
				>
					Rol
				</label>
				<select
					id="invite-role"
					name="role"
					required
					value={role}
					onChange={(e) => setRole(e.target.value as UserRole)}
					disabled={pending}
					className="mt-1 rounded border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 disabled:opacity-50"
				>
					<option value="">Seleccioná un rol</option>
					{roles.map((r) => (
						<option key={r.key} value={r.key}>
							{r.label}
						</option>
					))}
				</select>
			</div>

			<button
				type="submit"
				disabled={pending}
				className="flex items-center gap-2 rounded bg-zinc-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
			>
				<UserPlus className="h-4 w-4" />
				{pending ? "Invitando..." : "Enviar invitación"}
			</button>

			{error && <p className="w-full text-sm text-red-600">{error}</p>}
			{success && <p className="w-full text-sm text-green-700">{success}</p>}
		</form>
	);
}
