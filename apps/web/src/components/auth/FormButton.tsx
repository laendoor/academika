export function FormButton({
	pending,
	label,
	pendingLabel,
}: {
	pending: boolean;
	label: string;
	pendingLabel: string;
}) {
	return (
		<button
			type="submit"
			disabled={pending}
			className="w-full rounded-md bg-brand px-4 py-2 text-sm font-medium text-ink hover:bg-brand-600 disabled:opacity-50"
		>
			{pending ? pendingLabel : label}
		</button>
	);
}
