"use client";
import { Modal } from "@/components/ui/Modal";
import { Table, Tbody, Th } from "@/components/ui/Table";
import { useEstudianteDetalle } from "@/hooks/workspace";

interface EstudianteDetalleModalProps {
	alumnoId: string;
	estadoAcademicoLabels: Record<string, string>;
	estadoCursadaLabels: Record<string, string>;
	tipoCursadaLabels: Record<string, string>;
	onClose: () => void;
}

export function EstudianteDetalleModal({
	alumnoId,
	estadoAcademicoLabels,
	estadoCursadaLabels,
	tipoCursadaLabels,
	onClose,
}: EstudianteDetalleModalProps) {
	const { detail, loading, error } = useEstudianteDetalle(alumnoId);

	const title = detail
		? `${detail.apellido}, ${detail.nombre}`
		: "Detalle del estudiante";

	return (
		<Modal title={title} onClose={onClose}>
			{loading && <p className="text-sm text-zinc-500">Cargando…</p>}
			{error && (
				<p className="text-sm text-red-700" role="alert">
					{error}
				</p>
			)}
			{detail && (
				<>
					<p className="text-sm text-zinc-600">
						Legajo {detail.legajo ?? "—"} · DNI {detail.dni}
					</p>

					<h3 className="mt-4 mb-2 text-sm font-medium text-zinc-700">
						Carreras ({detail.carreras.length})
					</h3>
					{detail.carreras.length > 0 ? (
						<ul className="mb-4 space-y-1 text-sm text-zinc-600">
							{detail.carreras.map((c) => (
								<li key={c.plan_id}>
									<span className="text-zinc-800">{c.carrera_nombre}</span> ·
									Plan {c.plan_nombre} ({c.anio}) ·{" "}
									{estadoAcademicoLabels[c.estado_academico] ??
										c.estado_academico}
								</li>
							))}
						</ul>
					) : (
						<p className="mb-4 text-sm text-zinc-500">Sin carreras.</p>
					)}

					<h3 className="mt-4 mb-2 text-sm font-medium text-zinc-700">
						Historial de cursadas ({detail.cursadas.length})
					</h3>
					{detail.cursadas.length > 0 ? (
						<Table>
							<thead className="bg-zinc-50">
								<tr>
									<Th>Materia</Th>
									<Th>Carrera</Th>
									<Th>Año</Th>
									<Th>Cuat.</Th>
									<Th>Tipo</Th>
									<Th>Estado</Th>
									<Th>Nota</Th>
								</tr>
							</thead>
							<Tbody>
								{detail.cursadas.map((c) => (
									<tr key={c.id} className="bg-white">
										<td className="px-4 py-2 text-zinc-800">
											{c.materia.codigo} — {c.materia.nombre}
										</td>
										<td className="px-4 py-2 text-zinc-600">
											{c.carrera.codigo}
										</td>
										<td className="px-4 py-2 text-zinc-600">{c.anio}</td>
										<td className="px-4 py-2 text-zinc-600">
											{c.cuatrimestre}
										</td>
										<td className="px-4 py-2 text-zinc-600">
											{tipoCursadaLabels[c.tipo_cursada] ?? c.tipo_cursada}
										</td>
										<td className="px-4 py-2 text-zinc-600">
											{estadoCursadaLabels[c.estado_cursada] ??
												c.estado_cursada}
										</td>
										<td className="px-4 py-2 text-zinc-600">{c.nota ?? "—"}</td>
									</tr>
								))}
							</Tbody>
						</Table>
					) : (
						<p className="text-sm text-zinc-500">Sin cursadas.</p>
					)}
				</>
			)}
		</Modal>
	);
}
