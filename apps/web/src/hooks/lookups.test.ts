import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import {
	useEstadosAcademicos,
	useEstadosCursada,
	useNivelesCarrera,
	useNucleosCarrera,
	useTiposCursada,
	useUserRoles,
} from "@/hooks/lookups";
import * as lookups from "@/lib/api/lookups";

vi.mock("@/lib/api/lookups", () => ({
	getUserRoles: vi.fn(),
	getNivelesCarrera: vi.fn(),
	getNucleosCarrera: vi.fn(),
	getEstadosAcademicos: vi.fn(),
	getEstadosCursada: vi.fn(),
	getTiposCursada: vi.fn(),
}));

const getUserRoles = vi.mocked(lookups.getUserRoles);
const getNivelesCarrera = vi.mocked(lookups.getNivelesCarrera);
const getNucleosCarrera = vi.mocked(lookups.getNucleosCarrera);
const getEstadosAcademicos = vi.mocked(lookups.getEstadosAcademicos);
const getEstadosCursada = vi.mocked(lookups.getEstadosCursada);
const getTiposCursada = vi.mocked(lookups.getTiposCursada);

describe("useUserRoles", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga los roles del lookup", async () => {
		getUserRoles.mockResolvedValue({
			ok: true,
			data: [{ key: "docente", label: "Docente" }],
		});

		const { result } = renderHook(() => useUserRoles());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.roles).toEqual([
			{ key: "docente", label: "Docente" },
		]);
		expect(result.current.error).toBeUndefined();
	});

	it("expone el error si falla el fetch", async () => {
		getUserRoles.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useUserRoles());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("no autorizado");
		expect(result.current.roles).toEqual([]);
	});
});

describe("useNivelesCarrera", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga los niveles del lookup", async () => {
		getNivelesCarrera.mockResolvedValue({
			ok: true,
			data: [{ key: "grado", label: "Grado" }],
		});

		const { result } = renderHook(() => useNivelesCarrera());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.niveles).toEqual([{ key: "grado", label: "Grado" }]);
		expect(result.current.error).toBeUndefined();
	});

	it("expone el error si falla el fetch", async () => {
		getNivelesCarrera.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useNivelesCarrera());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("no autorizado");
		expect(result.current.niveles).toEqual([]);
	});
});

describe("useNucleosCarrera", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga los núcleos del lookup", async () => {
		getNucleosCarrera.mockResolvedValue({
			ok: true,
			data: [{ key: "basico", label: "Núcleo Básico" }],
		});

		const { result } = renderHook(() => useNucleosCarrera());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.nucleos).toEqual([
			{ key: "basico", label: "Núcleo Básico" },
		]);
		expect(result.current.error).toBeUndefined();
	});

	it("expone el error si falla el fetch", async () => {
		getNucleosCarrera.mockResolvedValue({ ok: false, error: "no autorizado" });

		const { result } = renderHook(() => useNucleosCarrera());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("no autorizado");
		expect(result.current.nucleos).toEqual([]);
	});
});

describe("useEstadosCursada", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga los estados de cursada del lookup", async () => {
		getEstadosCursada.mockResolvedValue({
			ok: true,
			data: [
				{ key: "inscripto", label: "Inscripto" },
				{ key: "regular", label: "Regular" },
			],
		});

		const { result } = renderHook(() => useEstadosCursada());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.estados.map((e) => e.key)).toEqual([
			"inscripto",
			"regular",
		]);
		expect(result.current.error).toBeUndefined();
	});
});

describe("useTiposCursada", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga los tipos de cursada del lookup", async () => {
		getTiposCursada.mockResolvedValue({
			ok: true,
			data: [{ key: "regular", label: "Cursada Regular" }],
		});

		const { result } = renderHook(() => useTiposCursada());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.tipos).toEqual([
			{ key: "regular", label: "Cursada Regular" },
		]);
		expect(result.current.error).toBeUndefined();
	});
});

describe("useEstadosAcademicos", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("carga los estados académicos del lookup", async () => {
		getEstadosAcademicos.mockResolvedValue({
			ok: true,
			data: [{ key: "alumno_regular", label: "Alumno Regular" }],
		});

		const { result } = renderHook(() => useEstadosAcademicos());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.estados).toEqual([
			{ key: "alumno_regular", label: "Alumno Regular" },
		]);
	});
});
