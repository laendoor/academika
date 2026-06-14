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
			className="w-full rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
		>
			{pending ? pendingLabel : label}
		</button>
	);
}
