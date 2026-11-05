"use client";
import { X } from "lucide-react";
import { Dialog } from "radix-ui";
import { type ReactNode, useEffect, useRef } from "react";

interface ModalProps {
	title: string;
	onClose: () => void;
	children: ReactNode;
}

/** Shell de modal sobre Radix: foco atrapado y devuelto al abridor, fondo inerte. */
export function Modal({ title, onClose, children }: ModalProps) {
	const panelRef = useRef<HTMLDivElement>(null);
	const openerRef = useRef<HTMLElement | null>(null);

	// Radix atrapa el foco; devolverlo es nuestro, para no depender del orden de
	// desmontaje cuando el modal se va con su contenedor. El abridor se guarda en
	// el auto-focus: un efecto de este componente ya corre con el panel enfocado.
	useEffect(() => {
		return () => {
			const opener = openerRef.current;
			if (opener?.isConnected) opener.focus();
		};
	}, []);

	return (
		<Dialog.Root
			open
			onOpenChange={(open) => {
				if (!open) onClose();
			}}
		>
			<Dialog.Portal>
				<Dialog.Overlay
					data-testid="modal-backdrop"
					onClick={onClose}
					className="fixed inset-0 z-50 bg-ink/50"
				/>
				<Dialog.Content
					ref={panelRef}
					aria-describedby={undefined}
					tabIndex={-1}
					onOpenAutoFocus={(e) => {
						// El panel recibe el foco, no el primer botón: el título se anuncia al abrir.
						e.preventDefault();
						openerRef.current = document.activeElement as HTMLElement | null;
						panelRef.current?.focus();
					}}
					className="fixed top-1/2 left-1/2 z-50 flex max-h-[80vh] w-[calc(100%-2rem)] max-w-4xl -translate-x-1/2 -translate-y-1/2 flex-col rounded-lg bg-white shadow-xl outline-none"
				>
					<div className="flex items-baseline justify-between gap-4 border-b border-sage-200 px-4 py-3">
						<Dialog.Title className="truncate text-sm font-medium text-sage-900">
							{title}
						</Dialog.Title>
						<Dialog.Close asChild>
							<button
								type="button"
								aria-label="Cerrar detalle"
								className="rounded p-1 text-sage-600 hover:bg-sage-100 hover:text-sage-900"
							>
								<X aria-hidden className="h-4 w-4" />
							</button>
						</Dialog.Close>
					</div>

					<div className="overflow-y-auto px-4 py-3">{children}</div>
				</Dialog.Content>
			</Dialog.Portal>
		</Dialog.Root>
	);
}
