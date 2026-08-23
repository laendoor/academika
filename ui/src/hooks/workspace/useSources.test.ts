import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useSources } from "@/hooks/workspace/useSources";
import * as sources from "@/lib/api/sources";

const { useWebSocketMock } = vi.hoisted(() => ({ useWebSocketMock: vi.fn() }));

vi.mock("@/hooks/useWebSocket", () => ({ useWebSocket: useWebSocketMock }));
vi.mock("@/lib/api/sources", () => ({ getSources: vi.fn() }));

const getSources = vi.mocked(sources.getSources);

function makeSource(id: string): sources.SourceItem {
	return {
		id,
		created_at: "2026-01-01T00:00:00Z",
		status: "ok",
		details: {
			sheet_type: null,
			files: [],
			processed: 0,
			skipped: 0,
			error: null,
		},
	};
}

interface WsMessage {
	type: string;
	payload: sources.SourceItem;
}

describe("useSources", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.stubGlobal(
			"fetch",
			vi
				.fn()
				.mockResolvedValue({ json: () => Promise.resolve({ token: "t1" }) }),
		);
	});

	it("carga sources al montar", async () => {
		getSources.mockResolvedValue({
			ok: true,
			data: { total: 1, items: [makeSource("s1")] },
		});

		const { result } = renderHook(() => useSources());

		await waitFor(() => expect(result.current.loading).toBe(false));
		expect(result.current.items).toHaveLength(1);
		expect(result.current.total).toBe(1);
	});

	it("prependea items y cuenta eventos cuando llega log_event por WS", async () => {
		getSources.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });

		const { result } = renderHook(() => useSources());
		await waitFor(() => expect(result.current.loading).toBe(false));

		const opts = useWebSocketMock.mock.calls[0][0] as {
			onMessage: (data: WsMessage) => void;
		};
		const newItem = makeSource("s2");

		act(() => {
			opts.onMessage({ type: "log_event", payload: newItem });
		});

		expect(result.current.items).toEqual([newItem]);
		expect(result.current.total).toBe(1);
		expect(result.current.wsEventCount).toBe(1);
	});

	it("ignora mensajes WS que no son log_event", async () => {
		getSources.mockResolvedValue({ ok: true, data: { total: 0, items: [] } });

		const { result } = renderHook(() => useSources());
		await waitFor(() => expect(result.current.loading).toBe(false));

		const opts = useWebSocketMock.mock.calls[0][0] as {
			onMessage: (data: WsMessage) => void;
		};

		act(() => {
			opts.onMessage({ type: "other", payload: makeSource("s3") });
		});

		expect(result.current.items).toEqual([]);
		expect(result.current.wsEventCount).toBe(0);
	});
});
