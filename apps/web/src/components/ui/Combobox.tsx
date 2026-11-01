"use client";
import { X } from "lucide-react";
import { Popover } from "radix-ui";
import { type KeyboardEvent, useId, useState } from "react";

import type { SearchHit } from "@/lib/api/search";

interface ComboboxProps {
	label: string;
	placeholder: string;
	value: string;
	onChange: (value: string) => void;
	suggestions: SearchHit[];
}

const INPUT_CLASS =
	"rounded border border-sage-200 px-3 py-1.5 text-sm text-sage-800";

/**
 * Input con lista de sugerencias: las flechas recorren, Enter elige, Escape cierra.
 * La lista vive en un portal para que no la recorte el contenedor con scroll.
 */
export function Combobox({
	label,
	placeholder,
	value,
	onChange,
	suggestions,
}: ComboboxProps) {
	const listId = useId();
	const [open, setOpen] = useState(false);
	const [active, setActive] = useState(-1);
	const visible = open && suggestions.length > 0;

	function pick(hit: SearchHit) {
		onChange(hit.term);
		setOpen(false);
		setActive(-1);
	}

	function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
		if (e.key === "Escape") {
			setOpen(false);
			return;
		}
		if (!visible) return;
		if (e.key === "ArrowDown") {
			e.preventDefault();
			setActive((i) => (i + 1) % suggestions.length);
		} else if (e.key === "ArrowUp") {
			e.preventDefault();
			setActive((i) => (i <= 0 ? suggestions.length - 1 : i - 1));
		} else if (e.key === "Enter" && active >= 0) {
			e.preventDefault();
			const hit = suggestions[active];
			if (hit) pick(hit);
		}
	}

	return (
		<Popover.Root open={visible} modal={false}>
			<Popover.Anchor asChild>
				<div className="relative">
					<input
						role="combobox"
						aria-label={label}
						aria-expanded={visible}
						aria-controls={listId}
						aria-autocomplete="list"
						aria-activedescendant={
							active >= 0 ? `${listId}-${active}` : undefined
						}
						placeholder={placeholder}
						value={value}
						onChange={(e) => {
							onChange(e.target.value);
							setOpen(true);
							setActive(-1);
						}}
						onKeyDown={onKeyDown}
						onBlur={() => setOpen(false)}
						className={`${INPUT_CLASS} ${value ? "pr-8" : ""}`}
					/>
					{value && (
						<button
							type="button"
							aria-label="Limpiar filtro"
							onClick={() => {
								onChange("");
								setOpen(false);
								setActive(-1);
							}}
							className="absolute top-1/2 right-2 -translate-y-1/2 rounded p-0.5 text-sage-600 hover:bg-sage-100 hover:text-sage-900"
						>
							<X aria-hidden className="h-3.5 w-3.5" />
						</button>
					)}
				</div>
			</Popover.Anchor>
			<Popover.Portal>
				<Popover.Content
					id={listId}
					role="listbox"
					aria-label={label}
					align="start"
					sideOffset={4}
					onOpenAutoFocus={(e) => e.preventDefault()}
					onCloseAutoFocus={(e) => e.preventDefault()}
					className="z-50 w-[var(--radix-popover-trigger-width,16rem)] rounded border border-sage-200 bg-white shadow-lg"
				>
					{suggestions.map((hit, i) => (
						// biome-ignore lint/a11y/useKeyWithClickEvents: el teclado lo maneja el input (patrón combobox); esto es el atajo de mouse
						<div
							key={hit.id}
							id={`${listId}-${i}`}
							role="option"
							tabIndex={-1}
							aria-selected={i === active}
							onMouseDown={(e) => e.preventDefault()}
							onClick={() => pick(hit)}
							className={`cursor-pointer px-3 py-1.5 text-sm text-sage-800 ${
								i === active ? "bg-sage-100" : ""
							}`}
						>
							{hit.label}
						</div>
					))}
				</Popover.Content>
			</Popover.Portal>
		</Popover.Root>
	);
}
