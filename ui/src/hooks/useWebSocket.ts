"use client";
import { useCallback, useEffect, useRef, useState } from "react";

interface UseWebSocketOptions<T> {
	url: string;
	onMessage: (data: T) => void;
}

export function useWebSocket<T>({ url, onMessage }: UseWebSocketOptions<T>) {
	const [connected, setConnected] = useState(false);
	const wsRef = useRef<WebSocket | null>(null);
	const retriesRef = useRef(0);
	const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const onMessageRef = useRef(onMessage);
	onMessageRef.current = onMessage;

	const connect = useCallback(() => {
		if (!url) return;
		if (wsRef.current?.readyState === WebSocket.OPEN) return;

		const ws = new WebSocket(url);
		wsRef.current = ws;

		ws.onopen = () => {
			setConnected(true);
			retriesRef.current = 0;
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
			setConnected(false);
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

	return { connected };
}
