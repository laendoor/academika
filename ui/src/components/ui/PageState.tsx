export function LoadingState() {
	return (
		<div className="flex min-h-full items-center justify-center">
			<p className="text-zinc-500">Cargando...</p>
		</div>
	);
}

export function ErrorState({ error }: { error: string }) {
	return (
		<div className="flex min-h-full items-center justify-center">
			<p className="text-red-500">{error}</p>
		</div>
	);
}
