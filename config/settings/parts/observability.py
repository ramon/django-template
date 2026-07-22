from config.settings.parts.django import INSTALLED_APPS, MIDDLEWARE
from config.settings.parts.env import env

ENABLE_PROMETHEUS: bool = env.bool("ENABLE_PROMETHEUS", default=False)

if ENABLE_PROMETHEUS:
    INSTALLED_APPS += [
        "django_prometheus",
    ]

    MIDDLEWARE += [
        "django_prometheus.middleware.PrometheusBeforeMiddleware",
        MIDDLEWARE,
        "django_prometheus.middleware.PrometheusAfterMiddleware",
    ]