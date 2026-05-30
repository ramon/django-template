from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

ENV_FILE = BASE_DIR.parent / ".env"

PUBLIC_DIR = BASE_DIR / "public"

__all__ = [
    "BASE_DIR",
    "ENV_FILE",
    "PUBLIC_DIR",
]