# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

from .env import env
from .paths import BASE_DIR, PUBLIC_DIR

STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = PUBLIC_DIR / "static"
STATICFILES_DIRS = [PUBLIC_DIR / "static"]

MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = PUBLIC_DIR / "media"

SERVESTATIC_ROOT = PUBLIC_DIR

__all__ = [
    "STATIC_URL",
    "STATIC_ROOT",
    "STATICFILES_DIRS",
    "MEDIA_URL",
    "MEDIA_ROOT",
    "SERVESTATIC_ROOT"
]
