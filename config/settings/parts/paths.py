from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

ENV_FILE = BASE_DIR / ".env"

STATIC_DIR = BASE_DIR / "static"
PUBLIC_DIR = BASE_DIR / "public"

__all__ = [
    "BASE_DIR",
    "ENV_FILE",
    "STATIC_DIR",
    "PUBLIC_DIR",
]