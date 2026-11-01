export function AuthHeader({
	title,
	subtitle,
}: {
	title: string;
	subtitle: string;
}) {
	return (
		<div className="text-center">
			<h1 className="text-2xl font-semibold tracking-tight text-sage-900">
				{title}
			</h1>
			<p className="mt-1 text-sm text-sage-700">{subtitle}</p>
		</div>
	);
}
