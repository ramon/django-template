"""Test Django settings."""

import tempfile
from pathlib import Path

from .base import *  # noqa: F403

DEBUG = False

# parts/security.py liga o redirect de HTTPS fora de DEBUG, olhando a variavel de
# ambiente. Em teste isso transforma toda request em 301 e quebra qualquer teste
# que faca HTTP de verdade (o test client e os e2e).
SECURE_SSL_REDIRECT = False

# parts/debug.py instala o toolbar olhando a variavel de ambiente DEBUG, entao a
# suite herdaria o .env de cada maquina: com DEBUG=True local e False no CI, os
# mesmos testes rodam com middlewares diferentes. Em teste o toolbar nunca entra.
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith("debug_toolbar")]  # noqa: F405

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

# o health check de storage grava e apaga um arquivo a cada sonda; sem isto os
# testes sujariam public/media/ no repositorio.
MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="django-template-media-"))

# o storage de producao exige collectstatic para resolver {% static %}; nos testes
# (inclusive nos e2e, que sobem um live_server) serve o arquivo direto.
STORAGES = {
    **STORAGES,  # noqa: F405
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa
