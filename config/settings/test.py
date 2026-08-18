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

# o storage de producao exige collectstatic para resolver {% static %}; nos testes
# (inclusive nos e2e, que sobem um live_server) serve o arquivo direto.
STORAGES = {
    **STORAGES,  # noqa: F405
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa
