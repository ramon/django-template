from config.settings.parts.django import DEBUG, INSTALLED_APPS, MIDDLEWARE, SILENCED_SYSTEM_CHECKS

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# debug_toolbar vive apenas no grupo `dev` das dependencias: instalar o app fora de
# DEBUG quebra o boot em producao com ImportError.
if DEBUG:
    SILENCED_SYSTEM_CHECKS.append("debug_toolbar.W006")
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

__all__ = ["INTERNAL_IPS"]
