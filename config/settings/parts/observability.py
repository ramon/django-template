from config.settings.parts.django import INSTALLED_APPS, MIDDLEWARE
from config.settings.parts.env import env

ENABLE_PROMETHEUS: bool = env.bool("ENABLE_PROMETHEUS", default=False)

if ENABLE_PROMETHEUS:
    INSTALLED_APPS += [
        "django_prometheus",
    ]

    # django_prometheus precisa envolver toda a stack: Before no topo, After no fim.
    MIDDLEWARE.insert(0, "django_prometheus.middleware.PrometheusBeforeMiddleware")
    MIDDLEWARE.append("django_prometheus.middleware.PrometheusAfterMiddleware")

__all__ = ["ENABLE_PROMETHEUS"]
