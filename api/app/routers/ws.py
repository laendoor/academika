import uuid
from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth.assertions import ensure_token_decoded
from app.auth.errors import InvalidTokenError
from app.observability.ws_manager import WSManager

router = APIRouter()
manager = WSManager()


@router.websocket("")
async def ws_endpoint(websocket: WebSocket, token: Annotated[str, Query()]) -> None:
    try:
        payload = ensure_token_decoded(token, expected_type="access")
    except InvalidTokenError:
        await websocket.close(code=4001)
        return

    user_id = uuid.UUID(payload["sub"])
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
