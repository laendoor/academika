export function LoadingState() {
	return (
		<div className="flex min-h-full items-center justify-center">
			<p className="text-sage-700">Cargando...</p>
		</div>
	);
}

export function ErrorState({ error }: { error: string }) {
	return (
		<div className="flex min-h-full items-center justify-center">
			<p className="text-danger">{error}</p>
		</div>
	);
}
