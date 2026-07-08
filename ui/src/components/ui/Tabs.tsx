"use client";
import { type ReactNode, useState } from "react";

export interface TabItem {
	label: string;
	content: ReactNode;
}

export function Tabs({ items }: { items: TabItem[] }) {
	const [active, setActive] = useState(0);

	return (
		<div>
			<div className="mb-6 flex gap-2 border-b border-zinc-200">
				{items.map((item, i) => (
					<button
						key={item.label}
						type="button"
						onClick={() => setActive(i)}
						className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${
							active === i
								? "border-zinc-900 text-zinc-900"
								: "border-transparent text-zinc-500 hover:text-zinc-700"
						}`}
					>
						{item.label}
					</button>
				))}
			</div>
			{items[active].content}
		</div>
	);
}
