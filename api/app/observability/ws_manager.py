import json
import logging
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSManager:
    def __init__(self) -> None:
        self._connections: dict[UUID, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, user_id: UUID) -> None:
        await ws.accept()
        self._connections.setdefault(user_id, []).append(ws)
        logger.info("ws connected: user=%s total=%d", user_id, len(self._connections))

    async def disconnect(self, ws: WebSocket, user_id: UUID) -> None:
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self._connections.pop(user_id, None)
        logger.info("ws disconnected: user=%s total=%d", user_id, len(self._connections))

    async def broadcast(self, message: dict) -> None:
        payload = json.dumps(message, default=str)
        stale: list[tuple[WebSocket, UUID]] = []
        for user_id, conns in self._connections.items():
            for ws in conns:
                try:
                    await ws.send_text(payload)
                except Exception:
                    logger.warning("ws send failed: user=%s — removing", user_id)
                    stale.append((ws, user_id))
        for ws, uid in stale:
            await self.disconnect(ws, uid)
