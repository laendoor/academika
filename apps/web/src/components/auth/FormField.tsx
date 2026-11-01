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
			<label htmlFor={id} className="block text-sm font-medium text-sage-800">
				{label}
			</label>
			<input
				id={id}
				name={name}
				type={type}
				required={required}
				autoComplete={autoComplete}
				placeholder={placeholder}
				className="mt-1 block w-full rounded-md border border-sage-300 bg-white px-3 py-2 text-sm placeholder-sage-700 focus:border-accent-700 focus:outline-none focus:ring-1 focus:ring-accent-700"
			/>
		</div>
	);
}
