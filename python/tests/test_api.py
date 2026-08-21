import pytest
from httpx import AsyncClient, ASGITransport
from python.app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "OGameX FastAPI Engine"

@pytest.mark.asyncio
async def test_planet_overview():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/game/planet/1/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Homeworld"
    assert "resources" in data
    assert data["resources"]["metal"] > 0

@pytest.mark.asyncio
async def test_fleet_dispatch_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "origin_planet_id": 1,
            "target": {
                "galaxy": 1,
                "system": 105,
                "position": 8,
                "planet_type": 1
            },
            "ships": {
                "202": 10, # 10 Small Cargos
                "204": 5   # 5 Light Fighters
            },
            "speed_percent": 1.0
        }
        response = await ac.post("/api/v1/game/fleet/dispatch/check", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["distance"] > 0
    assert data["flight_time_seconds"] > 0
    assert data["fuel_consumption"] > 0
    assert data["cargo_capacity"] == (10 * 5000) + (5 * 50)
