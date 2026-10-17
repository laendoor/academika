"use client";
import { X } from "lucide-react";
import { useEffect, useRef } from "react";

import { Table, Tbody, Th } from "@/components/ui/Table";
import type { PlanDetail } from "@/lib/api/workspace";

interface PlanDetailModalProps {
	detail: PlanDetail | null;
	loading: boolean;
	error?: string;
	nivelLabels: Record<string, string>;
	nucleoLabels: Record<string, string>;
	onClose: () => void;
}

export function PlanDetailModal({
	detail,
	loading,
	error,
	nivelLabels,
	nucleoLabels,
	onClose,
}: PlanDetailModalProps) {
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
			data-testid="plan-modal-backdrop"
			className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
			onClick={(e) => {
				if (e.target === e.currentTarget) onClose();
			}}
		>
			<div
				role="dialog"
				aria-modal="true"
				aria-label={`Detalle de ${detail?.nombre ?? "plan"}`}
				tabIndex={-1}
				ref={panelRef}
				className="flex max-h-[80vh] w-full max-w-3xl flex-col rounded-lg bg-white shadow-xl"
			>
				<div className="flex items-baseline justify-between gap-4 border-b border-zinc-200 px-4 py-3">
					<h2 className="truncate text-sm font-medium text-zinc-800">
						{detail?.nombre ?? "Detalle del plan"}
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

				<div className="overflow-y-auto px-4 py-3">
					{loading && <p className="text-sm text-zinc-500">Cargando…</p>}
					{error && (
						<p className="text-sm text-red-700" role="alert">
							{error}
						</p>
					)}
					{detail && (
						<>
							<p className="text-sm text-zinc-600">
								{detail.carrera_nombre} · Plan {detail.anio} ·{" "}
								{detail.nivel
									? (nivelLabels[detail.nivel] ?? detail.nivel)
									: "—"}{" "}
								· {detail.vigente ? "vigente" : "no vigente"}
							</p>

							<h3 className="mt-3 text-sm font-medium text-zinc-700">
								Materias ({detail.materias.length})
							</h3>
							{detail.materias.length > 0 ? (
								<Table>
									<thead className="bg-zinc-50">
										<tr>
											<Th>Código</Th>
											<Th>Sigla</Th>
											<Th>Nombre</Th>
											<Th>Créditos</Th>
											<Th>Núcleo</Th>
											<Th>Hs/sem</Th>
											<Th>Hs tot</Th>
										</tr>
									</thead>
									<Tbody>
										{detail.materias.map((m) => (
											<tr key={m.id} className="bg-white">
												<td className="px-4 py-3 text-zinc-600">{m.codigo}</td>
												<td className="px-4 py-3 text-zinc-600">
													{m.sigla ?? "—"}
												</td>
												<td className="px-4 py-3 text-zinc-800">{m.nombre}</td>
												<td className="px-4 py-3 text-zinc-600">
													{m.creditos?.toString() ?? "—"}
												</td>
												<td className="px-4 py-3 text-zinc-600">
													{m.nucleo
														? (nucleoLabels[m.nucleo] ?? m.nucleo)
														: "—"}
												</td>
												<td className="px-4 py-3 text-zinc-600">
													{m.horas_semanales?.toString() ?? "—"}
												</td>
												<td className="px-4 py-3 text-zinc-600">
													{m.carga_horaria_total?.toString() ?? "—"}
												</td>
											</tr>
										))}
									</Tbody>
								</Table>
							) : (
								<p className="mt-1 text-sm text-zinc-500">
									Este plan no tiene materias vinculadas.
								</p>
							)}
						</>
					)}
				</div>
			</div>
		</div>
	);
}
