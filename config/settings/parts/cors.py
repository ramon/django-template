from config.settings.parts.django import DEBUG
from config.settings.parts.env import env

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = []
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

__all__ = ["CORS_ALLOW_ALL_ORIGINS", "CORS_ALLOWED_ORIGINS"]
