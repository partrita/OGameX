import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from python.app.schemas.enums import Coordinate

router = APIRouter()

class ConnectionManager:
    """Manages active WebSocket connections for real-time game events."""
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {} # user_id -> sockets

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in list(self.active_connections[user_id]):
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    self.disconnect(user_id, connection)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint providing real-time game updates (resource ticks, fleet alerts, chat).
    """
    await manager.connect(user_id, websocket)
    try:
        # Initial greeting & sync
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "user_id": user_id,
            "message": "Connected to OGameX Real-time Engine"
        }))
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Handle client actions (ping, chat message, active planet switch)
                if msg.get("action") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
