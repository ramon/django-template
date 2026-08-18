import re

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from config.app_settings import get_integration_settings
from config.settings.parts.django import DEBUG

IGNORABLE_404_URLS = [
    re.compile(r"^/apple-touch-icon.*\.png$"),
    re.compile(r"^/favicon\.ico$"),
    re.compile(r"^/robots\.txt$"),
]


if not DEBUG:
    # integracoes de terceiros vivem em IntegrationSettings (pydantic-settings),
    # nao em django-environ: a variavel e' INTEGRATION_SENTRY_DSN.
    sentry_dsn = get_integration_settings().SENTRY_DSN

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn.get_secret_value(),
            integrations=[DjangoIntegration(), CeleryIntegration()],
            traces_sample_rate=0.1,
            profile_session_sample_rate=0.1,
            profile_lifecycle="trace",
            # ADR 0008: sem PII por padrao; cruzar erro com usuario e' via
            # correlation_id (X-Correlation-Id), nao pelo evento no Sentry.
            send_default_pii=False,
        )


__all__ = ["IGNORABLE_404_URLS"]
