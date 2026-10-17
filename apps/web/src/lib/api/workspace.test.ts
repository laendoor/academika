import { describe, expect, it, vi } from "vitest";

import * as client from "@/lib/api/client";
import { getPlanDetail, getPlanes } from "@/lib/api/workspace";

vi.mock("@/lib/api/client", () => ({ get: vi.fn() }));

const getMock = vi.mocked(client.get);

describe("getPlanes", () => {
	it("incluye el filtro por carrera solo cuando se pasa", async () => {
		getMock.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });

		await getPlanes(0, 20, "c1");
		expect(getMock).toHaveBeenCalledWith(
			"/api/planes?skip=0&limit=20&carrera_id=c1",
		);

		await getPlanes();
		expect(getMock).toHaveBeenCalledWith("/api/planes?skip=0&limit=20");
	});
});

describe("getPlanDetail", () => {
	it("encodea el id en la URL", async () => {
		getMock.mockResolvedValue({ ok: true, data: null });

		await getPlanDetail("a/b");
		expect(getMock).toHaveBeenCalledWith("/api/planes/a%2Fb");
	});
});
