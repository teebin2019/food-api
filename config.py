from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ──────────────── App ────────────────
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"

    # ──────────────── Database ────────────────
    DATABASE_URL: str = "sqlite:///./food.db"

    # ──────────────── Upload ────────────────
    UPLOAD_DIR: str = "uploads"
    CHUNK_SIZE: int = 1024 * 1024          # 1 MB per chunk
    MAX_FILES_PER_REQUEST: int = 10
    ALLOWED_CONTENT_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "application/pdf",
    ]

    # ──────────────── CORS ────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()