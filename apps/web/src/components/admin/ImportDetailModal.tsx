"use client";
import { Modal } from "@/components/ui/Modal";
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
	const sampleTruncated = details.skipped > skipSample.length;

	return (
		<Modal title={subtitle} onClose={onClose}>
			<p className="text-sm text-sage-700">
				procesadas: {details.processed.toLocaleString("es-AR")} · omitidas:{" "}
				{details.skipped.toLocaleString("es-AR")}
			</p>

			{!ok && (
				<pre className="mt-2 overflow-x-auto rounded bg-danger/10 p-2 font-mono text-xs text-danger">
					{details.error}
				</pre>
			)}

			<h3 className="mt-3 text-sm font-medium text-sage-800">
				Muestra del archivo (cabecera + 5 filas)
			</h3>
			{details.preview ? (
				<pre className="mt-1 overflow-x-auto rounded bg-sage-100 p-2 font-mono text-xs text-sage-800">
					{details.preview.join("\n")}
					{details.preview_truncated && "\n… (muestra truncada)"}
				</pre>
			) : (
				<p className="mt-1 text-sm text-sage-700">
					sin muestra (importación anterior)
				</p>
			)}

			{details.skipped > 0 && (
				<div className="mt-3">
					<h3 className="text-sm font-medium text-sage-800">
						No procesadas
						{sampleTruncated &&
							` (mostrando ${skipSample.length} de ${details.skipped.toLocaleString("es-AR")})`}
					</h3>
					{skipSample.length > 0 ? (
						<pre className="mt-1 overflow-x-auto rounded bg-warning/5 p-2 font-mono text-xs text-warning">
							{skipSample.join("\n")}
						</pre>
					) : (
						<p className="mt-1 text-sm text-sage-700">
							sin detalle (importación anterior)
						</p>
					)}
				</div>
			)}
		</Modal>
	);
}
