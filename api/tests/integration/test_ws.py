import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.auth.tokens import create_access_token
from app.db.base import generate_uuid
from app.main import app


def test_ws_accepts_valid_token():
    user_id = generate_uuid()
    token = create_access_token(user_id, "director", "test@unq.edu.ar")
    client = TestClient(app)
    with client.websocket_connect(f"/ws?token={token}") as ws:
        ws.send_text("ping")


def test_ws_rejects_invalid_token():
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?token=not-a-real-token") as ws:
            ws.receive_text()
