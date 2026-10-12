import { Check, History, X } from "lucide-react";

import type { SourceItem } from "@/lib/api/sources";
import { SHEET_TYPE_LABELS } from "@/lib/constants";

const dayFormat = new Intl.DateTimeFormat("es", {
	weekday: "long",
	day: "numeric",
	month: "long",
});
const dayFormatWithYear = new Intl.DateTimeFormat("es", {
	weekday: "long",
	day: "numeric",
	month: "long",
	year: "numeric",
});
const timeFormat = new Intl.DateTimeFormat("es-AR", {
	hour: "2-digit",
	minute: "2-digit",
	second: "2-digit",
	hour12: false,
});

export function dayKey(iso: string): string {
	const d = new Date(iso);
	return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
}

function dayLabel(date: Date): string {
	const label = (
		date.getFullYear() === new Date().getFullYear()
			? dayFormat
			: dayFormatWithYear
	)
		.format(date)
		.replace(",", "");
	return label.charAt(0).toLowerCase() + label.slice(1);
}

export function formatDayHeader(iso: string, now = new Date()): string {
	const date = new Date(iso);
	const startOf = (d: Date) =>
		new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
	const diffDays = Math.round((startOf(now) - startOf(date)) / 86_400_000);
	if (diffDays === 0) return `Hoy · ${dayLabel(date)}`;
	if (diffDays === 1) return `Ayer · ${dayLabel(date)}`;
	return dayLabel(date);
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

export interface DayGroup {
	key: string;
	header: string;
	items: SourceItem[];
}

export function groupByDay(items: SourceItem[], now = new Date()): DayGroup[] {
	const groups = new Map<string, DayGroup>();
	for (const item of items) {
		const key = dayKey(item.created_at);
		const group = groups.get(key);
		if (group) group.items.push(item);
		else
			groups.set(key, {
				key,
				header: formatDayHeader(item.created_at, now),
				items: [item],
			});
	}
	return [...groups.values()];
}

function typeLabel(sheetType: string | null): string {
	if (!sheetType) return "—";
	return SHEET_TYPE_LABELS[sheetType] ?? sheetType;
}

export function ImportLogList({ items }: { items: SourceItem[] }) {
	const resubmitted = resubmittedIds(items);

	return (
		<div>
			{groupByDay(items).map((group) => (
				<section key={group.key}>
					<h3 className="mt-4 border-b border-zinc-200 pb-1 text-sm font-medium text-zinc-700 first:mt-0">
						{group.header}
					</h3>
					{group.items.map((item) => {
						const { details } = item;
						const ok = item.status !== "error";
						return (
							<div
								key={item.id}
								className="flex flex-wrap items-baseline gap-x-2 px-2 py-1"
							>
								<span
									className="font-mono text-xs text-zinc-500"
									title={new Date(item.created_at).toLocaleString("es-AR")}
								>
									{timeFormat.format(new Date(item.created_at))}
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
							</div>
						);
					})}
				</section>
			))}
		</div>
	);
}
