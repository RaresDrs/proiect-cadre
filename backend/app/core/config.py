from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",
        "https://*.vercel.app",    # Vercel deploy — actualizat in Faza 3
    ]
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "StructCalc API"


settings = Settings()
