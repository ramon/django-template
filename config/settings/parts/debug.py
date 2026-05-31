from .django import SILENCED_SYSTEM_CHECKS, INSTALLED_APPS, MIDDLEWARE

SILENCED_SYSTEM_CHECKS.append("security.W006")
INTERNAL_IPS = ["127.0.0.1", "localhost"]
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
