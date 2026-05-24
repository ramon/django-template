# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/
from parts.env import env

LANGUAGE_CODE = env("LANGUAGE_CODE", default="pt-BR")
TIME_ZONE = env("TIME_ZONE", default="America/Sao_Paulo")
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True