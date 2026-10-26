import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useEstudianteDetalle } from "@/hooks/workspace/useEstudianteDetalle";
import type { ApiResult } from "@/lib/api/client";
import type { EstudianteDetalle } from "@/lib/api/workspace";
import * as workspace from "@/lib/api/workspace";

vi.mock("@/lib/api/workspace", () => ({ getEstudianteDetalle: vi.fn() }));

const getEstudianteDetalle = vi.mocked(workspace.getEstudianteDetalle);

function detalle(id: string): ApiResult<EstudianteDetalle> {
	return {
		ok: true,
		data: {
			id,
			nombre: "Ana",
			apellido: "García",
			dni: "12345678",
			legajo: null,
			carreras: [],
			cursadas: [],
		},
	};
}

function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((r) => {
		resolve = r;
	});
	return { promise, resolve };
}

beforeEach(() => {
	vi.clearAllMocks();
});

describe("useEstudianteDetalle", () => {
	it("descarta la respuesta del alumno anterior", async () => {
		const primero = deferred<ApiResult<EstudianteDetalle>>();
		const segundo = deferred<ApiResult<EstudianteDetalle>>();
		getEstudianteDetalle
			.mockReturnValueOnce(primero.promise)
			.mockReturnValueOnce(segundo.promise);

		const { result, rerender } = renderHook(
			({ id }) => useEstudianteDetalle(id),
			{ initialProps: { id: "a1" } },
		);
		rerender({ id: "a2" });

		await act(async () => {
			segundo.resolve(detalle("a2"));
		});
		await act(async () => {
			primero.resolve(detalle("a1"));
		});

		expect(result.current.detail?.id).toBe("a2");
		expect(result.current.loading).toBe(false);
	});

	it("expone el error del fetch", async () => {
		getEstudianteDetalle.mockResolvedValue({
			ok: false,
			error: "estudiante no encontrado",
		});

		const { result } = renderHook(() => useEstudianteDetalle("a1"));

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.error).toBe("estudiante no encontrado");
		expect(result.current.detail).toBeNull();
	});
});
