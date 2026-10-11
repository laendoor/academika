"use client";
import { useState } from "react";

import { Table, Tbody, Th } from "@/components/ui/Table";
import type { SettingItem } from "@/lib/api/admin";

function SettingRow({
	setting,
	isUpdating,
	onUpdate,
}: {
	setting: SettingItem;
	isUpdating: boolean;
	onUpdate: (key: string, value: unknown) => void;
}) {
	const [draft, setDraft] = useState<string | null>(null);
	const [invalidJson, setInvalidJson] = useState(false);
	const text = draft ?? JSON.stringify(setting.value);
	const dirty = draft !== null && draft !== JSON.stringify(setting.value);

	function handleSave() {
		let parsed: unknown;
		try {
			parsed = JSON.parse(text);
		} catch {
			setInvalidJson(true);
			return;
		}
		setInvalidJson(false);
		setDraft(null);
		onUpdate(setting.key, parsed);
	}

	return (
		<tr className="border-t border-zinc-200">
			<td className="px-4 py-2 font-mono text-sm text-zinc-900">
				{setting.key}
			</td>
			<td className="px-4 py-2 text-sm text-zinc-500">{setting.description}</td>
			<td className="px-4 py-2">
				<input
					value={text}
					disabled={isUpdating}
					onChange={(e) => setDraft(e.target.value)}
					className="w-full rounded border border-zinc-200 bg-white px-2 py-1 font-mono text-sm text-zinc-700 disabled:opacity-50"
				/>
				{invalidJson && (
					<p className="mt-1 text-xs text-red-600">JSON inválido</p>
				)}
			</td>
			<td className="px-4 py-2 text-right">
				<button
					type="button"
					disabled={isUpdating || !dirty}
					onClick={handleSave}
					className="rounded px-2 py-1 text-xs font-medium text-zinc-700 hover:bg-zinc-100 disabled:opacity-50"
				>
					{isUpdating ? "Guardando…" : "Guardar"}
				</button>
			</td>
		</tr>
	);
}

export function SettingsTable({
	settings,
	updating,
	onUpdate,
}: {
	settings: SettingItem[];
	updating: string | null;
	onUpdate: (key: string, value: unknown) => void;
}) {
	return (
		<Table>
			<thead className="bg-zinc-50">
				<tr>
					<Th>Clave</Th>
					<Th>Descripción</Th>
					<Th>Valor</Th>
					<Th>
						<span className="sr-only">Acciones</span>
					</Th>
				</tr>
			</thead>
			<Tbody>
				{settings.map((setting) => (
					<SettingRow
						key={setting.key}
						setting={setting}
						isUpdating={updating === setting.key}
						onUpdate={onUpdate}
					/>
				))}
			</Tbody>
		</Table>
	);
}
