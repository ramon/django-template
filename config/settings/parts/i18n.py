# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/
from django.utils.translation import gettext_lazy

from .env import env
from .paths import BASE_DIR

LANGUAGE_CODE = env.str("LANGUAGE_CODE", default="pt-BR")

# Idiomas que o `makemessages` gera por padrao (ver apps/core/management/commands).
LANGUAGES = [
    ("pt-br", gettext_lazy("Brazilian Portuguese")),
    ("en", gettext_lazy("English")),
]

# So os textos globais -- templates/ e config/. Os catalogos de cada app vivem em
# apps/<app>/locale/ e o Django os descobre sozinho, por app instalado.
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = env.str("TIME_ZONE", default="America/Sao_Paulo")
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

__all__ = [
    "LANGUAGES",
    "LANGUAGE_CODE",
    "LOCALE_PATHS",
    "TIME_ZONE",
    "USE_I18N",
    "USE_L10N",
    "USE_THOUSAND_SEPARATOR",
    "USE_TZ",
]
