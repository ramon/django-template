# A ordem dos imports abaixo e' semantica: cada part muta INSTALLED_APPS/MIDDLEWARE
# em sequencia, entao o isort nao pode reordenar este arquivo.
# ruff: noqa: I001, F403
from .parts.paths import *
from .parts.django import *
from .parts.security import *
from .parts.cors import *
from .parts.auth import *
from .parts.i18n import *
from .parts.database import *
from .parts.cache import *
from .parts.session import *
from .parts.storage import *
from .parts.logging import *
from .parts.templates import *
from .parts.cotton import *
from .parts.email import *
from .parts.celery import *
from .parts.sentry import *
from .parts.debug import *
from .parts.third_party import *
from .parts.project import *

# observability por ultimo: PrometheusBefore/After precisam envolver toda a stack.
from .parts.observability import *
