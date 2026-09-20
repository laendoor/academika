import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useWebSocket } from "@/hooks/useWebSocket";

class FakeWebSocket {
	static OPEN = 1;
	static instances: FakeWebSocket[] = [];
	url: string;
	readyState = 0;
	onopen: (() => void) | null = null;
	onmessage: ((event: { data: string }) => void) | null = null;
	onclose: (() => void) | null = null;
	close = vi.fn();

	constructor(url: string) {
		this.url = url;
		FakeWebSocket.instances.push(this);
	}
}

describe("useWebSocket", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		FakeWebSocket.instances = [];
		vi.stubGlobal("WebSocket", FakeWebSocket);
	});

	it("abre conexión cuando hay url y llama onConnected", () => {
		const onConnected = vi.fn();
		renderHook(() =>
			useWebSocket({ url: "ws://x", onMessage: vi.fn(), onConnected }),
		);

		const ws = FakeWebSocket.instances[0];
		expect(ws).toBeDefined();
		ws.onopen?.();
		expect(onConnected).toHaveBeenCalledTimes(1);
	});

	it("no abre conexión sin url", () => {
		renderHook(() => useWebSocket({ url: "", onMessage: vi.fn() }));
		expect(FakeWebSocket.instances).toHaveLength(0);
	});

	it("parsea mensajes válidos y descarta malformados", () => {
		const onMessage = vi.fn();
		const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
		renderHook(() => useWebSocket({ url: "ws://x", onMessage }));

		const ws = FakeWebSocket.instances[0];
		ws.onmessage?.({ data: JSON.stringify({ type: "log_event", payload: 1 }) });
		expect(onMessage).toHaveBeenCalledWith({ type: "log_event", payload: 1 });

		ws.onmessage?.({ data: "not json" });
		expect(onMessage).toHaveBeenCalledTimes(1);
		expect(warn).toHaveBeenCalled();
		warn.mockRestore();
	});

	it("cierra el socket al desmontar", () => {
		const { unmount } = renderHook(() =>
			useWebSocket({ url: "ws://x", onMessage: vi.fn() }),
		);
		const ws = FakeWebSocket.instances[0];
		unmount();
		expect(ws.close).toHaveBeenCalled();
	});

	it("reconecta con backoff al cerrarse", () => {
		vi.useFakeTimers();
		const { unmount } = renderHook(() =>
			useWebSocket({ url: "ws://x", onMessage: vi.fn() }),
		);
		const ws = FakeWebSocket.instances[0];
		ws.onclose?.();
		expect(FakeWebSocket.instances).toHaveLength(1);

		vi.advanceTimersByTime(1000);
		expect(FakeWebSocket.instances).toHaveLength(2);

		unmount();
		vi.useRealTimers();
	});
});
