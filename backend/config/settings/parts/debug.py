from .django import INSTALLED_APPS, MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1", "localhost"]
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
