import type { ReactNode } from "react";

export function Table({ children }: { children: ReactNode }) {
	return (
		<div className="overflow-hidden rounded-lg border border-sage-200">
			<table className="w-full text-sm">{children}</table>
		</div>
	);
}

export function Th({ children }: { children: ReactNode }) {
	return (
		<th className="bg-sage-800 px-4 py-3 text-left font-medium text-surface">
			{children}
		</th>
	);
}

export function Tbody({ children }: { children: ReactNode }) {
	return <tbody className="divide-y divide-sage-100">{children}</tbody>;
}
