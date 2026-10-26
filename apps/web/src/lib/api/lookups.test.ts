import { describe, expect, it, vi } from "vitest";

import * as client from "@/lib/api/client";
import { getEstadosCursada, getTiposCursada } from "@/lib/api/lookups";

vi.mock("@/lib/api/client", () => ({ get: vi.fn() }));

const getMock = vi.mocked(client.get);

describe("lookups de cursada", () => {
	it("pega en los endpoints del BFF", async () => {
		getMock.mockResolvedValue({ ok: true, data: [] });

		await getEstadosCursada();
		expect(getMock).toHaveBeenCalledWith("/api/lookups/estado-cursada");

		await getTiposCursada();
		expect(getMock).toHaveBeenCalledWith("/api/lookups/tipo-cursada");
	});
});
