"use client";
import { Modal } from "@/components/ui/Modal";
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
	return (
		<Modal title={detail?.nombre ?? "Detalle del plan"} onClose={onClose}>
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
						{detail.nivel ? (nivelLabels[detail.nivel] ?? detail.nivel) : "—"} ·{" "}
						{detail.vigente ? "vigente" : "no vigente"}
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
											{m.nucleo ? (nucleoLabels[m.nucleo] ?? m.nucleo) : "—"}
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
		</Modal>
	);
}
