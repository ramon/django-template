# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
from parts.env import env

STATIC_URL = env("STATIC_URL", default="/static/")
MEDIA_URL = env("MEDIA_URL", default="/media/")