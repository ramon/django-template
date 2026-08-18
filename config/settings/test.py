"""Test Django settings."""

from .base import *  # noqa: F403

DEBUG = False
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
# precisa espelhar os aliases de parts/cache.py: SESSION_CACHE_ALIAS aponta para "session"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "session": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa
