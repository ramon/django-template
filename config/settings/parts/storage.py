from config.settings.parts.env import env
from config.settings.parts.paths import PUBLIC_DIR, STATIC_DIR

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "servestatic.storage.CompressedManifestStaticFilesStorage",
    },
}

STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = PUBLIC_DIR / "static"
STATICFILES_DIRS = [STATIC_DIR]

MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = PUBLIC_DIR / "media"

SERVESTATIC_ROOT = PUBLIC_DIR

__all__ = [
    "STORAGES",
    "STATIC_URL",
    "STATIC_ROOT",
    "STATICFILES_DIRS",
    "MEDIA_URL",
    "MEDIA_ROOT",
    "SERVESTATIC_ROOT"
]