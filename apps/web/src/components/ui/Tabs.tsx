"use client";
import { type ReactNode, useState } from "react";

export interface TabItem {
	label: string;
	content: ReactNode;
}

interface TabsBase {
	items: TabItem[];
}

// `active` sin `onChange` dejaría los tabs muertos: el click actualiza el estado
// interno que el índice controlado ignora.
type TabsProps = TabsBase &
	(
		| { active?: undefined; onChange?: undefined }
		| { active: number; onChange: (index: number) => void }
	);

export function Tabs({ items, active, onChange }: TabsProps) {
	const [internal, setInternal] = useState(0);
	const current = active ?? internal;
	const select = onChange ?? setInternal;

	return (
		<div>
			<div className="mb-6 flex gap-2 border-b border-zinc-200">
				{items.map((item, i) => (
					<button
						key={item.label}
						type="button"
						onClick={() => select(i)}
						className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${
							current === i
								? "border-zinc-900 text-zinc-900"
								: "border-transparent text-zinc-500 hover:text-zinc-700"
						}`}
					>
						{item.label}
					</button>
				))}
			</div>
			{items[current].content}
		</div>
	);
}
