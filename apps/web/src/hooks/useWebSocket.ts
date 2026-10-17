"use client";
import { useCallback, useEffect, useRef } from "react";

interface UseWebSocketOptions<T> {
	url: string;
	onMessage: (data: T) => void;
	onConnected?: () => void;
}

export function useWebSocket<T>({
	url,
	onMessage,
	onConnected,
}: UseWebSocketOptions<T>) {
	const wsRef = useRef<WebSocket | null>(null);
	const retriesRef = useRef(0);
	const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const onMessageRef = useRef(onMessage);
	onMessageRef.current = onMessage;
	const onConnectedRef = useRef(onConnected);
	onConnectedRef.current = onConnected;

	const connect = useCallback(() => {
		if (!url) return;
		if (wsRef.current?.readyState === WebSocket.OPEN) return;

		const ws = new WebSocket(url);
		wsRef.current = ws;

		ws.onopen = () => {
			retriesRef.current = 0;
			onConnectedRef.current?.();
		};

		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data) as T;
				onMessageRef.current(data);
			} catch {
				console.warn("ws: ignoring malformed message", event.data);
			}
		};

		ws.onclose = () => {
			wsRef.current = null;
			const delay = Math.min(1000 * 2 ** retriesRef.current, 30_000);
			retriesRef.current++;
			timerRef.current = setTimeout(connect, delay);
		};
	}, [url]);

	useEffect(() => {
		connect();
		return () => {
			if (timerRef.current) clearTimeout(timerRef.current);
			if (wsRef.current) wsRef.current.close();
		};
	}, [connect]);
}
