import { Table, Tbody, Th } from "@/components/ui/Table";
import type { UserItem, UserRole, UserUpdate } from "@/lib/api/admin";
import type { LookupOption } from "@/lib/api/lookups";

function RoleSelect({
	role,
	roles,
	disabled,
	onChange,
}: {
	role: UserRole;
	roles: LookupOption[];
	disabled: boolean;
	onChange: (role: UserRole) => void;
}) {
	return (
		<select
			value={role}
			disabled={disabled}
			onChange={(e) => onChange(e.target.value as UserRole)}
			className="rounded border border-zinc-200 bg-white px-2 py-1 text-sm text-zinc-700 disabled:opacity-50"
		>
			{roles.map((r) => (
				<option key={r.key} value={r.key}>
					{r.label}
				</option>
			))}
		</select>
	);
}

function StatusToggle({
	isActive,
	disabled,
	onToggle,
}: {
	isActive: boolean;
	disabled: boolean;
	onToggle: () => void;
}) {
	return (
		<button
			type="button"
			disabled={disabled}
			onClick={onToggle}
			className={`rounded px-2 py-1 text-xs font-medium disabled:opacity-50 ${
				isActive
					? "bg-green-100 text-green-700 hover:bg-green-200"
					: "bg-zinc-100 text-zinc-500 hover:bg-zinc-200"
			}`}
		>
			{isActive ? "Activo" : "Inactivo"}
		</button>
	);
}

function UserRow({
	user,
	roles,
	isUpdating,
	onUpdate,
}: {
	user: UserItem;
	roles: LookupOption[];
	isUpdating: boolean;
	onUpdate: (id: string, data: UserUpdate) => void;
}) {
	return (
		<tr className="bg-white">
			<td className="px-4 py-3 text-zinc-800">{user.email}</td>
			<td className="px-4 py-3">
				<RoleSelect
					role={user.role}
					roles={roles}
					disabled={isUpdating}
					onChange={(role) => onUpdate(user.id, { role })}
				/>
			</td>
			<td className="px-4 py-3">
				<StatusToggle
					isActive={user.is_active}
					disabled={isUpdating}
					onToggle={() => onUpdate(user.id, { is_active: !user.is_active })}
				/>
			</td>
		</tr>
	);
}

export function UsersTable({
	users,
	roles,
	updating,
	onUpdate,
}: {
	users: UserItem[];
	roles: LookupOption[];
	updating: string | null;
	onUpdate: (id: string, data: UserUpdate) => void;
}) {
	return (
		<Table>
			<thead className="bg-zinc-50">
				<tr>
					<Th>Email</Th>
					<Th>Rol</Th>
					<Th>Estado</Th>
				</tr>
			</thead>
			<Tbody>
				{users.map((user) => (
					<UserRow
						key={user.id}
						user={user}
						roles={roles}
						isUpdating={updating === user.id}
						onUpdate={onUpdate}
					/>
				))}
			</Tbody>
		</Table>
	);
}
