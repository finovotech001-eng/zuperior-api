import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union, List
import json

# Project root (repo root) so that `.env` at repository root is discovered
# config.py is at app/core/config.py -> parents[2] points to repo root
BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "CRM API"
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ["*"]
    
    # SMTP Email Configuration
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = "Zuperior <noreply@zuperior.com>"
    SMTP_SECURE: bool = False
    CLIENT_URL: str = "https://dashboard.zuperior.com"
    EMAIL_LOGO_URL: str = ""

    def model_post_init(self, __context):
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            try:
                self.BACKEND_CORS_ORIGINS = json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                self.BACKEND_CORS_ORIGINS = (
                    ["*"] if self.BACKEND_CORS_ORIGINS == "*" else [self.BACKEND_CORS_ORIGINS]
                )

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),  # 👈 explicit full path
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
