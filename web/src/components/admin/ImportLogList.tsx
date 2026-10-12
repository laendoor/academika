import { Check, History, X } from "lucide-react";
import { useState } from "react";

import { ImportDetailModal } from "@/components/admin/ImportDetailModal";
import type { SourceItem } from "@/lib/api/sources";
import { SHEET_TYPE_LABELS } from "@/lib/constants";

/** Fecha que nunca revienta el render: normaliza el str() de Python y cae al crudo. */
export function parseDate(iso: string): Date | null {
	let date = new Date(iso);
	if (Number.isNaN(date.getTime())) date = new Date(iso.replace(" ", "T"));
	return Number.isNaN(date.getTime()) ? null : date;
}

export function formatIsoLocal(iso: string): string {
	const date = parseDate(iso);
	if (!date) return iso;
	const pad = (n: number) => String(n).padStart(2, "0");
	return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

export function emailLocal(email: string | null | undefined): string {
	if (!email) return "—";
	return email.split("@")[0];
}

/** Ids cuya file_hash ya apareció en una fila más vieja (el historial viene DESC). */
export function resubmittedIds(items: SourceItem[]): Set<string> {
	const seen = new Set<string>();
	const out = new Set<string>();
	for (const item of [...items].reverse()) {
		const hash = item.details.file_hash;
		if (!hash) continue;
		if (seen.has(hash)) out.add(item.id);
		seen.add(hash);
	}
	return out;
}

function typeLabel(sheetType: string | null): string {
	if (!sheetType) return "—";
	return SHEET_TYPE_LABELS[sheetType] ?? sheetType;
}

function statusIcon(item: SourceItem, isResubmission: boolean) {
	if (item.status === "error")
		return (
			<span title={item.details.error ?? "error"}>
				<X aria-hidden className="h-4 w-4 text-red-600" />
			</span>
		);
	if (isResubmission)
		return (
			<span title="Re-subida: este archivo ya se había importado antes">
				<History aria-hidden className="h-4 w-4 text-amber-600" />
			</span>
		);
	return (
		<span title="ok">
			<Check aria-hidden className="h-4 w-4 text-green-600" />
		</span>
	);
}

export function ImportLogList({ items }: { items: SourceItem[] }) {
	const resubmitted = resubmittedIds(items);
	const [selected, setSelected] = useState<SourceItem | null>(null);

	return (
		<div>
			{items.map((item) => {
				const { details } = item;
				const ok = item.status !== "error";
				return (
					<button
						key={item.id}
						type="button"
						aria-haspopup="dialog"
						onClick={() => setSelected(item)}
						className="grid w-full grid-cols-[150px_20px_minmax(0,1.2fr)_minmax(0,0.8fr)_minmax(0,1.5fr)_auto] items-center gap-x-2 px-2 py-1 text-left hover:bg-zinc-50"
					>
						<span className="font-mono text-xs text-zinc-500">
							{formatIsoLocal(item.created_at)}
						</span>
						{statusIcon(item, resubmitted.has(item.id))}
						<span
							className="truncate text-sm text-zinc-800"
							title={details.files[0] ?? "—"}
						>
							{details.files[0] ?? "—"}
						</span>
						<span className="truncate text-sm text-zinc-600">
							{typeLabel(details.sheet_type)}
						</span>
						{ok ? (
							<span className="text-sm text-zinc-600">
								· {details.processed.toLocaleString("es-AR")} ok
								{details.skipped > 0 &&
									` · ${details.skipped.toLocaleString("es-AR")} omitidas`}
							</span>
						) : (
							<span className="truncate text-sm text-red-700">
								· error: {details.error}
							</span>
						)}
						<span
							className="text-xs text-zinc-500"
							title={details.uploader_email ?? "—"}
						>
							por {emailLocal(details.uploader_email)}
						</span>
					</button>
				);
			})}
			{selected && (
				<ImportDetailModal
					item={selected}
					subtitle={`${selected.details.files[0] ?? "—"} — ${formatIsoLocal(selected.created_at)} — ${typeLabel(selected.details.sheet_type)}`}
					onClose={() => setSelected(null)}
				/>
			)}
		</div>
	);
}
