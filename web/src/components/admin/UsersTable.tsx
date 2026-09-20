import { Table, Tbody, Th } from "@/components/ui/Table";
import type { UserItem, UserRole, UserUpdate } from "@/lib/api/admin";

const ROLE_LABELS: Record<UserRole, string> = {
	admin: "Admin",
	director: "Director",
	docente: "Docente",
};

function RoleSelect({
	role,
	disabled,
	onChange,
}: {
	role: UserRole;
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
			{(Object.keys(ROLE_LABELS) as UserRole[]).map((r) => (
				<option key={r} value={r}>
					{ROLE_LABELS[r]}
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
	isUpdating,
	onUpdate,
}: {
	user: UserItem;
	isUpdating: boolean;
	onUpdate: (id: string, data: UserUpdate) => void;
}) {
	return (
		<tr className="bg-white">
			<td className="px-4 py-3 text-zinc-800">{user.email}</td>
			<td className="px-4 py-3">
				<RoleSelect
					role={user.role}
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
	updating,
	onUpdate,
}: {
	users: UserItem[];
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
						isUpdating={updating === user.id}
						onUpdate={onUpdate}
					/>
				))}
			</Tbody>
		</Table>
	);
}
