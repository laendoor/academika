import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.add(ws)
        logger.info("ws connected: total=%d", len(self._connections))

    async def disconnect(self, ws: WebSocket) -> None:
        self._connections.discard(ws)
        logger.info("ws disconnected: total=%d", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        payload = json.dumps(message, default=str)
        stale: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(payload)
            except Exception:
                logger.warning("ws send failed — removing connection")
                stale.append(ws)
        for ws in stale:
            await self.disconnect(ws)


manager = WSManager()
