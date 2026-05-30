# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

from .env import env
from .paths import BASE_DIR

STATIC_URL = env("STATIC_URL", default="/static/")
MEDIA_URL = env("MEDIA_URL", default="/media/")

STATIS_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
