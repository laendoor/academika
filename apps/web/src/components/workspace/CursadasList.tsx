"use client";
import { useState } from "react";

import { Combobox } from "@/components/ui/Combobox";
import { Pagination } from "@/components/ui/Pagination";
import { Table, Tbody, Th } from "@/components/ui/Table";
import { Tabs } from "@/components/ui/Tabs";
import { EstudianteDetalleModal } from "@/components/workspace/EstudianteDetalleModal";
import {
	useEstadosAcademicos,
	useEstadosCursada,
	useTiposCursada,
} from "@/hooks/lookups";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import {
	useCarreras,
	useCursadas,
	useSearchSuggestions,
} from "@/hooks/workspace";
import { toLabels } from "@/lib/api/lookups";
import { searchAlumnos, searchMaterias } from "@/lib/api/search";

const PAGE_SIZE = 20;
const INPUT_CLASS =
	"rounded border border-zinc-200 px-3 py-1.5 text-sm text-zinc-700";

export function CursadasList() {
	const [tab, setTab] = useState(0);
	const [skip, setSkip] = useState(0);
	const [carreraId, setCarreraId] = useState("");
	const [alumno, setAlumno] = useState("");
	const [materia, setMateria] = useState("");
	const [anio, setAnio] = useState("");
	const [cuatrimestre, setCuatrimestre] = useState("");
	const [estado, setEstado] = useState("");
	const [tipo, setTipo] = useState("");
	const [selectedAlumno, setSelectedAlumno] = useState<string | null>(null);
	const alumnoDebounced = useDebouncedValue(alumno);
	const materiaDebounced = useDebouncedValue(materia);
	const anioDebounced = useDebouncedValue(anio);
	// Menos de dos caracteres no filtra: el backend lo rechaza y no distingue nada.
	const alumnoTerm = alumnoDebounced.trim();
	const materiaTerm = materiaDebounced.trim();

	const { estados, error: estadosError } = useEstadosCursada();
	const { tipos } = useTiposCursada();
	const { estados: estadosAcademicos } = useEstadosAcademicos();
	const { items: carreras } = useCarreras({ limit: 100 });
	const alumnoSugerencias = useSearchSuggestions(searchAlumnos, alumno);
	const materiaSugerencias = useSearchSuggestions(searchMaterias, materia);

	// Historial = todo lo que no es una inscripción abierta.
	const historialKeys = estados
		.filter((e) => e.key !== "inscripto")
		.map((e) => e.key);
	const preset = tab === 0 ? historialKeys : ["inscripto"];
	const estadosFiltrados = estado ? [estado] : preset;
	// Sin el lookup, Historial no sabe qué excluir: se espera a tenerlo.
	const listo = tab !== 0 || historialKeys.length > 0;
	// Y si falla, se muestra el error en vez de una tabla sin filtrar (D3).
	const lookupError = tab === 0 ? estadosError : undefined;

	const { items, total, loading, error } = useCursadas({
		skip,
		limit: PAGE_SIZE,
		carrera_id: carreraId || undefined,
		alumno: alumnoTerm.length >= 2 ? alumnoTerm : undefined,
		materia: materiaTerm.length >= 2 ? materiaTerm : undefined,
		anio: anioDebounced ? Number(anioDebounced) : undefined,
		cuatrimestre: cuatrimestre || undefined,
		estado_cursada: estadosFiltrados,
		tipo_cursada: tipo || undefined,
		ready: listo,
	});

	const estadoLabels = toLabels(estados);
	const tipoLabels = toLabels(tipos);
	const estadoAcademicoLabels = toLabels(estadosAcademicos);

	function cambiarFiltro(setter: (value: string) => void) {
		return (value: string) => {
			setter(value);
			setSkip(0);
		};
	}

	const contenido = (
		<>
			<div className="mb-4 flex flex-wrap gap-3">
				<select
					aria-label="Filtrar por carrera"
					value={carreraId}
					onChange={(e) => cambiarFiltro(setCarreraId)(e.target.value)}
					className={INPUT_CLASS}
				>
					<option value="">Todas las carreras</option>
					{carreras.map((c) => (
						<option key={c.id} value={c.id}>
							{c.nombre}
						</option>
					))}
				</select>

				<Combobox
					label="Filtrar por alumno"
					placeholder="Alumno (DNI o nombre)"
					value={alumno}
					onChange={cambiarFiltro(setAlumno)}
					suggestions={alumnoSugerencias}
				/>

				<Combobox
					label="Filtrar por materia"
					placeholder="Materia (código o nombre)"
					value={materia}
					onChange={cambiarFiltro(setMateria)}
					suggestions={materiaSugerencias}
				/>

				<input
					aria-label="Filtrar por año"
					type="number"
					placeholder="Año"
					value={anio}
					onChange={(e) => cambiarFiltro(setAnio)(e.target.value)}
					className={`${INPUT_CLASS} w-24`}
				/>

				<select
					aria-label="Filtrar por cuatrimestre"
					value={cuatrimestre}
					onChange={(e) => cambiarFiltro(setCuatrimestre)(e.target.value)}
					className={INPUT_CLASS}
				>
					<option value="">Todos los cuatrimestres</option>
					<option value="1C">1C</option>
					<option value="2C">2C</option>
				</select>

				<select
					aria-label="Filtrar por estado"
					value={estado}
					onChange={(e) => cambiarFiltro(setEstado)(e.target.value)}
					className={INPUT_CLASS}
				>
					<option value="">Todos los estados</option>
					{estados.map((e) => (
						<option key={e.key} value={e.key}>
							{e.label}
						</option>
					))}
				</select>

				<select
					aria-label="Filtrar por tipo"
					value={tipo}
					onChange={(e) => cambiarFiltro(setTipo)(e.target.value)}
					className={INPUT_CLASS}
				>
					<option value="">Todos los tipos</option>
					{tipos.map((t) => (
						<option key={t.key} value={t.key}>
							{t.label}
						</option>
					))}
				</select>
			</div>

			{error && (
				<div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
					{error}
				</div>
			)}

			{lookupError && (
				<div
					role="alert"
					className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700"
				>
					No se pudo cargar el filtro de estados: {lookupError}
				</div>
			)}

			{!lookupError && (
				<>
					<Table>
						<thead className="bg-zinc-50">
							<tr>
								<Th>Alumno</Th>
								<Th>Materia</Th>
								<Th>Carrera</Th>
								<Th>Año</Th>
								<Th>Cuat.</Th>
								<Th>Comisión</Th>
								<Th>Tipo</Th>
								<Th>Estado</Th>
								<Th>Nota</Th>
							</tr>
						</thead>
						<Tbody>
							{items.map((item) => (
								<tr key={item.id} className="bg-white">
									<td className="px-4 py-3">
										<button
											type="button"
											onClick={() => setSelectedAlumno(item.alumno.id)}
											className="text-zinc-800 underline-offset-2 hover:underline"
										>
											{item.alumno.apellido}, {item.alumno.nombre}
										</button>
									</td>
									<td className="px-4 py-3 text-zinc-800">
										{item.materia.codigo} — {item.materia.nombre}
									</td>
									<td className="px-4 py-3 text-zinc-600">
										{item.carrera.codigo}
									</td>
									<td className="px-4 py-3 text-zinc-600">{item.anio}</td>
									<td className="px-4 py-3 text-zinc-600">
										{item.cuatrimestre}
									</td>
									<td className="px-4 py-3 text-zinc-600">
										{item.comision ?? "—"}
									</td>
									<td className="px-4 py-3 text-zinc-600">
										{tipoLabels[item.tipo_cursada] ?? item.tipo_cursada}
									</td>
									<td className="px-4 py-3 text-zinc-600">
										{estadoLabels[item.estado_cursada] ?? item.estado_cursada}
									</td>
									<td className="px-4 py-3 text-zinc-600">
										{item.nota ?? "—"}
									</td>
								</tr>
							))}
						</Tbody>
					</Table>

					{total === 0 && !loading && !error && (
						<p className="mt-4 text-sm text-zinc-500">Sin cursadas.</p>
					)}

					<Pagination
						skip={skip}
						total={total}
						pageSize={PAGE_SIZE}
						loading={loading}
						onChange={setSkip}
					/>
				</>
			)}
		</>
	);

	return (
		<div className="p-8">
			<h2 className="mb-4 text-lg font-medium text-zinc-800">
				Cursadas e Inscripciones
			</h2>

			<Tabs
				active={tab}
				onChange={(i) => {
					setTab(i);
					setEstado("");
					setSkip(0);
				}}
				items={[
					{ label: "Historial", content: contenido },
					{ label: "Inscripciones", content: contenido },
				]}
			/>

			{selectedAlumno && (
				<EstudianteDetalleModal
					alumnoId={selectedAlumno}
					estadoAcademicoLabels={estadoAcademicoLabels}
					estadoCursadaLabels={estadoLabels}
					tipoCursadaLabels={tipoLabels}
					onClose={() => setSelectedAlumno(null)}
				/>
			)}
		</div>
	);
}
