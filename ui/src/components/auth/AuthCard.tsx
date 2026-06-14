import type { ReactNode } from "react";

export function AuthCard({
	children,
	className = "space-y-6",
}: {
	children: ReactNode;
	className?: string;
}) {
	return (
		<div className="flex min-h-full items-center justify-center bg-zinc-50 px-4">
			<div className={`w-full max-w-sm ${className}`}>{children}</div>
		</div>
	);
}
