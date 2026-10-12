"use client";
import { X } from "lucide-react";
import { useEffect, useRef } from "react";

import type { SourceItem } from "@/lib/api/sources";

interface ImportDetailModalProps {
	item: SourceItem;
	subtitle: string;
	onClose: () => void;
}

export function ImportDetailModal({
	item,
	subtitle,
	onClose,
}: ImportDetailModalProps) {
	const { details } = item;
	const ok = item.status !== "error";
	const skipSample = details.skipped_sample ?? [];
	const panelRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		function onKey(e: KeyboardEvent) {
			if (e.key === "Escape") onClose();
		}
		document.addEventListener("keydown", onKey);
		return () => document.removeEventListener("keydown", onKey);
	}, [onClose]);

	useEffect(() => {
		panelRef.current?.focus();
	}, []);

	return (
		// biome-ignore lint/a11y/useKeyWithClickEvents lint/a11y/noStaticElementInteractions: cerrar por click fuera es atajo de mouse; teclado usa Escape y el botón Cerrar
		<div
			data-testid="import-modal-backdrop"
			className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
			onClick={(e) => {
				if (e.target === e.currentTarget) onClose();
			}}
		>
			<div
				role="dialog"
				aria-modal="true"
				aria-label={`Detalle de ${details.files[0] ?? "importación"}`}
				tabIndex={-1}
				ref={panelRef}
				className="flex max-h-[80vh] w-full max-w-3xl flex-col rounded-lg bg-white shadow-xl"
			>
				<div className="flex items-baseline justify-between gap-4 border-b border-zinc-200 px-4 py-3">
					<h2 className="truncate text-sm font-medium text-zinc-800">
						{subtitle}
					</h2>
					<button
						type="button"
						onClick={onClose}
						aria-label="Cerrar detalle"
						className="rounded p-1 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-800"
					>
						<X aria-hidden className="h-4 w-4" />
					</button>
				</div>

				<div className="overflow-y-auto px-4 py-3">
					<p className="text-sm text-zinc-600">
						procesadas: {details.processed.toLocaleString("es-AR")} · omitidas:{" "}
						{details.skipped.toLocaleString("es-AR")}
					</p>

					{!ok && (
						<pre className="mt-2 overflow-x-auto rounded bg-red-50 p-2 font-mono text-xs text-red-800">
							{details.error}
						</pre>
					)}

					<h3 className="mt-3 text-sm font-medium text-zinc-700">
						Muestra del archivo (cabecera + 5 filas)
					</h3>
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

					{details.skipped > 0 && (
						<div className="mt-3">
							<h3 className="text-sm font-medium text-zinc-700">
								No procesadas
								{details.skipped_sample_truncated &&
									` (mostrando ${skipSample.length} de ${details.skipped.toLocaleString("es-AR")})`}
							</h3>
							{skipSample.length > 0 ? (
								<pre className="mt-1 overflow-x-auto rounded bg-amber-50 p-2 font-mono text-xs text-amber-900">
									{skipSample.join("\n")}
								</pre>
							) : (
								<p className="mt-1 text-sm text-zinc-500">
									sin detalle (importación anterior)
								</p>
							)}
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
