export function FormError({ error }: { error?: string }) {
	if (!error) return null;
	return <p className="text-sm text-danger">{error}</p>;
}
