export function FormField({
	id,
	name,
	label,
	type = "text",
	required,
	autoComplete,
	placeholder,
}: {
	id: string;
	name: string;
	label: string;
	type?: string;
	required?: boolean;
	autoComplete?: string;
	placeholder?: string;
}) {
	return (
		<div>
			<label htmlFor={id} className="block text-sm font-medium text-zinc-700">
				{label}
			</label>
			<input
				id={id}
				name={name}
				type={type}
				required={required}
				autoComplete={autoComplete}
				placeholder={placeholder}
				className="mt-1 block w-full rounded-md border border-zinc-300 px-3 py-2 text-sm placeholder-zinc-400 focus:border-zinc-900 focus:outline-none focus:ring-1 focus:ring-zinc-900"
			/>
		</div>
	);
}
