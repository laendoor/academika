import { Check, History, X } from "lucide-react";
import { useState } from "react";

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

export function ImportLogList({ items }: { items: SourceItem[] }) {
	const resubmitted = resubmittedIds(items);
	const [open, setOpen] = useState<Set<string>>(new Set());

	function toggle(id: string) {
		const next = new Set(open);
		if (next.has(id)) next.delete(id);
		else next.add(id);
		setOpen(next);
	}

	return (
		<div>
			{items.map((item) => {
				const { details } = item;
				const ok = item.status !== "error";
				const skipSample = details.skipped_sample ?? [];
				return (
					<div key={item.id}>
						<button
							type="button"
							aria-expanded={open.has(item.id)}
							onClick={() => toggle(item.id)}
							className="flex w-full flex-wrap items-baseline gap-x-2 px-2 py-1 text-left hover:bg-zinc-50"
						>
							<span className="font-mono text-xs text-zinc-500">
								{formatIsoLocal(item.created_at)}
							</span>
							{ok ? (
								<Check
									aria-hidden
									className="h-4 w-4 self-center text-green-600"
								/>
							) : (
								<X aria-hidden className="h-4 w-4 self-center text-red-600" />
							)}
							<span className="text-sm text-zinc-800">
								{details.files[0] ?? "—"}
							</span>
							<span aria-hidden className="text-sm text-zinc-400">
								→
							</span>
							<span className="text-sm text-zinc-600">
								{typeLabel(details.sheet_type)}
							</span>
							{ok ? (
								<span className="text-sm text-zinc-600">
									· {details.processed.toLocaleString("es-AR")} ok
									{details.skipped > 0 &&
										` · ${details.skipped.toLocaleString("es-AR")} omitidas`}
								</span>
							) : (
								<span className="text-sm text-red-700">
									· error: {details.error}
								</span>
							)}
							<span className="text-xs text-zinc-500">
								por {emailLocal(details.uploader_email)}
							</span>
							{resubmitted.has(item.id) && (
								<span className="inline-flex items-center gap-1 rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-800">
									<History aria-hidden className="h-3 w-3" />
									re-subida
								</span>
							)}
						</button>
						{open.has(item.id) && (
							<div className="ml-6 border-l-2 border-zinc-200 pl-3 pb-2">
								{!ok && (
									<pre className="overflow-x-auto rounded bg-red-50 p-2 font-mono text-xs text-red-800">
										{details.error}
									</pre>
								)}
								{skipSample.length > 0 && (
									<div className="mt-1">
										<p className="text-sm text-zinc-600">omitidas (muestra):</p>
										<pre className="mt-1 overflow-x-auto rounded bg-amber-50 p-2 font-mono text-xs text-amber-900">
											{skipSample.join("\n")}
										</pre>
									</div>
								)}
								{details.preview ? (
									<pre className="mt-1 overflow-x-auto rounded bg-zinc-100 p-2 font-mono text-xs text-zinc-800">
										{details.preview.join("\n")}
										{details.preview_truncated && "\n… (muestra truncada)"}
									</pre>
								) : (
									<p className="mt-1 text-sm text-zinc-500">
										sin muestra (importación anterior)
									</p>
								)}
							</div>
						)}
					</div>
				);
			})}
		</div>
	);
}
