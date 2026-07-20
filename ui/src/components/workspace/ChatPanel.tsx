export function ChatPanel() {
	return (
		<div className="flex h-full flex-col">
			<div className="flex-1" />
			<div className="border-t border-zinc-200 p-4">
				<div className="flex gap-2">
					<input
						type="text"
						disabled
						placeholder="Hari estará disponible próximamente..."
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
