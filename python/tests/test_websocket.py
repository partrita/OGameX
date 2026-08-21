import pytest
from fastapi.testclient import TestClient
from python.app.main import app

def test_websocket_connection():
    client = TestClient(app)
    with client.websocket_connect("/ws/1") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connection_established"
        assert data["user_id"] == 1
        
        # Test ping/pong
        websocket.send_json({"action": "ping"})
        response = websocket.receive_json()
        assert response["type"] == "pong"
