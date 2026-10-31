"use client";
import { X } from "lucide-react";
import { type ReactNode, useEffect, useRef } from "react";

interface ModalProps {
	title: string;
	onClose: () => void;
	children: ReactNode;
}

/** Shell de modal: backdrop, Escape, foco inicial, cabecera y botón cerrar. */
export function Modal({ title, onClose, children }: ModalProps) {
	const panelRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		function onKey(e: KeyboardEvent) {
			if (e.key === "Escape") onClose();
		}
		document.addEventListener("keydown", onKey);
		return () => document.removeEventListener("keydown", onKey);
	}, [onClose]);

	useEffect(() => {
		panelRef.current?.focus();
	}, []);

	return (
		// biome-ignore lint/a11y/useKeyWithClickEvents lint/a11y/noStaticElementInteractions: cerrar por click fuera es atajo de mouse; teclado usa Escape y el botón Cerrar
		<div
			data-testid="modal-backdrop"
			className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
			onClick={(e) => {
				if (e.target === e.currentTarget) onClose();
			}}
		>
			<div
				role="dialog"
				aria-modal="true"
				aria-label={title}
				tabIndex={-1}
				ref={panelRef}
				className="flex max-h-[80vh] w-full max-w-4xl flex-col rounded-lg bg-white shadow-xl"
			>
				<div className="flex items-baseline justify-between gap-4 border-b border-zinc-200 px-4 py-3">
					<h2 className="truncate text-sm font-medium text-zinc-800">
						{title}
					</h2>
					<button
						type="button"
						onClick={onClose}
						aria-label="Cerrar detalle"
						className="rounded p-1 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-800"
					>
						<X aria-hidden className="h-4 w-4" />
					</button>
				</div>

				<div className="overflow-y-auto px-4 py-3">{children}</div>
			</div>
		</div>
	);
}
