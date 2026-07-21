import { Bot } from "lucide-react";

export function ChatPanel() {
	return (
		<div className="flex h-full flex-col">
			<div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
				<div className="rounded-full bg-zinc-100 p-3">
					<Bot className="h-8 w-8 text-zinc-400" />
				</div>
				<p className="mt-4 text-lg font-medium text-zinc-600">Hari</p>
				<p className="mt-1 text-sm text-zinc-400">
					Hari estará disponible próximamente
				</p>
			</div>
			<div className="border-t border-zinc-200 p-4">
				<div className="flex gap-2">
					<input
						type="text"
						disabled
						placeholder="Escribí tu consulta..."
						className="flex-1 rounded-lg border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm text-zinc-400 outline-none"
					/>
					<button
						type="button"
						disabled
						className="rounded-lg bg-zinc-200 px-4 py-2.5 text-sm font-medium text-zinc-400"
					>
						Enviar
					</button>
				</div>
			</div>
		</div>
	);
}
