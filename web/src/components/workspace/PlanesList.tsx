"use client";
import { useCallback, useEffect, useRef, useState } from "react";

import { Pagination } from "@/components/ui/Pagination";
import { Table, Tbody, Th } from "@/components/ui/Table";
import { PlanDetailModal } from "@/components/workspace/PlanDetailModal";
import { usePlanes } from "@/hooks/workspace";
import type { LookupOption } from "@/lib/api/lookups";
import * as lookups from "@/lib/api/lookups";
import type { CarreraOption, PlanDetail, PlanRow } from "@/lib/api/workspace";
import * as workspace from "@/lib/api/workspace";

const PAGE_SIZE = 20;

function toLabels(options: LookupOption[]): Record<string, string> {
	return Object.fromEntries(options.map((o) => [o.key, o.label]));
}

export function PlanesList() {
	const [skip, setSkip] = useState(0);
	const [carreraId, setCarreraId] = useState("");
	const [carreras, setCarreras] = useState<CarreraOption[]>([]);
	const [niveles, setNiveles] = useState<LookupOption[]>([]);
	const [nucleos, setNucleos] = useState<LookupOption[]>([]);
	const [selected, setSelected] = useState(false);
	const [detail, setDetail] = useState<PlanDetail | null>(null);
	const [detailLoading, setDetailLoading] = useState(false);
	const [detailError, setDetailError] = useState<string | undefined>(undefined);
	const requestId = useRef(0);

	const { items, total, loading, error } = usePlanes({
		skip,
		limit: PAGE_SIZE,
		carrera_id: carreraId || undefined,
	});

	useEffect(() => {
		workspace.getCarreras().then((r) => {
			if (r.ok) setCarreras(r.data.items);
			else console.warn("Error fetching carreras:", r.error);
		});
		lookups.getNivelesCarrera().then((r) => {
			if (r.ok) setNiveles(r.data);
			else console.warn("Error fetching niveles:", r.error);
		});
		lookups.getNucleosCarrera().then((r) => {
			if (r.ok) setNucleos(r.data);
			else console.warn("Error fetching núcleos:", r.error);
		});
	}, []);

	const nivelLabels = toLabels(niveles);
	const nucleoLabels = toLabels(nucleos);

	const closeDetail = useCallback(() => {
		setSelected(false);
		setDetail(null);
		setDetailError(undefined);
	}, []);

	async function openDetail(plan: PlanRow) {
		const id = ++requestId.current;
		setSelected(true);
		setDetail(null);
		setDetailError(undefined);
		setDetailLoading(true);
		const r = await workspace.getPlanDetail(plan.id);
		if (requestId.current !== id) return;
		setDetailLoading(false);
		if (r.ok) setDetail(r.data);
		else setDetailError(r.error);
	}

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-zinc-800">
				Planes de estudio
			</h2>

			<div className="mb-4 flex gap-4">
				<select
					aria-label="Filtrar por carrera"
					value={carreraId}
					onChange={(e) => {
						setCarreraId(e.target.value);
						setSkip(0);
					}}
					className="rounded border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700"
				>
					<option value="">Todas las carreras</option>
					{carreras.map((c) => (
						<option key={c.id} value={c.id}>
							{c.nombre}
						</option>
					))}
				</select>
			</div>

			{error && (
				<div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			)}

			<Table>
				<thead className="bg-zinc-50">
					<tr>
						<Th>Nombre</Th>
						<Th>Carrera</Th>
						<Th>Año</Th>
						<Th>Nivel</Th>
						<Th>Vigente</Th>
					</tr>
				</thead>
				<Tbody>
					{items.map((item) => (
						<tr key={item.id} className="bg-white">
							<td className="px-4 py-3">
								<button
									type="button"
									aria-haspopup="dialog"
									onClick={() => openDetail(item)}
									className="text-zinc-800 underline decoration-zinc-300 underline-offset-2 hover:decoration-zinc-600"
								>
									{item.nombre}
								</button>
							</td>
							<td className="px-4 py-3 text-zinc-600">{item.carrera_nombre}</td>
							<td className="px-4 py-3 text-zinc-600">{item.anio}</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.nivel ? (nivelLabels[item.nivel] ?? item.nivel) : "—"}
							</td>
							<td className="px-4 py-3 text-zinc-600">
								{item.vigente ? "Sí" : "No"}
							</td>
						</tr>
					))}
				</Tbody>
			</Table>

			{total === 0 && !loading && !error && (
				<p className="mt-4 text-sm text-zinc-500">Sin planes.</p>
			)}

			<Pagination
				skip={skip}
				total={total}
				pageSize={PAGE_SIZE}
				loading={loading}
				onChange={setSkip}
			/>

			{selected && (
				<PlanDetailModal
					detail={detail}
					loading={detailLoading}
					error={detailError}
					nivelLabels={nivelLabels}
					nucleoLabels={nucleoLabels}
					onClose={closeDetail}
				/>
			)}
		</div>
	);
}
