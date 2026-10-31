"use client";
import { X } from "lucide-react";
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
	"rounded border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700";

/** Input con lista de sugerencias: las flechas recorren, Enter elige, Escape cierra. */
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
		<div className="relative">
			<input
				role="combobox"
				aria-label={label}
				aria-expanded={visible}
				aria-controls={listId}
				aria-autocomplete="list"
				aria-activedescendant={active >= 0 ? `${listId}-${active}` : undefined}
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
					className="absolute top-1/2 right-2 -translate-y-1/2 rounded p-0.5 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-800"
				>
					<X aria-hidden className="h-3.5 w-3.5" />
				</button>
			)}
			{visible && (
				<div
					id={listId}
					role="listbox"
					className="absolute z-10 mt-1 w-full rounded border border-zinc-200 bg-white shadow-lg"
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
							className={`cursor-pointer px-3 py-1.5 text-sm text-zinc-700 ${
								i === active ? "bg-zinc-100" : ""
							}`}
						>
							{hit.label}
						</div>
					))}
				</div>
			)}
		</div>
	);
}
