import uuid
from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.auth.assertions import ensure_token_decoded
from app.auth.errors import InvalidTokenError
from app.observability.ws_manager import manager

router = APIRouter()


@router.websocket("")
async def ws_endpoint(websocket: WebSocket, token: Annotated[str, Query()]) -> None:
    try:
        payload = ensure_token_decoded(token, expected_type="access")
    except InvalidTokenError:
        await websocket.close(code=4001)
        return

    try:
        _user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        await websocket.close(code=4001)
        return

    await manager.connect(websocket)
    try:
        while True:
            _data = await websocket.receive_text()
            if websocket.client_state == WebSocketState.DISCONNECTED:
                break
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
