import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { usePlanes } from "@/hooks/workspace/usePlanes";
import * as workspace from "@/lib/api/workspace";

vi.mock("@/lib/api/workspace", () => ({ getPlanes: vi.fn() }));

const getPlanes = vi.mocked(workspace.getPlanes);

describe("usePlanes", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("pasa paginación y filtro de carrera al cliente", async () => {
		getPlanes.mockResolvedValue({ ok: true, data: { total: 1, items: [] } });

		const { result } = renderHook(() => usePlanes({ carrera_id: "c1" }));

		await waitFor(() => expect(result.current.total).toBe(1));
		expect(getPlanes).toHaveBeenCalledWith(0, 20, "c1");
	});
});
