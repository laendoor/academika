import { FileText } from "lucide-react";

export function SourcesPanel() {
	return (
		<div className="flex h-full flex-col items-center justify-center p-8 text-center">
			<div className="rounded-full bg-zinc-100 p-3">
				<FileText className="h-6 w-6 text-zinc-400" />
			</div>
			<p className="mt-4 text-sm font-medium text-zinc-600">Sources</p>
			<p className="mt-1 text-xs text-zinc-400">Próximamente disponible</p>
		</div>
	);
}
