from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "OGameX Python Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "ogamex"
    DB_PASSWORD: str = "ogamex"
    DB_NAME: str = "ogamex"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        
    # Game Speed / Config
    ECONOMY_SPEED: int = 1
    FLEET_SPEED: int = 1
    
    # Secret / Auth
    SECRET_KEY: str = "ogamex-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
