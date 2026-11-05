import type { ReactNode } from "react";

export function AuthFooterLink({
	href,
	children,
}: {
	href: string;
	children: ReactNode;
}) {
	return (
		<p className="text-center text-sm text-sage-700">
			<a
				href={href}
				className="text-accent-700 underline hover:text-accent-800"
			>
				{children}
			</a>
		</p>
	);
}
