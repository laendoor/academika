"use client";
import { Tabs as RadixTabs } from "radix-ui";
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
		<RadixTabs.Root
			value={String(current)}
			onValueChange={(value) => select(Number(value))}
		>
			<RadixTabs.List className="mb-6 flex gap-2 border-b border-sage-200">
				{items.map((item, i) => (
					<RadixTabs.Trigger
						key={item.label}
						value={String(i)}
						className="-mb-px border-b-2 border-transparent px-4 py-2 text-sm font-medium text-sage-700 hover:text-sage-900 data-[state=active]:border-brand-700 data-[state=active]:text-sage-900"
					>
						{item.label}
					</RadixTabs.Trigger>
				))}
			</RadixTabs.List>
			{items.map((item, i) => (
				<RadixTabs.Content key={item.label} value={String(i)}>
					{item.content}
				</RadixTabs.Content>
			))}
		</RadixTabs.Root>
	);
}
