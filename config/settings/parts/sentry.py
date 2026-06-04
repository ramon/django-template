import re

import sentry_sdk
from config.settings.parts.django import DEBUG
from config.settings.parts.env import env
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

IGNORABLE_404_URLS = [
    re.compile(r"^/apple-touch-icon.*\.png$"),
    re.compile(r"^/favicon\.ico$"),
    re.compile(r"^/robots\.txt$"),
]


if not DEBUG:
    sentry_dsn = env("SENTRY_DSN", default=None)

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                DjangoIntegration(),
                CeleryIntegration()
            ],
            traces_sample_rate=0.1,
            profile_session_sample_rate=0.1,
            profile_lifecycle="trace",
            send_default_pii=True,
        )



__all__ = ["IGNORABLE_404_URLS"]