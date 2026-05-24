from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"

__all__ = [
    "BASE_DIR",
    "ENV_FILE",
]