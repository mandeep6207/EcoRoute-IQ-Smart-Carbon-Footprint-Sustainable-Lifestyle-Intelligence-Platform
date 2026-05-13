from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class AppConfig:
    secret_key: str = os.environ.get("SECRET_KEY", "ecoroute-iq-dev-secret")
    session_cookie_samesite: str = "Lax"
    session_cookie_secure: bool = False
    permanent_session_days: int = 7
    default_port: int = int(os.environ.get("PORT", 8000))
    flask_debug: bool = os.environ.get("FLASK_DEBUG", "0") == "1"


ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
