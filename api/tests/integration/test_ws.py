import asyncio
import json

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


def test_ws_broadcast():
    from app.routers.ws import manager

    user_id = generate_uuid()
    token = create_access_token(user_id, "director", "test@unq.edu.ar")
    client = TestClient(app)

    with client.websocket_connect(f"/ws?token={token}") as ws:
        asyncio.run(
            manager.broadcast(
                {
                    "type": "log_event",
                    "payload": {
                        "id": str(generate_uuid()),
                        "created_at": "2026-07-12T12:00:00+00:00",
                        "action": "import_guarani",
                        "status": "ok",
                        "details": {"sheet_type": "carreras", "processed": 5},
                    },
                }
            )
        )
        data = json.loads(ws.receive_text())
        assert data["type"] == "log_event"
        assert data["payload"]["status"] == "ok"
        assert data["payload"]["action"] == "import_guarani"
