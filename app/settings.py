# app/settings.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Основные настройки
    app_name: str = "SPAS System"
    app_version: str = "1.0.0"
    debug: bool = False

    # Настройки сервера
    host: str = "127.0.0.1"
    port: int = 8000

    # Настройки логирования
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False




settings = Settings()
