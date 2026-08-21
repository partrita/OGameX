from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from python.app.core.config import settings
from python.app.routers import game, websocket

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance async Python backend for OGameX",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(game.router, prefix="/api/v1/game", tags=["Game Engine"])
app.include_router(websocket.router, tags=["WebSockets"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "OGameX FastAPI Engine",
        "economy_speed": settings.ECONOMY_SPEED,
        "fleet_speed": settings.FLEET_SPEED,
    }
