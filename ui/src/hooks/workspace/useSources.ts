"use client";
import { useCallback, useEffect, useState } from "react";

import { useWebSocket } from "@/hooks/useWebSocket";
import * as sources from "@/lib/api/sources";
import { WS_URL } from "@/lib/constants";

interface UseSourcesOptions {
	skip?: number;
	limit?: number;
}

interface WsMessage {
	type: string;
	payload: sources.SourceItem;
}

export function useSources({ skip = 0, limit = 20 }: UseSourcesOptions = {}) {
	const [items, setItems] = useState<sources.SourceItem[]>([]);
	const [total, setTotal] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | undefined>();
	const [wsEventCount, setWsEventCount] = useState(0);
	const [wsToken, setWsToken] = useState<string | null>(null);

	useEffect(() => {
		fetch("/api/auth/ws-token")
			.then((r) => r.json())
			.then((data) => setWsToken(data.token))
			.catch((err) => console.error("ws-token fetch failed:", err));
	}, []);

	useWebSocket<WsMessage>({
		url: wsToken ? `${WS_URL}?token=${wsToken}` : "",
		onMessage: (data) => {
			if (data.type !== "log_event") return;
			setItems((prev) => [data.payload, ...prev]);
			setTotal((prev) => prev + 1);
			setWsEventCount((prev) => prev + 1);
		},
	});

	const refresh = useCallback(async () => {
		setLoading(true);
		const result = await sources.getSources(skip, limit);
		if (result.ok) {
			setItems(result.data.items);
			setTotal(result.data.total);
			setError(undefined);
		} else {
			setError(result.error);
		}
		setLoading(false);
	}, [skip, limit]);

	useEffect(() => {
		refresh();
	}, [refresh]);

	return { items, total, loading, error, refresh, wsEventCount };
}
